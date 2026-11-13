"""Mapping model for CPI Message Mapping (.mmap) files.

read_mmap(text)   -> Mapping   (fails loudly on anything not described in FORMAT_NOTES)
render_mmap(map)  -> str       (single-line .mmap, byte-identical for standard references)

Every XML shape produced here was copied from the reference exports.
See _reference/FORMAT_NOTES.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .xmltree import E, Node, parse, write

SCRIPT_DIR = "src/main/resources/script"
LABEL_DEFAULT = "21327ec998d3248b3333da4cbe20b699"          # FORMAT_NOTES §2.1
ADDITIONAL_PROPS = ["externalNameSpace", "choiceOccurrence", "groupsOccurrence",
                    "topLevelChoiceOccurrenceApplied"]       # FORMAT_NOTES §2.1


class FormatError(ValueError):
    """The file uses a structure that FORMAT_NOTES does not cover."""


# ----------------------------------------------------------------------------- model
@dataclass
class Link:                    # SOURCE_IFR_MESS / TARGET_IFR_MESS (FORMAT_NOTES §2.2)
    type_id: str               # xsd | wsdl | json
    elems: list[str]           # [file, folder, root/message, (namespace)]


@dataclass
class Param:                   # <param name=..><value>..</value></param>
    name: str
    text: str | None = None                       # plain value ("" = <value/>)
    table: list[tuple[str, str]] | None = None    # FixValues table
    calend: list[tuple[str, str]] | None = None   # TransformDate/currentDate calend_props


@dataclass
class Src:
    path: str
    context: str | None = None
    uid: str | None = None
    xy: tuple[str, str] | None = None
    gid: str = "0"


@dataclass
class Ref:
    uid: str


@dataclass
class Arg:
    expr: "Src | Ref | Func"
    out: str | None = None     # <arg from="n"> : output n of a multi-output UDF


@dataclass
class Func:
    fname: str
    fns: str = "dflt"
    args: list[Arg] = field(default_factory=list)
    params: list[Param] | None = None              # None = no <bindings>
    uid: str | None = None
    xy: tuple[str, str] | None = None


@dataclass
class Target:                                      # one Dst brick
    path: str
    expr: "Src | Ref | Func | None" = None
    xy: tuple[str, str] | None = None
    group: str | None = None                       # <group object_uid="gN"/>
    disabled: bool = False                         # properties/switchedOff=true
    props_first: bool = False                      # <properties> before <group> (seen once, DIR)
    gid: str = "0"
    out: str | None = None                         # <arg from="n"> on the Dst: output n of a multi-output UDF


@dataclass
class Mapping:
    name: str
    target: Link
    source: Link
    udfs: list[str] = field(default_factory=list)          # script file names, in kpos order
    namespaces: list[tuple[str, str]] = field(default_factory=list)   # (prefix, uri)
    targets: list[Target] = field(default_factory=list)
    modif_at_long: str = "0"
    text_obj_id: str = "0" * 32
    label: str = LABEL_DEFAULT
    # Names in <AdditionalProperties>; [] = block absent. References show 4 (MAT, CLF, DOC, DIR),
    # 3 (CCM, JDBC, JE, SUP: no topLevelChoiceOccurrenceApplied) or none (ACC, INV, FLAT).
    additional_properties: list[str] = field(default_factory=lambda: list(ADDITIONAL_PROPS))
    blank_xmlns: bool = True                       # xmlns="" on idInfo, documentation, generic, AdditionalProperties, content; FLAT omits all


# ----------------------------------------------------------------------------- reading
def _need(cond, msg):
    if not cond:
        raise FormatError(msg)


def _xy(n: Node):
    vd = n.children[0] if n.children and n.children[0].tag == "viewData" else None
    _need(vd is not None and [k for k, _ in vd.attrs] == ["x", "y"], f"brick without viewData: {n.attrs}")
    return (vd.get("x"), vd.get("y"))


def _read_value(p: Node) -> Param:
    _need([k for k, _ in p.attrs] == ["name"] and len(p.children) == 1 and p.children[0].tag == "value",
          "unexpected <param> shape")
    v = p.children[0]
    name = p.get("name")
    if not v.children:
        _need(v.selfclose or v.text, f"param {name}: empty <value></value> not seen in references")
        return Param(name, text=v.text or "")
    _need(len(v.children) == 1, f"param {name}: several children in <value>")
    c = v.children[0]
    if c.tag == "properties":
        rows = []
        for pr in c.children:
            _need(pr.tag == "property" and [k for k, _ in pr.attrs] == ["name"] and not pr.children,
                  "unexpected table row")
            _need(not pr.selfclose, "self-closed table row not seen in references")
            rows.append((pr.get("name"), pr.text or ""))
        return Param(name, table=rows)
    if c.tag == "calend_props":
        rows = []
        for pr in c.children:
            _need(not pr.children and pr.text is not None, "unexpected calend_props entry")
            rows.append((pr.tag, pr.text))
        return Param(name, calend=rows)
    raise FormatError(f"param {name}: unknown value content <{c.tag}>")


def _read_expr(b: Node):
    _need(b.tag == "brick", f"expected brick, got {b.tag}")
    keys = [k for k, _ in b.attrs]
    if keys == ["object_uid"]:
        _need(not b.children and b.selfclose, "reference brick with content")
        return Ref(b.get("object_uid"))
    t = b.get("type")
    if t == "Src":
        _need(set(keys) <= {"context", "gid", "object_uid", "path", "type"}, f"Src attrs {keys}")
        _need(len(b.children) == 1, "Src brick with extra children")
        return Src(b.get("path"), b.get("context"), b.get("object_uid"), _xy(b), b.get("gid"))
    if t == "Func":
        _need(set(keys) <= {"fname", "fns", "object_uid", "type"}, f"Func attrs {keys}")
        f = Func(b.get("fname"), b.get("fns"), uid=b.get("object_uid"), xy=_xy(b))
        rest = b.children[1:]
        for i, a in enumerate(c for c in rest if c.tag == "arg"):
            pin = a.get("pin", "0")
            _need(pin == str(i), f"{f.fname}: pins not contiguous")
            _need(set(k for k, _ in a.attrs) <= {"from", "pin"} and len(a.children) == 1, "arg shape")
            f.args.append(Arg(_read_expr(a.children[0]), a.get("from")))
        tags = [c.tag for c in rest]
        _need(tags == ["arg"] * len(f.args) + (["bindings"] if "bindings" in tags else []),
              f"{f.fname}: unexpected children {tags}")
        bd = b.find("bindings")
        if bd is not None:
            _need(not bd.attrs and bd.children, "empty bindings")
            f.params = [_read_value(p) for p in bd.children]
        return f
    raise FormatError(f"unknown brick type {t}")


def _read_link(lr: Node) -> Link:
    lnk = lr.children[0]
    _need(lnk.tag == "lnk" and lnk.attrs == [("rMode", "R")] and len(lr.children) == 1, "lnk shape")
    key = lnk.children[0]
    _need(key.get("version") == "1.1" and len(lnk.children) == 1, "key shape")
    elems = []
    for e in key.children:
        _need(e.tag == "elem" and not e.children, "elem shape")
        _need(e.text or not e.selfclose, "self-closed <elem/> in lnks not seen in references")
        elems.append(e.text or "")
    return Link(key.get("type_id") or key.get("typeID"), elems)


def read_mmap(raw: str, name: str) -> Mapping:
    """Parse a .mmap and check it renders back identically (standard envelope only)."""
    root = parse(raw)
    gen = root.find("generic")
    _need(gen is not None, "no <generic>")
    roles = [(lr.get("role"), lr.get("kpos"), lr) for lr in gen.find("lnks").children]
    _need([r for r, _, _ in roles[:2]] == ["TARGET_IFR_MESS", "SOURCE_IFR_MESS"], "lnks must start TARGET, SOURCE")
    udfs = []
    for i, (role, kpos, lr) in enumerate(roles[2:], start=1):
        _need(role == "UsedFuncLib" and kpos == str(i), "UsedFuncLib kpos not sequential")
        lk = _read_link(lr)
        _need(lk.type_id == "gsh" and lk.elems[1:] == [SCRIPT_DIR] and len(lk.elems) == 2, "UDF link shape")
        udfs.append(lk.elems[0])
    texts = gen.find("textInfo").find("textObj").find("texts").children
    _need(len(texts) == 2 and texts[0].get("label") == "", "non-standard <texts> (legacy envelope)")
    ap = root.find("AdditionalProperties")
    ap_names = []
    if ap is not None:
        for p in ap.children:
            _need(p.attrs == [("Applicable", "BOTH")] and p.find("PropertyValue").text == "RESOLVED",
                  "unexpected AdditionalProperties entry")
            ap_names.append(p.find("PropertyName").text)
        _need(ap_names == ADDITIONAL_PROPS[:len(ap_names)], f"AdditionalProperties {ap_names} not seen in references")
    idinfo = root.find("idInfo")
    _need(idinfo.attrs in ([("xmlns", ""), ("VID", "01")], [("VID", "01")]), "idInfo attrs")
    project = root.find("content").children[0].find("tr:MetaData").find("mappingtool").find("project")
    trans = project.find("transformation")
    m = Mapping(
        name=name,
        target=_read_link(roles[0][2]),
        source=_read_link(roles[1][2]),
        udfs=udfs,
        modif_at_long=gen.find("admInf").find("modifAtLong").text,
        text_obj_id=gen.find("textInfo").find("textObj").get("id"),
        label=texts[1].get("label"),
        additional_properties=ap_names,
        blank_xmlns=idinfo.get("xmlns") is not None,
    )
    for b in trans.children:
        if b.tag == "namespaces":
            _need(b is trans.children[-1], "<namespaces> not last in transformation")
            for p in b.children[0].children:
                m.namespaces.append((p.text, p.get("name")))
            continue
        _need(b.tag == "brick" and b.get("type") == "Dst", f"unexpected <{b.tag}> in transformation")
        _need([k for k, _ in b.attrs] == ["gid", "path", "type"], "Dst attrs")
        t = Target(b.get("path"), xy=_xy(b), gid=b.get("gid"))
        tags = [c.tag for c in b.children[1:]]
        _need(tags in (["arg", "group"], ["group", "properties"], ["arg", "properties", "group"],
                       ["arg", "group", "properties"], ["group"]), f"Dst {t.path}: children {tags}")
        if "arg" in tags:
            a = b.find("arg")
            _need([k for k, _ in a.attrs] in ([], ["from"]) and len(a.children) == 1, "Dst arg shape")
            t.expr = _read_expr(a.children[0])
            t.out = a.get("from")
        g = b.find("group")
        _need(not g.children and set(k for k, _ in g.attrs) <= {"object_uid"}, "group shape")
        t.group = g.get("object_uid")
        pr = b.find("properties")
        if pr is not None:
            _need([(p.get("name"), p.text) for p in pr.children] == [("switchedOff", "true")],
                  f"Dst {t.path}: unknown properties")
            t.disabled = True
            t.props_first = tags.index("properties") < tags.index("group")
        m.targets.append(t)
    out = render_mmap(m)
    if out != raw:
        i = next((k for k in range(min(len(out), len(raw))) if out[k] != raw[k]), min(len(out), len(raw)))
        raise FormatError(f"round-trip differs at offset {i}: ...{raw[max(0, i-80):i+40]!r} vs ...{out[max(0, i-80):i+40]!r}")
    return m


# ----------------------------------------------------------------------------- rendering
def _vd(xy):
    return E("viewData", attrs=[("x", xy[0]), ("y", xy[1])])


def _render_param(p: Param) -> Node:
    if p.table is not None:
        val = E("value", E("properties", *[E("property", attrs=[("name", k)], text=v, sc=False) for k, v in p.table]))
    elif p.calend is not None:
        val = E("value", E("calend_props", *[E(k, text=v) for k, v in p.calend]))
    else:
        val = E("value", text=p.text or None)
    return E("param", val, attrs=[("name", p.name)])


def _render_expr(x) -> Node:
    if isinstance(x, Ref):
        return E("brick", attrs=[("object_uid", x.uid)])
    if isinstance(x, Src):
        attrs = ([("context", x.context)] if x.context else []) + [("gid", x.gid)]
        attrs += ([("object_uid", x.uid)] if x.uid else []) + [("path", x.path), ("type", "Src")]
        return E("brick", _vd(x.xy), attrs=attrs, sc=False)
    attrs = [("fname", x.fname), ("fns", x.fns)] + ([("object_uid", x.uid)] if x.uid else []) + [("type", "Func")]
    kids = [_vd(x.xy)]
    for i, a in enumerate(x.args):
        aat = ([("from", a.out)] if a.out is not None else []) + ([("pin", str(i))] if i else [])
        kids.append(E("arg", _render_expr(a.expr), attrs=aat))
    if x.params is not None:
        kids.append(E("bindings", *[_render_param(p) for p in x.params]))
    return E("brick", *kids, attrs=attrs, sc=False)


def _render_target(t: Target) -> Node:
    kids = [_vd(t.xy)]
    if t.expr is not None:
        kids.append(E("arg", _render_expr(t.expr), attrs=[("from", t.out)] if t.out is not None else []))
    grp = E("group", attrs=[("object_uid", t.group)] if t.group else [])
    props = E("properties", E("property", attrs=[("name", "switchedOff")], text="true")) if t.disabled else None
    kids += [props, grp] if (props is not None and t.props_first) else ([grp] + ([props] if props is not None else []))
    return E("brick", *kids, attrs=[("gid", t.gid), ("path", t.path), ("type", "Dst")])


def _link(role: str, kpos: int, lk: Link) -> Node:
    key = E("key", *[E("elem", text=e or None, sc=False) for e in lk.elems],
            attrs=[("typeID", lk.type_id), ("version", "1.1")])
    return E("lnkRole", E("lnk", key, attrs=[("rMode", "R")]), attrs=[("kpos", str(kpos)), ("role", role)])


def _empty(tag):
    return E(tag, sc=False)


def _usernamespace() -> Node:
    # Copied from every standard reference (e.g. MAT): the fixed empty Java UDF namespace.
    fm = E("functionmodel", E("signature", attrs=[("cacheType", "0")]), _empty("name"), _empty("key"),
           _empty("tab"), _empty("title"), _empty("uiTitle"),
           E("implementation", E("javaText"), attrs=[("type", "udf")]))
    fs = E("functionstorage",
           E("key", E("key", _empty("elem"), _empty("elem"), attrs=[("typeID", "")])),
           _empty("classname"), _empty("package"), E("imports"), E("globals", E("javaText")),
           E("init", fm), E("cleanup", E("javaText")), E("usedjars"), attrs=[("version", "XI7.1")])
    return E("entry", fs, attrs=[("name", "usernamespace")])


def _libref(pos: int, script: str) -> Node:
    key = E("key", E("elem", text=script), E("elem", text=SCRIPT_DIR), E("elem"), E("elem"), E("elem"),
            attrs=[("typeID", "gsh"), ("version", "1.1")])
    ref = E("ref", E("key", key), E("functions"), attrs=[("pos", str(pos)), ("role", "UsedFuncLib")])
    return E("entry", E("libref", ref), attrs=[("name", script.rsplit(".", 1)[0])])


def _params(tag):
    p = E("tr:Parameter", E("tr:Position", text="1"), E("tr:Minoccurs", text="1"), E("tr:Maxoccurs", text="1"))
    return E(tag, p)


def _bx(m: Mapping):
    return [("xmlns", "")] if m.blank_xmlns else []


def render_mmap(m: Mapping) -> str:
    lnks = [_link("TARGET_IFR_MESS", 1, m.target), _link("SOURCE_IFR_MESS", 1, m.source)]
    lnks += [_link("UsedFuncLib", i, Link("gsh", [s, SCRIPT_DIR])) for i, s in enumerate(m.udfs, start=1)]
    for l in lnks[2:]:                 # UDF links have no empty elems; keep normal form
        pass
    generic = E("generic",
                E("admInf", _empty("modifBy"), _empty("modifAt"), E("modifAtLong", text=m.modif_at_long), E("owner")),
                E("lnks", *lnks),
                E("textInfo", E("textObj", E("texts", E("text", attrs=[("label", "")]),
                                             E("text", attrs=[("label", m.label)], sc=False),
                                             attrs=[("lang", "EN")]),
                                attrs=[("id", m.text_obj_id), ("masterL", "EN"), ("type", "0")]),
                  attrs=[("loadedL", "EN")]),
                attrs=_bx(m))
    trans_kids = [_render_target(t) for t in m.targets]
    if m.namespaces:
        trans_kids.append(E("namespaces", E("properties", *[
            E("property", attrs=[("name", uri)], text=prefix) for prefix, uri in m.namespaces])))
    project = E("project",
                E("libstorage", _usernamespace(), *[_libref(i, s) for i, s in enumerate(m.udfs, start=1)]),
                E("transformation", *trans_kids),
                E("testData", E("instances")), _empty("ViewState"), E("pcont"),
                attrs=[("version", "XI7.1")])
    trafo = E("tr:XiTrafo",
              E("tr:MetaData", E("mappingtool", project, attrs=[("version", "XI7.1")])),
              E("tr:ByteCodeJar"), E("tr:SourceStructure"), E("tr:TargetStructure"),
              E("tr:Multiplicity", text="1:1"), _params("tr:SourceParameters"), _params("tr:TargetParameters"),
              attrs=[("xmlns:tr", "urn:sap-com:xi:mapping:xitrafo")])
    kids = [
        E("idInfo", E("vc", E("clCxt", attrs=[("consider", "A")]),
                      attrs=[("caption", "LOCAL"), ("sp", "-1"), ("swcGuid", "0" * 32), ("vcType", "S")]),
          E("key", attrs=[("typeID", "XI_TRAFO"), ("version", "")]), E("version", text="1.0"),
          attrs=_bx(m) + [("VID", "01")]),
        E("documentation", E("description"), attrs=_bx(m)),
        generic,
    ]
    if m.additional_properties:
        kids.append(E("AdditionalProperties", *[
            E("Property", E("PropertyName", text=n), E("PropertyValue", text="RESOLVED"), attrs=[("Applicable", "BOTH")])
            for n in m.additional_properties], attrs=_bx(m)))
    kids.append(E("content", trafo, attrs=_bx(m)))
    return write(E("xiObj", *kids, attrs=[("xmlns", "urn:sap-com:xi")]))


def load(path) -> Mapping:
    from pathlib import Path
    p = Path(path)
    return read_mmap(p.read_bytes().decode("utf-8"), p.stem)
