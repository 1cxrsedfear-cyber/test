"""Tiny BPMN 2.0 toolkit: one model -> SVG (BPMN look) + .bpmn XML with diagram interchange (DI).

Elements: pools/lanes, start/end/intermediate/boundary events, tasks, gateways, data objects.
Flows: sequence / message / association with explicit orthogonal waypoints.
"""
import html
import math

FONT = "DejaVu Sans, Arial, sans-serif"
INK = "#222"


def esc(s):
    return html.escape(s, quote=True)


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


class Diagram:
    def __init__(self, name, W, H):
        self.name, self.W, self.H = name, W, H
        self.pools = []      # dict(id,name,x,y,w,h,lanes=[(id,name,y,h)],black)
        self.nodes = {}      # id -> dict
        self.flows = []
        self.order = []

    # ------------------------------------------------------------------ model
    def pool(self, id, name, x, y, w, h, lanes=None, black=False):
        self.pools.append(dict(id=id, name=name, x=x, y=y, w=w, h=h, lanes=lanes or [], black=black))

    def _add(self, id, **kw):
        kw["id"] = id
        self.nodes[id] = kw
        self.order.append(id)
        return kw

    def task(self, id, x, y, name, kind="task", pool=None, lane=None, w=124, h=76):
        return self._add(id, type="task", kind=kind, x=x, y=y, w=w, h=h, name=name, pool=pool, lane=lane)

    def gw(self, id, x, y, name, kind="xor", lab="T", pool=None, lane=None, lw=16):
        return self._add(id, type="gw", kind=kind, x=x, y=y, w=46, h=46, name=name, lab=lab, pool=pool, lane=lane, lw=lw)

    def ev(self, id, x, y, name, kind="start", defn=None, lab="B", pool=None, lane=None, lw=16, lx=0, ly=0):
        # kind: start | end | catch | throw ; defn: None|message|timer|error
        return self._add(id, type="ev", kind=kind, defn=defn, x=x, y=y, w=36, h=36, name=name, lab=lab, pool=pool, lane=lane, lw=lw, lx=lx, ly=ly)

    def boundary(self, id, host, side, off, defn, name, lab="B", lw=16, lx=0, ly=0):
        h = self.nodes[host]
        if side == "B":
            x, y = h["x"] + off, h["y"] + h["h"] / 2
        elif side == "T":
            x, y = h["x"] + off, h["y"] - h["h"] / 2
        elif side == "R":
            x, y = h["x"] + h["w"] / 2, h["y"] + off
        else:
            x, y = h["x"] - h["w"] / 2, h["y"] + off
        return self._add(id, type="ev", kind="boundary", defn=defn, x=x, y=y, w=30, h=30, name=name, lab=lab, host=host,
                         pool=h["pool"], lane=h["lane"], lw=lw, lx=lx, ly=ly)

    def data(self, id, x, y, name, lab="B", lw=14, pool=None, lane=None, lx=0, ly=0):
        return self._add(id, type="data", x=x, y=y, w=28, h=36, name=name, lab=lab, lw=lw, pool=pool, lane=lane, lx=lx, ly=ly)

    def flow(self, id, kind, src, tgt, sp="R", tp="L", via=None, label=None, lx=None, ly=None, ln=18, anchor="middle"):
        self.flows.append(dict(id=id, kind=kind, src=src, tgt=tgt, sp=sp, tp=tp, via=via, label=label, lx=lx, ly=ly, ln=ln, anchor=anchor))

    # ---------------------------------------------------------------- routing
    def port(self, ref, spec):
        if ref in self.nodes:
            n = self.nodes[ref]
            x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        else:
            p = next(p for p in self.pools if p["id"] == ref)
            x, y, w, h = p["x"] + p["w"] / 2, p["y"] + p["h"] / 2, p["w"], p["h"]
        side, off = spec[0], 0
        if len(spec) > 1:
            off = float(spec[1:])
        if side == "T":
            return (x + off, y - h / 2)
        if side == "B":
            return (x + off, y + h / 2)
        if side == "L":
            return (x - w / 2, y + off)
        return (x + w / 2, y + off)

    def waypoints(self, f):
        p1 = self.port(f["src"], f["sp"])
        p2 = self.port(f["tgt"], f["tp"])
        if f["via"] is not None:
            return [p1] + list(f["via"]) + [p2]
        a, b = f["sp"][0], f["tp"][0]
        (x1, y1), (x2, y2) = p1, p2
        if a in "RL" and b in "RL":
            if abs(y1 - y2) < 1:
                return [p1, p2]
            mx = (x1 + x2) / 2
            return [p1, (mx, y1), (mx, y2), p2]
        if a in "TB" and b in "TB":
            if abs(x1 - x2) < 1:
                return [p1, p2]
            my = (y1 + y2) / 2
            return [p1, (x1, my), (x2, my), p2]
        if a in "RL" and b in "TB":
            return [p1, (x2, y1), p2]
        return [p1, (x1, y2), p2]

    # -------------------------------------------------------------------- SVG
    def svg(self):
        o = []
        o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}" font-family="{FONT}">')
        o.append('''<defs>
<marker id="seq" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker>
<marker id="msgEnd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#fff" stroke="#222" stroke-width="1.2"/></marker>
<marker id="msgStart" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8"><circle cx="5" cy="5" r="3.4" fill="#fff" stroke="#222" stroke-width="1.2"/></marker>
<marker id="assoc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9" fill="none" stroke="#555" stroke-width="1.2"/></marker>
</defs>''')
        o.append(f'<rect width="{self.W}" height="{self.H}" fill="#ffffff"/>')
        for p in self.pools:
            o += self._pool_svg(p)
        for f in self.flows:
            o += self._flow_svg(f)
        for nid in self.order:
            n = self.nodes[nid]
            o += {"task": self._task_svg, "gw": self._gw_svg, "ev": self._ev_svg, "data": self._data_svg}[n["type"]](n)
        o.append("</svg>")
        return "\n".join(o)

    def _text(self, x, y, lines, size=11, anchor="middle", weight="normal", fill=INK, lh=None, italic=False):
        lh = lh or size * 1.22
        st = ' font-style="italic"' if italic else ""
        out = [f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{st}>']
        for i, ln in enumerate(lines):
            out.append(f'<tspan x="{x:.1f}" dy="{0 if i == 0 else lh:.1f}">{esc(ln)}</tspan>')
        out.append("</text>")
        return "".join(out)

    def _pool_svg(self, p):
        o = []
        x, y, w, h = p["x"], p["y"], p["w"], p["h"]
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#f3f3f3" if p["black"] else "#fff"}" stroke="{INK}" stroke-width="1.6"/>')
        if p["black"]:
            o.append(self._text(x + 20, y + h / 2 + 5, [p["name"]], 13, anchor="start", weight="bold"))
            return o
        o.append(f'<line x1="{x+30}" y1="{y}" x2="{x+30}" y2="{y+h}" stroke="{INK}" stroke-width="1.6"/>')
        lines = wrap(p["name"], max(8, int(h / 7.2)))
        cx, cy = x + 15, y + h / 2
        o.append(f'<g transform="rotate(-90 {cx} {cy})">{self._text(cx, cy + 4 - (len(lines)-1)*7, lines, 12, weight="bold", lh=14)}</g>')
        for (lid, lname, ly, lh_) in p["lanes"]:
            o.append(f'<rect x="{x+30}" y="{ly}" width="{w-30}" height="{lh_}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
            o.append(f'<rect x="{x+30}" y="{ly}" width="24" height="{lh_}" fill="#eef1f5" stroke="{INK}" stroke-width="1.2"/>')
            cx2, cy2 = x + 42, ly + lh_ / 2
            ls = wrap(lname, max(8, int(lh_ / 6.8)))
            o.append(f'<g transform="rotate(-90 {cx2} {cy2})">{self._text(cx2, cy2 + 3.5 - (len(ls)-1)*6, ls, 10.5, weight="bold", lh=12)}</g>')
        return o

    def _task_svg(self, n):
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        o = [f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w}" height="{h}" rx="10" fill="#fff" stroke="{INK}" stroke-width="1.8"/>']
        lines = wrap(n["name"], int((w - 14) / 6.2))
        lh = 13
        ty = y - (len(lines) - 1) * lh / 2 + 4 + (5 if n["kind"] != "task" else 0)
        o.append(self._text(x, ty, lines, 11, lh=lh))
        ix, iy = x - w / 2 + 8, y - h / 2 + 7
        k = n["kind"]
        if k == "user":
            o.append(f'<circle cx="{ix+5:.1f}" cy="{iy+3:.1f}" r="3" fill="none" stroke="{INK}" stroke-width="1.2"/><path d="M{ix:.1f},{iy+13:.1f} q5,-9 10,0 z" fill="none" stroke="{INK}" stroke-width="1.2"/>')
        elif k == "service":
            o.append(f'<circle cx="{ix+6:.1f}" cy="{iy+6:.1f}" r="3.6" fill="none" stroke="{INK}" stroke-width="1.3"/>')
            for a in range(8):
                ang = a * math.pi / 4
                o.append(f'<line x1="{ix+6+4.6*math.cos(ang):.1f}" y1="{iy+6+4.6*math.sin(ang):.1f}" x2="{ix+6+7*math.cos(ang):.1f}" y2="{iy+6+7*math.sin(ang):.1f}" stroke="{INK}" stroke-width="1.8"/>')
        elif k in ("send", "receive"):
            fill = INK if k == "send" else "#fff"
            sc = "#fff" if k == "send" else INK
            o.append(f'<rect x="{ix:.1f}" y="{iy+2:.1f}" width="14" height="10" fill="{fill}" stroke="{INK}" stroke-width="1.1"/><polyline points="{ix:.1f},{iy+2:.1f} {ix+7:.1f},{iy+8:.1f} {ix+14:.1f},{iy+2:.1f}" fill="none" stroke="{sc}" stroke-width="1.1"/>')
        return o

    def _gw_svg(self, n):
        x, y = n["x"], n["y"]
        r = 23
        o = [f'<polygon points="{x},{y-r} {x+r},{y} {x},{y+r} {x-r},{y}" fill="#fff" stroke="{INK}" stroke-width="1.8"/>']
        if n["kind"] == "and":
            o.append(f'<path d="M{x-10},{y} H{x+10} M{x},{y-10} V{y+10}" stroke="{INK}" stroke-width="3.2"/>')
        else:
            o.append(f'<path d="M{x-8},{y-8} L{x+8},{y+8} M{x+8},{y-8} L{x-8},{y+8}" stroke="{INK}" stroke-width="3"/>')
        if n["name"]:
            lines = wrap(n["name"], n["lw"])
            side = n["lab"]
            if side == "T":
                o.append(self._text(x, y - r - 6 - (len(lines) - 1) * 12.5, lines, 11, weight="bold", lh=12.5))
            elif side == "B":
                o.append(self._text(x, y + r + 14, lines, 11, weight="bold", lh=12.5))
            elif side == "R":
                o.append(self._text(x + r + 6, y + 4, lines, 11, anchor="start", weight="bold", lh=12.5))
            else:
                o.append(self._text(x - r - 6, y + 4, lines, 11, anchor="end", weight="bold", lh=12.5))
        return o

    def _envelope(self, x, y, fill):
        sc = "#fff" if fill == INK else INK
        return (f'<rect x="{x-7:.1f}" y="{y-5:.1f}" width="14" height="10" fill="{fill}" stroke="{INK}" stroke-width="1.1"/>'
                f'<polyline points="{x-7:.1f},{y-5:.1f} {x:.1f},{y+1:.1f} {x+7:.1f},{y-5:.1f}" fill="none" stroke="{sc}" stroke-width="1.1"/>')

    def _ev_svg(self, n):
        x, y, kind, defn = n["x"], n["y"], n["kind"], n["defn"]
        r = n["w"] / 2
        o = []
        if kind == "start":
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
        elif kind == "end":
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="4.2"/>')
        else:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="1.6"/><circle cx="{x}" cy="{y}" r="{r-3.5}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        filled = INK if kind in ("end", "throw") else "#fff"
        if defn == "message":
            o.append(self._envelope(x, y, filled))
        elif defn == "timer":
            o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#fff" stroke="{INK}" stroke-width="1.3"/><path d="M{x},{y-5} V{y} L{x+4},{y+2}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
            for a in range(12):
                ang = a * math.pi / 6
                o.append(f'<line x1="{x+5.8*math.cos(ang):.1f}" y1="{y+5.8*math.sin(ang):.1f}" x2="{x+7*math.cos(ang):.1f}" y2="{y+7*math.sin(ang):.1f}" stroke="{INK}" stroke-width="0.8"/>')
        elif defn == "error":
            o.append(f'<polygon points="{x-6},{y+6} {x-2},{y-3} {x+1},{y+2} {x+6},{y-7} {x+2},{y+3} {x-1},{y-2}" fill="{filled}" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round"/>')
        if n["name"]:
            lines = wrap(n["name"], n["lw"])
            side = n["lab"]
            lx, ly = n.get("lx", 0), n.get("ly", 0)
            if side == "B":
                o.append(self._text(x + lx, y + r + 13 + ly, lines, 10.5, lh=12))
            elif side == "T":
                o.append(self._text(x + lx, y - r - 6 - (len(lines) - 1) * 12 + ly, lines, 10.5, lh=12))
            elif side == "R":
                o.append(self._text(x + r + 6 + lx, y + 4 + ly - (len(lines) - 1) * 6, lines, 10.5, anchor="start", lh=12))
            else:
                o.append(self._text(x - r - 6 + lx, y + 4 + ly - (len(lines) - 1) * 6, lines, 10.5, anchor="end", lh=12))
        return o

    def _data_svg(self, n):
        x, y = n["x"], n["y"]
        w, h = 24, 32
        x0, y0 = x - w / 2, y - h / 2
        o = [f'<path d="M{x0},{y0} H{x0+w-8} L{x0+w},{y0+8} V{y0+h} H{x0} Z" fill="#fff" stroke="{INK}" stroke-width="1.4"/>'
             f'<path d="M{x0+w-8},{y0} V{y0+8} H{x0+w}" fill="none" stroke="{INK}" stroke-width="1.2"/>']
        lines = wrap(n["name"], n["lw"])
        lx, ly = n.get("lx", 0), n.get("ly", 0)
        side = n["lab"]
        if side == "B":
            o.append(self._text(x + lx, y + h / 2 + 12 + ly, lines, 10, lh=11.5))
        elif side == "R":
            o.append(self._text(x + w / 2 + 6 + lx, y - (len(lines) - 1) * 5.75 + 4 + ly, lines, 10, anchor="start", lh=11.5))
        elif side == "L":
            o.append(self._text(x - w / 2 - 6 + lx, y - (len(lines) - 1) * 5.75 + 4 + ly, lines, 10, anchor="end", lh=11.5))
        else:
            o.append(self._text(x + lx, y - h / 2 - 5 - (len(lines) - 1) * 11.5 + ly, lines, 10, lh=11.5))
        return o

    def _flow_svg(self, f):
        pts = self.waypoints(f)
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        if f["kind"] == "seq":
            s = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.6" marker-end="url(#seq)"/>'
        elif f["kind"] == "msg":
            s = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="7 4" marker-start="url(#msgStart)" marker-end="url(#msgEnd)"/>'
        else:
            s = f'<path d="{d}" fill="none" stroke="#555" stroke-width="1.2" stroke-dasharray="2 3" marker-end="url(#assoc)"/>'
        o = [s]
        if f["label"]:
            lines = wrap(f["label"], f["ln"])
            lx, ly = f["lx"], f["ly"]
            if lx is None:
                # middle of the longest segment
                best = max(range(len(pts) - 1), key=lambda i: abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]))
                lx = (pts[best][0] + pts[best + 1][0]) / 2
                ly = (pts[best][1] + pts[best + 1][1]) / 2
            wmax = max(len(l) for l in lines) * 5.1 + 6
            hh = len(lines) * 10.5 + 3
            ax = f["anchor"]
            rx = lx - wmax / 2 if ax == "middle" else (lx - 2 if ax == "start" else lx - wmax + 2)
            o.append(f'<rect x="{rx:.1f}" y="{ly-hh+4:.1f}" width="{wmax:.1f}" height="{hh:.1f}" fill="#fff" fill-opacity="0.85"/>')
            o.append(self._text(lx, ly - hh + 13, lines, 9, anchor=ax, fill="#444", lh=10.5, italic=True))
        return o

    # -------------------------------------------------------------- BPMN XML
    def bpmn(self):
        X = []
        A = X.append
        A('<?xml version="1.0" encoding="UTF-8"?>')
        A('<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
          'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" '
          f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="Definitions_{self.name}" targetNamespace="http://bpmn.io/schema/bpmn" exporter="bpmnlib" exporterVersion="1.0">')
        procs = [p for p in self.pools if not p["black"]]
        A(f'  <bpmn:collaboration id="Collab_{self.name}">')
        for p in self.pools:
            if p["black"]:
                A(f'    <bpmn:participant id="{p["id"]}" name="{esc(p["name"])}"/>')
            else:
                A(f'    <bpmn:participant id="{p["id"]}" name="{esc(p["name"])}" processRef="Proc_{p["id"]}"/>')
        for f in self.flows:
            if f["kind"] == "msg":
                mname = ' name="%s"' % esc(f["label"]) if f["label"] else ""
                A(f'    <bpmn:messageFlow id="{f["id"]}" sourceRef="{f["src"]}" targetRef="{f["tgt"]}"{mname}/>')
        A("  </bpmn:collaboration>")
        # data objects need unique ids
        for p in procs:
            nodes = [n for n in (self.nodes[i] for i in self.order) if n["pool"] == p["id"]]
            A(f'  <bpmn:process id="Proc_{p["id"]}" isExecutable="false">')
            if p["lanes"]:
                A("    <bpmn:laneSet>")
                for (lid, lname, ly, lh_) in p["lanes"]:
                    A(f'      <bpmn:lane id="{lid}" name="{esc(lname)}">')
                    for n in nodes:
                        if n["lane"] == lid and n["type"] != "data":
                            A(f'        <bpmn:flowNodeRef>{n["id"]}</bpmn:flowNodeRef>')
                    A("      </bpmn:lane>")
                A("    </bpmn:laneSet>")
            assoc_out = {}
            assoc_in = {}
            assocs = []
            for f in self.flows:
                if f["kind"] == "assoc":
                    s, t = f["src"], f["tgt"]
                    if self.nodes[s]["type"] == "data":
                        assoc_in.setdefault(t, []).append((f["id"], s))
                    else:
                        assoc_out.setdefault(s, []).append((f["id"], t))
            for n in nodes:
                t = n["type"]
                nm = f' name="{esc(n["name"])}"' if n["name"] else ""
                outs = "".join(f'<bpmn:outgoing>{f["id"]}</bpmn:outgoing>' for f in self.flows if f["kind"] == "seq" and f["src"] == n["id"])
                ins = "".join(f'<bpmn:incoming>{f["id"]}</bpmn:incoming>' for f in self.flows if f["kind"] == "seq" and f["tgt"] == n["id"])
                if t == "task":
                    tag = {"task": "task", "user": "userTask", "service": "serviceTask", "send": "sendTask", "receive": "receiveTask"}[n["kind"]]
                    inner = ins + outs
                    for (aid, s) in assoc_in.get(n["id"], []):
                        inner += f'<bpmn:dataInputAssociation id="{aid}"><bpmn:sourceRef>{s}Ref</bpmn:sourceRef></bpmn:dataInputAssociation>'
                    for (aid, tt) in assoc_out.get(n["id"], []):
                        inner += f'<bpmn:dataOutputAssociation id="{aid}"><bpmn:targetRef>{tt}Ref</bpmn:targetRef></bpmn:dataOutputAssociation>'
                    A(f'    <bpmn:{tag} id="{n["id"]}"{nm}>{inner}</bpmn:{tag}>')
                elif t == "gw":
                    A(f'    <bpmn:{"parallelGateway" if n["kind"] == "and" else "exclusiveGateway"} id="{n["id"]}"{nm}>{ins}{outs}</bpmn:{"parallelGateway" if n["kind"] == "and" else "exclusiveGateway"}>')
                elif t == "ev":
                    d = n["defn"]
                    dd = {"message": "<bpmn:messageEventDefinition/>", "timer": '<bpmn:timerEventDefinition><bpmn:timeDuration xsi:type="bpmn:tFormalExpression">PT5M</bpmn:timeDuration></bpmn:timerEventDefinition>',
                          "error": "<bpmn:errorEventDefinition/>"}.get(d, "")
                    k = n["kind"]
                    if k == "start":
                        A(f'    <bpmn:startEvent id="{n["id"]}"{nm}>{outs}{dd}</bpmn:startEvent>')
                    elif k == "end":
                        A(f'    <bpmn:endEvent id="{n["id"]}"{nm}>{ins}{dd}</bpmn:endEvent>')
                    elif k == "boundary":
                        A(f'    <bpmn:boundaryEvent id="{n["id"]}"{nm} attachedToRef="{n["host"]}" cancelActivity="true">{outs}{dd}</bpmn:boundaryEvent>')
                    elif k == "throw":
                        A(f'    <bpmn:intermediateThrowEvent id="{n["id"]}"{nm}>{ins}{outs}{dd}</bpmn:intermediateThrowEvent>')
                    else:
                        A(f'    <bpmn:intermediateCatchEvent id="{n["id"]}"{nm}>{ins}{outs}{dd}</bpmn:intermediateCatchEvent>')
                elif t == "data":
                    A(f'    <bpmn:dataObjectReference id="{n["id"]}Ref" name="{esc(n["name"])}" dataObjectRef="{n["id"]}"/>')
                    A(f'    <bpmn:dataObject id="{n["id"]}"/>')
            for f in self.flows:
                if f["kind"] == "seq" and self.nodes[f["src"]]["pool"] == p["id"]:
                    nm = f' name="{esc(f["label"])}"' if f["label"] else ""
                    A(f'    <bpmn:sequenceFlow id="{f["id"]}" sourceRef="{f["src"]}" targetRef="{f["tgt"]}"{nm}/>')
            A("  </bpmn:process>")
        # diagram
        A(f'  <bpmndi:BPMNDiagram id="Diagram_{self.name}">')
        A(f'    <bpmndi:BPMNPlane id="Plane_{self.name}" bpmnElement="Collab_{self.name}">')
        for p in self.pools:
            A(f'      <bpmndi:BPMNShape id="{p["id"]}_di" bpmnElement="{p["id"]}" isHorizontal="true"><dc:Bounds x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["h"]}"/></bpmndi:BPMNShape>')
            for (lid, lname, ly, lh_) in p["lanes"]:
                A(f'      <bpmndi:BPMNShape id="{lid}_di" bpmnElement="{lid}" isHorizontal="true"><dc:Bounds x="{p["x"]+30}" y="{ly}" width="{p["w"]-30}" height="{lh_}"/></bpmndi:BPMNShape>')
        for nid in self.order:
            n = self.nodes[nid]
            bid = nid + ("Ref" if n["type"] == "data" else "")
            extra = ' isMarkerVisible="true"' if (n["type"] == "gw" and n["kind"] == "xor") else ""
            A(f'      <bpmndi:BPMNShape id="{nid}_di" bpmnElement="{bid}"{extra}><dc:Bounds x="{n["x"]-n["w"]/2:.1f}" y="{n["y"]-n["h"]/2:.1f}" width="{n["w"]}" height="{n["h"]}"/></bpmndi:BPMNShape>')
        for f in self.flows:
            A(f'      <bpmndi:BPMNEdge id="{f["id"]}_di" bpmnElement="{f["id"]}">')
            for (x, y) in self.waypoints(f):
                A(f'        <di:waypoint x="{x:.1f}" y="{y:.1f}"/>')
            A("      </bpmndi:BPMNEdge>")
        A("    </bpmndi:BPMNPlane>")
        A("  </bpmndi:BPMNDiagram>")
        A("</bpmn:definitions>")
        return "\n".join(X)
