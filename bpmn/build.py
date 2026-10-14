"""Builds the three BPMN diagrams for the Aeroflot Bonus desktop registration assignment.

Outputs (next to this file): <name>.bpmn, <name>.svg  (PNG is rendered separately with headless Chromium).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from bpmnlib import Diagram  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# patch: allow absolute points ("abs", x, y) as ports
# ---------------------------------------------------------------------------
_orig_port = Diagram.port


def _port(self, ref, spec):
    if isinstance(spec, tuple):
        return (spec[1], spec[2])
    return _orig_port(self, ref, spec)


Diagram.port = _port


def save(d, name):
    with open(os.path.join(OUT, name + ".bpmn"), "w", encoding="utf-8") as f:
        f.write(d.bpmn())
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(d.svg())


# ===========================================================================
# 1. MAIN COLLABORATION DIAGRAM
# ===========================================================================
def main_diagram():
    W, H = 2870, 1400
    d = Diagram("registration", W, H)
    X = lambda c: 125 + 140 * c  # noqa: E731

    # rows
    R1, R2 = 95, 190                  # user pool rows
    UP, LO, BO = 380, 520, 660        # UI lane rows (upper / lower / bottom)
    AU = 825                          # auth lane row
    DS = 1030                         # data lane row
    SM = 1210                         # sms pool row
    DBT = 1320                        # top of DB pool

    pw = W - 30
    d.pool("P_user", "Пользователь", 15, 20, pw, 230)
    d.pool("P_web", "Веб-система Аэрофлот", 15, 290, pw, 810,
           lanes=[("L_ui", "UI/UX (Frontend)", 290, 440), ("L_auth", "AuthService (Backend)", 730, 230), ("L_ds", "DataStore", 960, 140)])
    d.pool("P_sms", "SMS-шлюз", 15, 1140, pw, 140)
    d.pool("P_db", "База данных (пользователи, коды, согласия)", 15, 1320, pw, 50, black=True)

    # ------------------------------------------------------------- User pool
    d.ev("U_s", X(0), R1, "Открыта страница регистрации (десктоп)", "start", pool="P_user", lw=17)
    d.task("U_nav", X(1), R1, "Перейти на страницу регистрации", "send", "P_user")
    d.task("U_input", X(4), R1, "Ввод данных пользователем (с Tab-навигацией)", "user", "P_user")
    d.task("U_submit", X(7), R1, "Нажать «Отправить»", "user", "P_user")
    d.task("U_wait", X(15), R1, "Ожидание ввода кода (код из SMS)", "user", "P_user")
    d.boundary("BE1", "U_wait", "B", -30, "timer", "Таймаут кода: срок действия истёк", lab="L", lw=10, lx=-6, ly=20)
    d.task("U_newcode", X(13), R2, "Нажать «Запросить новый код»", "user", "P_user")
    d.ev("U_end", X(16), R1, "Процесс регистрации завершён", "end", pool="P_user", lw=16)

    # --------------------------------------------------------------- UI lane
    UI = dict(pool="P_web", lane="L_ui")
    d.ev("W_s", X(1), LO, "Запрос страницы регистрации", "start", "message", lab="B", lw=14, **UI)
    d.task("T_open", X(2), LO, "Открыть форму регистрации (десктоп)", "task", **UI)
    d.task("T_focus", X(3), LO, "Автофокус на первом поле", "task", **UI)
    d.task("T_blur", X(4), LO, "Валидация поля при потере фокуса (on blur)", "task", **UI)
    d.boundary("BE3", "T_blur", "B", -35, "message", "Назад / закрытие вкладки", lab="R", lw=12, ly=14)
    d.task("T_clean", X(4) - 35, BO, "Очистить локальные данные формы, закрыть страницу", "task", **UI)
    d.ev("E_cancel", X(5) + 25, BO, "Регистрация отменена", "end", lab="B", lw=14, **UI)
    d.gw("G1", X(5), LO, "Поле валидно?", "xor", lab="B", lw=14, **UI)
    d.task("T_err", X(5), UP, "Показать сообщение об ошибке под полем", "task", **UI)
    d.task("T_block", X(6), UP, "Блокировать кнопку «Отправить» при ошибках", "task", **UI)
    d.gw("G2", X(6), LO, "Все поля валидны?", "xor", lab="B", lw=14, **UI)
    d.task("T_upd", X(7), LO, "Разблокировать кнопку «Отправить»", "task", **UI)
    d.task("T_send", X(8), LO, "Отправить форму на проверку", "task", **UI)
    d.gw("G3", X(9), LO, "", "and", **UI)
    d.task("T_fmt", X(10), LO, "Проверить формат email", "task", **UI)
    d.task("T_dup", X(12), UP, "Показать под полем: email уже занят (HTTP 409)", "task", **UI)
    d.task("T_msgErr", X(14), LO, "Показать понятное сообщение, предложить повторить позже", "task", **UI)
    d.ev("E_err1", X(14), UP, "Финальное сообщение об ошибке (шлюз недоступен)", "end", "error", lab="T", lw=18, **UI)
    d.task("T_retry", X(17), LO, "Сообщить о неверном коде (повторный ввод)", "task", **UI)
    d.task("T_limit", X(18), LO, "Показать финальное сообщение об ошибке", "task", **UI)
    d.ev("E_err2", X(18), UP, "Финальное сообщение об ошибке (лимит попыток)", "end", "error", lab="T", lw=18, **UI)
    d.data("DO_form", X(2) - 42, UP, "Форма регистрации (десктоп)", lab="L", lw=14, **UI)
    d.data("DO_cons", X(2) + 42, UP, "Документ согласия", lab="R", lw=12, **UI)
    d.data("DO_user", X(9) - 5, UP - 52, "Объект пользователя", lab="R", lw=11, **UI)

    # ------------------------------------------------------------- Auth lane
    AUTH = dict(pool="P_web", lane="L_auth")
    d.task("T_uniq", X(10), AU, "Проверить уникальность email на бэкенде", "service", **AUTH)
    d.gw("J", X(11), AU, "", "and", **AUTH)
    d.gw("G4", X(12), AU, "Email уникален?", "xor", lab="B", lw=14, **AUTH)
    d.task("T_gen", X(13), AU, "Сгенерировать код подтверждения", "service", **AUTH)
    d.data("DO_code", X(13), AU + 78, "Код подтверждения", lab="B", lw=16, **AUTH)
    d.task("T_sms", X(14), AU, "Отправить SMS через шлюз", "send", **AUTH)
    d.boundary("BE2", "T_sms", "T", 0, "error", "SMS-шлюз недоступен", lab="R", lw=10, ly=-44)
    d.task("T_check", X(15), AU, "Проверить код подтверждения", "service", **AUTH)
    d.gw("G5", X(16), AU, "Код подтверждения верный?", "xor", lab="T", lw=14, **AUTH)
    d.gw("G6", X(17), AU, "Лимит попыток исчерпан?", "xor", lab="B", lw=14, **AUTH)

    # ------------------------------------------------------------- Data lane
    DSL = dict(pool="P_web", lane="L_ds")
    d.task("T_save", X(16), DS, "Сохранить пользователя в БД", "service", **DSL)
    d.ev("E_ok", X(17), DS, "Успешный вход в ЛК", "end", lab="B", lw=14, **DSL)
    d.data("DO_u2", X(15) + 20, DS, "Объект пользователя", lab="B", lw=11, **DSL)
    d.data("DO_c2", X(15) - 55, DS, "Документ согласия", lab="B", lw=11, **DSL)

    # ---------------------------------------------------------------- SMS pool
    SMSP = dict(pool="P_sms")
    d.ev("S_s", X(14), SM, "Запрос на отправку SMS", "start", "message", lab="B", lw=14, **SMSP)
    d.task("S_task", X(15), SM, "Доставить SMS на номер пользователя", "send", **SMSP)
    d.ev("S_end", X(16) + 60, SM, "SMS с кодом отправлен", "end", "message", lab="B", lw=14, **SMSP)

    # ------------------------------------------------------- sequence flows
    s = lambda i, a, b, sp="R", tp="L", **k: d.flow(i, "seq", a, b, sp, tp, **k)  # noqa: E731
    s("s01", "U_s", "U_nav"); s("s02", "U_nav", "U_input"); s("s03", "U_input", "U_submit")
    s("s04", "U_submit", "U_wait"); s("s05", "U_wait", "U_end")
    s("s06", "BE1", "U_newcode", "B", "R+15")
    s("s07", "U_newcode", "U_wait", "R-15", "L")
    s("s10", "W_s", "T_open"); s("s11", "T_open", "T_focus"); s("s12", "T_focus", "T_blur"); s("s13", "T_blur", "G1")
    s("s14", "G1", "T_err", "T", "B", label="нет", lx=X(5) + 8, ly=LO - 38, anchor="start", ln=6)
    s("s15", "T_err", "T_block")
    s("s16", "G1", "G2", label="да", lx=X(5) + 36, ly=LO - 6, anchor="start", ln=6)
    s("s17", "G2", "T_block", "T", "B", label="нет", lx=X(6) + 8, ly=LO - 38, anchor="start", ln=6)
    s("s18", "T_block", "T_blur", "T", "T-20", via=[(X(6), UP - 58), (X(4) - 20, UP - 58)])
    s("s19", "G2", "T_upd", label="да", lx=X(6) + 36, ly=LO - 6, anchor="start", ln=6)
    s("s20", "T_upd", "T_send"); s("s21", "T_send", "G3"); s("s22", "G3", "T_fmt")
    s("s23", "G3", "T_uniq", "B", "L")
    s("s24", "T_fmt", "J", "R", "T")
    s("s25", "T_uniq", "J"); s("s26", "J", "G4")
    s("s27", "G4", "T_dup", "T", "B", label="нет", lx=X(12) + 8, ly=AU - 38, anchor="start", ln=6)
    s("s28", "T_dup", "T_block", "L", "R")
    s("s29", "G4", "T_gen", label="да", lx=X(12) + 34, ly=AU - 6, anchor="start", ln=6)
    s("s30", "T_gen", "T_sms"); s("s31", "T_sms", "T_check")
    s("s32", "BE2", "T_msgErr", "T", "B")
    s("s33", "T_msgErr", "E_err1", "T", "B")
    s("s34", "T_check", "G5")
    s("s35", "G5", "T_save", "B", "T", label="да", lx=X(16) + 8, ly=AU + 46, anchor="start", ln=6)
    s("s36", "G5", "G6", label="нет", lx=X(16) + 30, ly=AU - 6, anchor="start", ln=6)
    s("s37", "G6", "T_retry", "T", "B", label="нет", lx=X(17) + 8, ly=AU - 38, anchor="start", ln=6)
    s("s38", "T_retry", "T_check", "L", "T+30")
    s("s39", "G6", "T_limit", "R", "B", label="да", lx=X(17) + 30, ly=AU - 6, anchor="start", ln=6)
    s("s40", "T_limit", "E_err2", "T", "B")
    s("s41", "T_save", "E_ok")
    s("s42", "BE3", "T_clean", "B", "T"); s("s43", "T_clean", "E_cancel")
    s("s50", "S_s", "S_task"); s("s51", "S_task", "S_end")

    # --------------------------------------------------------- message flows
    m = lambda i, a, b, sp, tp, **k: d.flow(i, "msg", a, b, sp, tp, **k)  # noqa: E731
    m("m01", "U_nav", "W_s", "B", "T", label="Запрос страницы регистрации", lx=X(1) + 6, ly=330, anchor="start", ln=15)
    m("m02", "T_focus", "U_input", "T+30", "B-25", via=[(X(3) + 30, 268), (X(4) - 25, 268)], label="Форма показана, автофокус", lx=X(3) + 34, ly=330, anchor="start", ln=14)
    m("m03", "U_input", "T_blur", "B+35", "T+35", label="Ввод и потеря фокуса (blur)", lx=X(4) + 39, ly=438, anchor="start", ln=14)
    m("m04", "T_err", "U_input", "T", "B+5", via=[(X(5), 268), (X(4) + 5, 268)], label="Подсказка под полем", lx=X(5) + 6, ly=330, anchor="start", ln=14)
    m("m05", "T_upd", "U_submit", "T", "B", label="Кнопка «Отправить» доступна", lx=X(7) + 6, ly=330, anchor="start", ln=14)
    m("m06", "U_submit", "T_send", "B+25", "T", via=[(X(7) + 25, 268), (X(8), 268)], label="Отправка формы", lx=X(8) + 6, ly=330, anchor="start", ln=14)
    m("m07", "U_input", "BE3", "B-55", "L", via=[(X(4) - 55, 200), (X(4) - 70, 200), (X(4) - 70, LO + 38)], label="Отмена пользователем", lx=X(4) - 76, ly=600, anchor="end", ln=12)
    m("m10", "T_uniq", "P_db", "B-20", ("abs", X(10) - 20, DBT), label="Запрос: email уже есть?", lx=X(10) - 24, ly=1300, anchor="end", ln=24)
    m("m11", "P_db", "T_uniq", ("abs", X(10) + 20, DBT), "B+20", label="Ответ: свободен / занят", lx=X(10) + 24, ly=1300, anchor="start", ln=24)
    m("m12", "T_sms", "S_s", "B", "T", label="Запрос на отправку SMS", lx=X(14) + 6, ly=1120, anchor="start", ln=14)
    m("m13", "S_end", "U_wait", "R", "T+25", via=[(X(19), SM), (X(19), 38), (X(15) + 25, 38)], label="SMS с кодом", lx=X(19) - 6, ly=SM - 20, anchor="end", ln=14)
    m("m14", "U_newcode", "T_gen", "B", "T", label="Запрос нового кода", lx=X(13) + 6, ly=330, anchor="start", ln=14)
    m("m15", "U_wait", "T_check", "B+5", "T+5", label="Введённый код", lx=X(15) + 9, ly=330, anchor="start", ln=14)
    m("m16", "T_retry", "U_wait", "T", "B+40", via=[(X(17), 268), (X(15) + 40, 268)], label="Код неверный, повторите", lx=X(16) + 6, ly=264, anchor="middle", ln=24)
    m("m17", "T_save", "P_db", "B-20", ("abs", X(16) - 20, DBT), label="Запись пользователя и согласий", lx=X(16) - 24, ly=1300, anchor="end", ln=30)
    m("m18", "P_db", "T_save", ("abs", X(16) + 10, DBT), "B+10", label="Подтверждение записи", lx=X(16) + 14, ly=1300, anchor="start", ln=24)

    # ------------------------------------------------- data associations
    a = lambda i, p, q, sp, tp, **k: d.flow(i, "assoc", p, q, sp, tp, **k)  # noqa: E731
    a("a01", "T_open", "DO_form", "T-42", "B")
    a("a02", "DO_cons", "T_open", "B", "T+42")
    a("a03", "T_send", "DO_user", "T+48", "B")
    a("a04", "T_gen", "DO_code", "B", "T")
    a("a05", "DO_code", "T_check", "R", "B")
    a("a06", "DO_u2", "T_save", "R", "L")
    a("a07", "DO_c2", "T_save", "T", "T-20", via=[(X(15) - 55, DS - 56), (X(16) - 20, DS - 56)])
    return d


# ===========================================================================
# 2. STAGE 3a: VALIDATION ON DESKTOP (on blur + submit)
# ===========================================================================
def validation_diagram():
    W, H = 1400, 760
    d = Diagram("validation", W, H)
    X = lambda c: 130 + 150 * c  # noqa: E731
    Y1, YE, Y2, Y3 = 255, 415, 545, 665
    d.pool("P_user", "Пользователь (браузер)", 15, 20, W - 30, 60, black=True)
    d.pool("P_ui", "UI/UX (Frontend)", 15, 130, W - 30, 610)
    UI = dict(pool="P_ui")

    d.ev("S1", X(0), Y1, "Поле X потеряло фокус", "start", "message", lab="B", lw=14, **UI)
    d.task("T1", X(1), Y1, "Потеря фокуса на поле X", "task", **UI)
    d.gw("G_pat", X(2), Y1, "Соответствует шаблону?", "xor", lab="T", lw=14, **UI)
    d.task("T_req", X(3), Y1, "Проверить обязательность", "task", **UI)
    d.gw("G_req", X(4), Y1, "Обязательное поле заполнено?", "xor", lab="T", lw=14, **UI)
    d.gw("Mg", X(3), YE, "", "xor", **UI)
    d.task("T_err", X(4), YE, "Показать ошибку под полем", "task", **UI)
    d.task("T_red", X(5), YE, "Подсветить поле красным", "task", **UI)
    d.task("T_btn", X(6), Y1, "Обновить состояние кнопки «Отправить»", "task", **UI)
    d.ev("E1", X(7), Y1, "Состояние кнопки обновлено", "end", lab="B", lw=14, **UI)

    d.ev("S2", X(0), Y2, "Нажата «Отправить» / Enter", "start", "message", lab="B", lw=14, **UI)
    d.task("T_all", X(1), Y2, "Проверить все поля формы", "task", **UI)
    d.gw("G_all", X(2), Y2, "Все поля валидны?", "xor", lab="T", lw=12, **UI)
    d.task("T_pass", X(3), Y2, "Передать данные на бэкенд", "send", **UI)
    d.ev("E2", X(4), Y2, "Отправка выполнена", "end", lab="B", lw=14, **UI)
    d.task("T_stop", X(3), Y3, "Прервать отправку, вернуть фокус на первое ошибочное поле", "task", **UI)
    d.ev("E3", X(4) + 20, Y3, "Отправка заблокирована", "end", lab="B", lw=14, **UI)

    s = lambda i, p, q, sp="R", tp="L", **k: d.flow(i, "seq", p, q, sp, tp, **k)  # noqa: E731
    s("v01", "S1", "T1"); s("v02", "T1", "G_pat")
    s("v03", "G_pat", "T_req", label="да", lx=X(2) + 30, ly=Y1 - 6, anchor="start", ln=6)
    s("v04", "G_pat", "Mg", "B", "L", label="нет", lx=X(2) + 8, ly=Y1 + 48, anchor="start", ln=6)
    s("v05", "T_req", "G_req")
    s("v06", "G_req", "T_btn", label="да", lx=X(4) + 30, ly=Y1 - 6, anchor="start", ln=6)
    s("v07", "G_req", "Mg", "B", "T", label="нет", lx=X(4) + 8, ly=Y1 + 48, anchor="start", ln=6)
    s("v08", "Mg", "T_err"); s("v09", "T_err", "T_red")
    s("v10", "T_red", "T_btn", "R", "B")
    s("v11", "T_btn", "E1")
    s("v20", "S2", "T_all"); s("v21", "T_all", "G_all")
    s("v22", "G_all", "T_pass", label="да", lx=X(2) + 30, ly=Y2 - 6, anchor="start", ln=6)
    s("v23", "T_pass", "E2")
    s("v24", "G_all", "T_stop", "B", "L", label="нет", lx=X(2) + 8, ly=Y2 + 48, anchor="start", ln=6)
    s("v25", "T_stop", "E3")

    m = lambda i, p, q, sp, tp, **k: d.flow(i, "msg", p, q, sp, tp, **k)  # noqa: E731
    m("vm1", "P_user", "S1", ("abs", X(0), 80), "T", label="Уход с поля (on blur)", lx=X(0) + 6, ly=165, anchor="start", ln=18)
    m("vm2", "P_user", "S2", ("abs", X(0) - 70, 80), "L", via=[(X(0) - 70, Y2)], label="Клик / Enter", lx=X(0) - 66, ly=340, anchor="start", ln=14)
    return d


# ===========================================================================
# 3. STAGE 3b: CONSENT HANDLING ON DESKTOP
# ===========================================================================
def consent_diagram():
    W, H = 1480, 720
    d = Diagram("consents", W, H)
    X = lambda c: 130 + 150 * c  # noqa: E731
    Y1, Y2, Y3 = 175, 335, 520
    d.pool("P_ui", "UI/UX (Frontend)", 15, 20, W - 30, 400)
    d.pool("P_auth", "AuthService (Backend)", 15, 450, W - 30, 160)
    d.pool("P_db", "База данных", 15, 640, W - 30, 50, black=True)
    UI = dict(pool="P_ui")
    d.ev("S", X(0), Y1, "Открыта форма регистрации", "start", lab="B", lw=14, **UI)
    d.task("T_show", X(1), Y1, "Отобразить чекбоксы и ссылки на документы", "task", **UI)
    d.data("DO_doc", X(1), Y1 - 100, "Документ согласия", lab="R", lw=12, **UI)
    d.task("T_chk", X(2), Y1, "Проверить, что все обязательные галочки проставлены", "task", **UI)
    d.gw("G", X(3), Y1, "Есть непроставленные обязательные согласия?", "xor", lab="T", lw=20, **UI)
    d.task("T_lock", X(3), Y2, "Заблокировать кнопку отправки", "task", **UI)
    d.task("T_hint", X(4), Y2, "Показать подсказку «Примите условия»", "task", **UI)
    d.ev("E_wait", X(5), Y2, "Ожидание действий пользователя", "end", lab="B", lw=14, **UI)
    d.task("T_unlock", X(4), Y1, "Разблокировать кнопку отправки", "task", **UI)
    d.task("T_pass", X(6), Y1, "Передать согласия на сервер", "send", **UI)
    AU = dict(pool="P_auth")
    d.ev("A_s", X(6), Y3, "Согласия получены", "start", "message", lab="L", lw=12, **AU)
    d.task("A_rec", X(7), Y3, "Записать Consent в БД с датой и типом", "service", **AU)
    d.ev("A_end", X(8), Y3, "Согласия сохранены", "end", lab="B", lw=14, **AU)

    s = lambda i, p, q, sp="R", tp="L", **k: d.flow(i, "seq", p, q, sp, tp, **k)  # noqa: E731
    s("c01", "S", "T_show"); s("c02", "T_show", "T_chk"); s("c03", "T_chk", "G")
    s("c04", "G", "T_lock", "B", "T", label="да", lx=X(3) + 8, ly=Y1 + 52, anchor="start", ln=6)
    s("c05", "T_lock", "T_hint"); s("c06", "T_hint", "E_wait")
    s("c07", "G", "T_unlock", label="нет", lx=X(3) + 30, ly=Y1 - 6, anchor="start", ln=6)
    s("c08", "T_unlock", "T_pass")
    s("c20", "A_s", "A_rec"); s("c21", "A_rec", "A_end")
    m = lambda i, p, q, sp, tp, **k: d.flow(i, "msg", p, q, sp, tp, **k)  # noqa: E731
    m("cm1", "T_pass", "A_s", "B", "T", label="Согласия: тип + версия + время", lx=X(6) + 6, ly=400, anchor="start", ln=18)
    m("cm2", "A_rec", "P_db", "B", ("abs", X(7), 640), label="Запись Consent", lx=X(7) + 6, ly=632, anchor="start", ln=14)
    a = lambda i, p, q, sp, tp, **k: d.flow(i, "assoc", p, q, sp, tp, **k)  # noqa: E731
    a("ca1", "DO_doc", "T_show", "B", "T")
    return d


if __name__ == "__main__":
    save(main_diagram(), "registration")
    save(validation_diagram(), "validation")
    save(consent_diagram(), "consents")
    print("ok")
