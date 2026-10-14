"""Compact single-page version of the main BPMN diagram (same required elements, ~35 % narrower)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402  (patches Diagram.port for absolute points)
from bpmnlib import Diagram  # noqa: E402


def compact_main():
    W, H = 2000, 1160
    d = Diagram("registration_compact", W, H)
    TW, TH = 104, 70                      # task size
    R1, R2 = 90, 178                      # user pool rows
    UP, LO = 350, 480                     # UI lane rows (upper = errors, lower = main flow)
    AU = 650                              # auth lane row
    DS = 820                              # data lane row
    SM = 985                              # sms pool row
    DBT = 1085                            # top of DB pool

    pw = W - 30
    d.pool("P_user", "Пользователь", 15, 20, pw, 230)
    d.pool("P_web", "Веб-система Аэрофлот", 15, 270, pw, 610,
           lanes=[("L_ui", "UI/UX (Frontend)", 270, 290), ("L_auth", "AuthService (Backend)", 560, 200), ("L_ds", "DataStore", 760, 120)])
    d.pool("P_sms", "SMS-шлюз", 15, 925, pw, 120)
    d.pool("P_db", "База данных (пользователи, коды, согласия)", 15, 1085, pw, 50, black=True)

    # x positions (centres)
    xs = dict(W_s=130, T_open=222, T_focus=348, M2=445, T_blur=542, G1=639, G2=707, T_unb=804, E_c=896, G3=959,
              T_fmt=1056, J=1153, G4=1221, T_gen=1318, T_sms=1444, M4=1541, T_check=1638, G5=1735, G6=1803, END=1866,
              M1=736, T_block=833, M3=1540)
    x = xs

    UI = dict(pool="P_web", lane="L_ui")
    AUTH = dict(pool="P_web", lane="L_auth")
    DSL = dict(pool="P_web", lane="L_ds")

    # ----------------------------------------------------------- User pool
    d.ev("U_s", x["W_s"], R1, "Открыта страница регистрации", "start", pool="P_user", lw=16)
    d.task("U_input", x["T_blur"], R1, "Ввод данных (с Tab-навигацией)", "user", "P_user", w=TW, h=TH)
    d.task("U_submit", x["E_c"], R1, "Нажать «Отправить»", "user", "P_user", w=TW, h=TH)
    d.gw("M3", x["M3"], R1, "", "xor", pool="P_user")
    d.task("U_wait", x["T_check"], R1, "Ожидание ввода кода", "user", "P_user", w=TW, h=TH)
    d.boundary("BE1", "U_wait", "B", -30, "timer", "Таймаут кода", lab="L", lw=10, lx=-4, ly=14)
    d.task("U_new", x["T_gen"], R2, "Запросить новый код", "user", "P_user", w=TW, h=TH)
    d.ev("U_end", x["END"], R1, "Процесс завершён", "end", pool="P_user", lw=14)

    # -------------------------------------------------------------- UI lane
    d.ev("W_s", x["W_s"], LO, "Страница запрошена", "start", lab="B", lw=12, **UI)
    d.task("T_open", x["T_open"], LO, "Открыть форму регистрации (десктоп)", "task", w=TW, h=TH, **UI)
    d.task("T_focus", x["T_focus"], LO, "Автофокус на первом поле", "task", w=TW, h=TH, **UI)
    d.gw("M2", x["M2"], LO, "", "xor", **UI)
    d.task("T_blur", x["T_blur"], LO, "Валидация поля при потере фокуса (on blur)", "task", w=TW, h=TH, **UI)
    d.gw("G1", x["G1"], LO, "Поле валидно?", "xor", lab="B", lw=12, **UI)
    d.gw("G2", x["G2"], LO, "Все поля валидны?", "xor", lab="B", lw=12, **UI)
    d.task("T_err", x["G1"], UP, "Показать сообщение об ошибке под полем", "task", w=TW, h=TH, **UI)
    d.gw("M1", x["M1"], UP, "", "xor", **UI)
    d.task("T_block", x["T_block"], UP, "Блокировать кнопку «Отправить» при ошибках", "task", w=TW, h=TH, **UI)
    d.task("T_unb", x["T_unb"], LO, "Разблокировать кнопку «Отправить»", "task", w=TW, h=TH, **UI)
    d.ev("E_c", x["E_c"], LO, "Нажата «Отправить»", "catch", "message", lab="B", lw=11, **UI)
    d.gw("G3", x["G3"], LO, "", "and", **UI)
    d.task("T_fmt", x["T_fmt"], LO, "Проверить формат email", "task", w=TW, h=TH, **UI)
    d.task("T_dup", x["G4"], UP, "Показать под полем: email уже занят (409)", "task", w=TW, h=TH, **UI)
    d.task("T_msgErr", x["T_sms"], LO, "Показать понятное сообщение, предложить повторить позже", "task", w=TW + 8, h=TH + 6, **UI)
    d.ev("E_err1", x["T_sms"], UP, "Финальное сообщение об ошибке (шлюз недоступен)", "end", "error", lab="T", lw=18, **UI)
    d.task("T_retry", x["G6"], LO, "Сообщить о неверном коде (повторный ввод)", "task", w=TW + 8, h=TH + 6, **UI)
    d.data("DO_form", 200, 362, "Форма регистрации", lab="T", lw=12, **UI)
    d.data("DO_cons", 272, 362, "Документ согласия", lab="T", lw=12, **UI)

    # ------------------------------------------------------------ Auth lane
    d.task("T_uniq", x["T_fmt"], AU, "Проверить уникальность email на бэкенде", "service", w=TW, h=TH, **AUTH)
    d.gw("J", x["J"], AU, "", "and", **AUTH)
    d.gw("G4", x["G4"], AU, "Email уникален?", "xor", lab="B", lw=12, **AUTH)
    d.task("T_gen", x["T_gen"], AU, "Сгенерировать код подтверждения", "service", w=TW, h=TH, **AUTH)
    d.data("DO_code", x["T_gen"], AU + 62, "Код подтверждения", lab="B", lw=18, **AUTH)
    d.task("T_sms", x["T_sms"], AU, "Отправить SMS через шлюз", "send", w=TW, h=TH, **AUTH)
    d.boundary("BE2", "T_sms", "T", 0, "error", "SMS-шлюз недоступен", lab="R", lw=10, ly=-44)
    d.gw("M4", x["M4"], AU, "", "xor", **AUTH)
    d.task("T_check", x["T_check"], AU, "Проверить код подтверждения", "service", w=TW, h=TH, **AUTH)
    d.gw("G5", x["G5"], AU, "Код подтверждения верный?", "xor", lab="T", lw=13, **AUTH)
    d.gw("G6", x["G6"], AU, "Лимит попыток исчерпан?", "xor", lab="B", lw=13, **AUTH)
    d.ev("E_err2", x["END"] + 10, AU, "Финальное сообщение об ошибке (лимит попыток)", "end", "error", lab="T", lw=14, **AUTH)

    # ------------------------------------------------------------ Data lane
    d.task("T_save", x["G5"], DS, "Сохранить пользователя в БД", "service", w=TW, h=TH, **DSL)
    d.ev("E_ok", x["G5"] + 98, DS, "Успешный вход в ЛК", "end", lab="B", lw=14, **DSL)
    d.data("DO_user", x["G5"] - 100, DS, "Объект пользователя", lab="B", lw=11, **DSL)

    # ------------------------------------------------------------- SMS pool
    SMSP = dict(pool="P_sms")
    d.ev("S_s", x["T_sms"], SM, "Запрос на отправку SMS", "start", "message", lab="B", lw=14, **SMSP)
    d.task("S_task", 1560, SM, "Доставить SMS на номер пользователя", "send", w=TW, h=TH, **SMSP)
    d.ev("S_end", 1672, SM, "SMS с кодом отправлен", "end", "message", lab="B", lw=14, **SMSP)

    # ------------------------------------------------------------ sequence
    s = lambda i, a, b, sp="R", tp="L", **k: d.flow(i, "seq", a, b, sp, tp, **k)  # noqa: E731
    s("s01", "U_s", "U_input"); s("s02", "U_input", "U_submit"); s("s03", "U_submit", "M3"); s("s03b", "M3", "U_wait"); s("s04", "U_wait", "U_end")
    s("s05", "BE1", "U_new", "B", "R+15")
    s("s06", "U_new", "M3", "R-15", "B")
    s("s10", "W_s", "T_open"); s("s11", "T_open", "T_focus"); s("s12", "T_focus", "M2"); s("s12b", "M2", "T_blur"); s("s13", "T_blur", "G1")
    s("s14", "G1", "T_err", "T", "B", label="нет", lx=x["G1"] + 8, ly=LO - 38, anchor="start", ln=6)
    s("s15", "T_err", "M1"); s("s15b", "M1", "T_block")
    s("s16", "G1", "G2", label="да", lx=x["G1"] + 28, ly=LO - 6, anchor="start", ln=6)
    s("s17", "G2", "M1", "T", "B", label="нет", lx=x["G2"] + 8, ly=LO - 38, anchor="start", ln=6)
    s("s18", "T_block", "M2", "T", "T", via=[(x["T_block"], 285), (x["M2"], 285)])
    s("s19", "G2", "T_unb", label="да", lx=x["G2"] + 28, ly=LO - 6, anchor="start", ln=6)
    s("s20", "T_unb", "E_c"); s("s21", "E_c", "G3"); s("s22", "G3", "T_fmt")
    s("s23", "G3", "T_uniq", "B", "L")
    s("s24", "T_fmt", "J", "R", "T")
    s("s25", "T_uniq", "J"); s("s26", "J", "G4")
    s("s27", "G4", "T_dup", "T", "B", label="нет", lx=x["G4"] + 8, ly=AU - 38, anchor="start", ln=6)
    s("s28", "T_dup", "M1", "T", "T", via=[(x["G4"], 300), (x["M1"], 300)])
    s("s29", "G4", "T_gen", label="да", lx=x["G4"] + 28, ly=AU - 6, anchor="start", ln=6)
    s("s30", "T_gen", "T_sms"); s("s31", "T_sms", "M4"); s("s31b", "M4", "T_check")
    s("s32", "BE2", "T_msgErr", "T", "B"); s("s33", "T_msgErr", "E_err1", "T", "B")
    s("s34", "T_check", "G5")
    s("s35", "G5", "T_save", "B", "T", label="да", lx=x["G5"] + 8, ly=AU + 44, anchor="start", ln=6)
    s("s36", "G5", "G6", label="нет", lx=x["G5"] + 28, ly=AU - 6, anchor="start", ln=6)
    s("s37", "G6", "T_retry", "T", "B", label="нет", lx=x["G6"] + 8, ly=AU - 38, anchor="start", ln=6)
    s("s38", "T_retry", "M4", "L", "T")
    s("s39", "G6", "E_err2", label="да", lx=x["G6"] + 28, ly=AU - 6, anchor="start", ln=6)
    s("s40", "T_save", "E_ok")
    s("s50", "S_s", "S_task"); s("s51", "S_task", "S_end")

    # ------------------------------------------------------------- messages
    m = lambda i, a, b, sp, tp, **k: d.flow(i, "msg", a, b, sp, tp, **k)  # noqa: E731
    m("m02", "T_focus", "U_input", "T+30", "B-25", via=[(x["T_focus"] + 30, 250), (x["T_blur"] - 25, 250)])
    m("m03", "U_input", "T_blur", "B+35", "T+35")
    m("m04", "T_err", "U_input", "T", "B+5", via=[(x["G1"], 250), (x["T_blur"] + 5, 250)])
    m("m05", "T_unb", "U_submit", "T+40", "B-28", via=[(x["T_unb"] + 40, 250), (x["E_c"] - 28, 250)])
    m("m06", "U_submit", "E_c", "B+25", "T", via=[(x["E_c"] + 25, 250), (x["E_c"], 250)])
    m("m10", "T_uniq", "P_db", "B-20", ("abs", x["T_fmt"] - 20, DBT), label="Есть ли такой email?", lx=x["T_fmt"] - 24, ly=1070, anchor="end", ln=24)
    m("m11", "P_db", "T_uniq", ("abs", x["T_fmt"] + 20, DBT), "B+20", label="Ответ БД", lx=x["T_fmt"] + 24, ly=1070, anchor="start", ln=24)
    m("m12", "T_sms", "S_s", "B", "T")
    m("m13", "S_end", "U_wait", "R", "T+25", via=[(1960, SM), (1960, 38), (x["T_check"] + 25, 38)], label="SMS с кодом", lx=1956, ly=SM - 18, anchor="end", ln=14)
    m("m14", "U_new", "T_gen", "B", "T")
    m("m15", "U_wait", "T_check", "B+5", "T+5", label="Введённый код", lx=x["T_check"] + 9, ly=330, anchor="start", ln=14)
    m("m16", "T_retry", "U_wait", "T", "B+40", via=[(x["G6"], 250), (x["T_check"] + 40, 250)])
    m("m17", "T_save", "P_db", "B-20", ("abs", x["G5"] - 20, DBT))
    m("m18", "P_db", "T_save", ("abs", x["G5"] + 10, DBT), "B+10")

    # --------------------------------------------------------- data objects
    a = lambda i, p, q, sp, tp, **k: d.flow(i, "assoc", p, q, sp, tp, **k)  # noqa: E731
    a("a01", "T_open", "DO_form", "T-30", "B")
    a("a02", "DO_cons", "T_open", "B", "T+40")
    a("a04", "T_gen", "DO_code", "B", "T")
    a("a05", "DO_code", "T_check", "R", "B")
    a("a06", "DO_user", "T_save", "R", "L")
    return d


if __name__ == "__main__":
    build.save(compact_main(), "registration_compact")
    print("ok")
