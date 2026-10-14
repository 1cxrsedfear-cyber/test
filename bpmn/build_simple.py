"""Simplified (beginner-level) versions of the three diagrams: same required elements, fewer extras."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402  (patches Diagram.port and gives main_diagram etc.)


def drop(d, node_ids=(), flow_ids=()):
    for n in node_ids:
        d.nodes.pop(n, None)
        if n in d.order:
            d.order.remove(n)
    d.flows = [f for f in d.flows if f["id"] not in flow_ids]


def simple_main():
    d = build.main_diagram()
    d.name = "registration_simple"
    # no "cancel" branch, no duplicated data objects
    drop(d, ["BE3", "T_clean", "E_cancel", "DO_user", "DO_c2"], ["s42", "s43", "m07", "a03", "a07"])
    # keep only the most useful message labels
    keep = {"m01": "Запрос страницы", "m13": "SMS с кодом", "m15": "Введённый код", "m10": "Есть ли такой email?", "m11": "Ответ БД"}
    for f in d.flows:
        if f["kind"] == "msg":
            f["label"] = keep.get(f["id"])
    return d


def simple_validation():
    d = build.validation_diagram()
    d.name = "validation_simple"
    drop(d, ["S2", "T_all", "G_all", "T_pass", "E2", "T_stop", "E3"], ["v20", "v21", "v22", "v23", "v24", "v25", "vm2"])
    d.W, d.H = 1400, 560
    for p in d.pools:
        if p["id"] == "P_ui":
            p["h"] = 400
        if p["id"] == "P_user":
            p["w"] = d.W - 30
        else:
            p["w"] = d.W - 30
    for f in d.flows:
        if f["id"] == "vm1":
            f["label"] = None
    return d


def simple_consents():
    d = build.consent_diagram()
    d.name = "consents_simple"
    return d


if __name__ == "__main__":
    build.save(simple_main(), "registration_simple")
    build.save(simple_validation(), "validation_simple")
    build.save(simple_consents(), "consents_simple")
    print("ok")
