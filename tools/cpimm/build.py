"""Builder API: write a mapping as Python expressions, get a Mapping model.

    b = Builder("Map_X", source=Link(...), target=Link(...))
    belnr = b.src("/ORDERS02/IDOC/E1EDK01/BELNR")
    b.map("/OrdersMessage/DocumentId/DocumentNo", belnr)
    b.map("/OrdersMessage/Header/SchemaId", b.const("EDI.ORDER"))
    b.map(".../LineNo", b.udf("removezeros", "removezeros", b.src(".../POSEX")))
    m = b.finish()

Rules taken from the references (FORMAT_NOTES §3.7):
  * Reusing the same Python expression object in several places creates a shared node.
    The first use gets object_uid="rN" and later uses become <brick object_uid="rN"/>.
    Only reused nodes get a uid.
  * Targets that share a node get one common <group object_uid="gN"/>. Others get <group/>.
  * viewData coordinates are generated (layout only, UNVERIFIED whether CPI needs them).
"""
from __future__ import annotations

import copy
import time
import uuid
from collections import Counter

from .model import (ADDITIONAL_PROPS, Arg, Func, Link, Mapping, Param, Ref, Src, Target)

COL, ROW, X0, Y0 = 130, 60, 30, 33


class Out:
    """Select output n of a multi-output UDF: b.map(path, b.out(udf_call, 1))."""
    def __init__(self, expr, n: int):
        self.expr, self.n = expr, str(n)


class Builder:
    def __init__(self, name: str, source: Link, target: Link, namespaces=None, udfs=None):
        self.m = Mapping(name=name, source=source, target=target,
                         namespaces=list(namespaces or []), udfs=list(udfs or []),
                         modif_at_long=str(int(time.time() * 1000)), text_obj_id=uuid.uuid4().hex,
                         additional_properties=list(ADDITIONAL_PROPS))
        self._targets: list[tuple[str, object]] = []

    # -- leaves ------------------------------------------------------------------
    def src(self, path: str, context: str | None = None) -> Src:
        return Src(path, context=context)

    def const(self, value: str) -> Func:
        return Func("const", params=[Param("value", text=value)])

    # -- functions ---------------------------------------------------------------
    def fn(self, fname: str, *inputs, **params) -> Func:
        """Standard function (fns="dflt"). Params are written in the order given."""
        return self._func(fname, "dflt", inputs, params)

    def udf(self, script: str, fname: str, *inputs, context_param: bool = False) -> Func:
        """Groovy UDF. Set context_param=True for array UDFs (String[] inputs + Output)."""
        if script + ".groovy" not in self.m.udfs:
            self.m.udfs.append(script + ".groovy")
        return self._func(fname, script, inputs, {"context": ""} if context_param else {})

    def table(self, fname: str, inp, rows: list[tuple[str, str]], default: str = "", strategy: str = "2") -> Func:
        """FixValues with an inline table. strategy: see FORMAT_NOTES §3.11 (numbers UNVERIFIED except 1)."""
        return Func(fname, "dflt", [Arg(inp)], [Param("vmdefault", text=default), Param("vmstrategy", text=strategy),
                                                 Param("table", table=list(rows))])

    def out(self, expr: Func, n: int):
        """Output n of a multi-output UDF. Output 0 is a plain <arg> (FORMAT_NOTES §3.10, ACC NAME)."""
        return expr if n == 0 else Out(expr, n)

    @staticmethod
    def _func(fname, fns, inputs, params) -> Func:
        args = [Arg(i.expr, i.n) if isinstance(i, Out) else Arg(i) for i in inputs]
        ps = []
        for k, v in params.items():
            if isinstance(v, dict) and "calend" in v:
                ps.append(Param(k, calend=list(v["calend"])))
            else:
                ps.append(Param(k, text=str(v)))
        return Func(fname, fns, args, ps or None)

    # -- targets -----------------------------------------------------------------
    def map(self, path: str, expr=None):
        self._targets.append((path, expr))

    def disabled(self, path: str):
        self._targets.append((path, "DISABLED"))

    # -- finish --------------------------------------------------------------------
    def finish(self) -> Mapping:
        self._split_unclean()
        # count how often each expression object is used (shared nodes)
        uses: Counter = Counter()
        owners: dict[int, set[int]] = {}

        def count(x, ti):
            x = x.expr if isinstance(x, Out) else x
            uses[id(x)] += 1
            owners.setdefault(id(x), set()).add(ti)
            if uses[id(x)] == 1 and isinstance(x, Func):
                for a in x.args:
                    count(a.expr, ti)

        for ti, (_, e) in enumerate(self._targets):
            if e not in (None, "DISABLED"):
                count(e, ti)

        # union-find over targets that share a node -> groups
        parent = list(range(len(self._targets)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for oid, ts in owners.items():
            if uses[oid] > 1 and len(ts) > 1:
                ts = sorted(ts)
                for t in ts[1:]:
                    parent[find(t)] = find(ts[0])
        shared_roots = {find(t) for oid, ts in owners.items() if uses[oid] > 1 and len(ts) > 1 for t in ts}

        uid_of: dict[int, str] = {}
        rn = [0]

        def emit(x):
            """Copy the tree; first use of a shared object gets a uid, later uses become Ref."""
            if id(x) in uid_of:
                return Ref(uid_of[id(x)])
            uid = None
            if uses[id(x)] > 1:
                uid = f"r{rn[0]}"
                rn[0] += 1
                uid_of[id(x)] = uid
            if isinstance(x, Src):
                return Src(x.path, x.context, uid)
            return Func(x.fname, x.fns, [Arg(emit(a.expr), a.out) for a in x.args], x.params, uid)

        gnames: dict[int, str] = {}
        for ti, (path, e) in enumerate(self._targets):
            t = Target(path)
            if e == "DISABLED":
                t.disabled = True
            elif e is not None:
                if isinstance(e, Out):
                    t.out, e = e.n, e.expr
                t.expr = emit(e)
            r = find(ti)
            if r in shared_roots:
                gnames.setdefault(r, f"g{len(gnames)}")
                t.group = gnames[r]
            self.m.targets.append(t)
        canvases: dict[str, list[Target]] = {}
        for i, t in enumerate(self.m.targets):
            canvases.setdefault(t.group or f"single{i}", []).append(t)
        for ts in canvases.values():
            _layout(ts)
        return self.m

    def _split_unclean(self):
        """User rule (ORDRSP feedback 2026-11-15): share a brick between targets only when the canvas stays
        clean, i.e. the brick sits in the same column (same distance to the target) for every use.
        A use at another distance gets its own copy of the subtree (split)."""
        level_of: dict[int, int] = {}

        def walk(x, level):
            inner = x.expr if isinstance(x, Out) else x
            if id(inner) in level_of:
                if level_of[id(inner)] == level:
                    return x                                    # clean shared use
                inner = copy.deepcopy(inner)                    # split
                x = Out(inner, x.n) if isinstance(x, Out) else inner
            level_of[id(inner)] = level
            if isinstance(inner, Func):
                for a in inner.args:
                    a.expr = walk(a.expr, level + 1)
            return x

        self._targets = [(p, e if e in (None, "DISABLED") else walk(e, 0)) for p, e in self._targets]


def _layout(targets: list[Target]):
    """Left-to-right layout of one editor canvas: a group of targets sharing bricks, or a single target.
    Leaves on the left, targets on the right, one column per distance to the target, so a shared brick
    (same distance for every use, see Builder._split_unclean) lines up for all its targets.
    One row counter for the whole canvas; a shared brick is placed once (its Ref uses keep its position);
    no two bricks get the same x/y."""
    nodes: dict[str, object] = {}

    def collect(x):
        if isinstance(x, (Func, Src)) and x.uid:
            nodes.setdefault(x.uid, x)
        if isinstance(x, Func):
            for a in x.args:
                collect(a.expr)

    def depth(x):
        if isinstance(x, Ref):
            return depth(nodes[x.uid])
        if isinstance(x, Func) and x.args:
            return 1 + max(depth(a.expr) for a in x.args)
        return 0

    for t in targets:
        if t.expr is not None:
            collect(t.expr)
    d = max([depth(t.expr) for t in targets if t.expr is not None], default=0)
    used: dict[int, set[int]] = {}
    next_row = [0]
    pos: dict[str, int] = {}

    def free(col, row):
        while row in used.setdefault(col, set()):
            row = next_row[0]
            next_row[0] += 1
        used[col].add(row)
        next_row[0] = max(next_row[0], row + 1)
        return row

    def place(x, level):
        if isinstance(x, Ref):
            return pos[x.uid]
        col = d - level
        if isinstance(x, Func) and x.args:
            rows = [place(a.expr, level + 1) for a in x.args]
            row = free(col, round(sum(rows) / len(rows)))
        else:
            row = free(col, next_row[0])
        x.xy = (str(X0 + COL * col), str(Y0 + ROW * row))
        if x.uid:
            pos[x.uid] = row
        return row

    for t in targets:
        if t.expr is None:
            t.xy = ("0", "0") if t.disabled else (str(X0 + COL), str(Y0 + ROW * free(1, next_row[0])))
            continue
        row = free(d + 1, place(t.expr, 0))
        t.xy = (str(X0 + COL * (d + 1)), str(Y0 + ROW * row))
