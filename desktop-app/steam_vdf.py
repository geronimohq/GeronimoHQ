"""Careful reader and editor for Steam's text VDF files (localconfig.vdf, loginusers.vdf).

Why this exists: the old code used regular expressions over the whole file. That replaced the launch options of EVERY game, could read another
game's options, and broke on quotes or backslashes. This module reads the real block structure and edits only the one value it is asked to,
leaving the rest of the file byte for byte as Steam wrote it.
"""
import glob
import os
import re
from typing import Dict, List, Optional, Tuple

STEAMID64_BASE = 76561197960265728          # SteamID64 minus this number = the folder name in steam/userdata

APPS_PATH = ("UserLocalConfigStore", "Software", "Valve", "Steam", "apps")


class VdfError(ValueError):
    pass


class _Tok:
    __slots__ = ("kind", "val", "start", "end")

    def __init__(self, kind: str, val: str, start: int, end: int):
        self.kind, self.val, self.start, self.end = kind, val, start, end


class Node:
    """One key. Either a string value (vstart/vend span the quoted value) or a block (open/close are the braces' offsets)."""

    def __init__(self, key: str):
        self.key = key
        self.kstart = -1
        self.value: Optional[str] = None
        self.vstart = self.vend = -1
        self.children: Optional[List["Node"]] = None
        self.open = self.close = -1

    def child(self, key: str) -> Optional["Node"]:
        for c in self.children or []:
            if c.key.lower() == key.lower():
                return c
        return None


def escape(value: str) -> str:
    """How Steam writes a string value: backslash and quote are escaped, line breaks never appear."""
    return value.replace("\r", " ").replace("\n", " ").replace("\\", "\\\\").replace('"', '\\"')


def _tokenize(text: str) -> List[_Tok]:
    toks: List[_Tok] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in " \t\r\n":
            i += 1
        elif c == "/" and text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
        elif c == "{" or c == "}":
            toks.append(_Tok(c, "", i, i + 1))
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    nxt = text[j + 1]
                    buf.append({"n": "\n", "t": "\t", "\\": "\\", '"': '"'}.get(nxt, "\\" + nxt))
                    j += 2
                else:
                    buf.append(text[j])
                    j += 1
            if j >= n:
                raise VdfError("unterminated quoted string")
            toks.append(_Tok("str", "".join(buf), i, j + 1))
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in " \t\r\n{}\"":
                j += 1
            toks.append(_Tok("str", text[i:j], i, j))     # unquoted word
            i = j
    return toks


def parse(text: str) -> List[Node]:
    toks = _tokenize(text)
    pos = 0

    def block() -> List[Node]:
        nonlocal pos
        nodes: List[Node] = []
        while pos < len(toks):
            t = toks[pos]
            if t.kind == "}":
                return nodes
            if t.kind != "str":
                raise VdfError("unexpected brace")
            node = Node(t.val)
            node.kstart = t.start
            pos += 1
            if pos >= len(toks):
                raise VdfError("key without a value")
            nxt = toks[pos]
            if nxt.kind == "str":
                node.value, node.vstart, node.vend = nxt.val, nxt.start, nxt.end
                pos += 1
            elif nxt.kind == "{":
                node.open = nxt.start
                pos += 1
                node.children = block()
                if pos >= len(toks) or toks[pos].kind != "}":
                    raise VdfError("block is not closed")
                node.close = toks[pos].start
                pos += 1
            else:
                raise VdfError("unexpected closing brace")
            nodes.append(node)
        return nodes

    root = block()
    if pos != len(toks):
        raise VdfError("trailing data after the root block")
    return root


def _find(nodes: List[Node], key: str) -> Optional[Node]:
    for n in nodes:
        if n.key.lower() == key.lower():
            return n
    return None


def _apps_node(root: List[Node]) -> Optional[Node]:
    cur_nodes = root
    node: Optional[Node] = None
    for key in APPS_PATH:
        node = _find(cur_nodes, key)
        if node is None or node.children is None:
            return None
        cur_nodes = node.children
    return node


def get_launch_options(text: str, appid: str = "730") -> Optional[str]:
    """The launch options of one game, or None when that game has no LaunchOptions entry. Raises VdfError for a file it cannot read."""
    apps = _apps_node(parse(text))
    if apps is None:
        raise VdfError("apps block not found")
    app = apps.child(appid)
    if app is None or app.children is None:
        return None
    lo = app.child("LaunchOptions")
    return lo.value if lo is not None and lo.value is not None else None


def set_launch_options(text: str, new_options: str, appid: str = "730") -> str:
    """Returns the text with ONLY this game's LaunchOptions set. Other games and every other byte stay as they were."""
    apps = _apps_node(parse(text))
    if apps is None:
        raise VdfError("apps block not found in Steam's config")
    val = escape((new_options or "").strip())
    app = apps.child(appid)
    if app is not None and app.children is not None:
        lo = app.child("LaunchOptions")
        if lo is not None and lo.value is not None:
            return text[:lo.vstart] + f'"{val}"' + text[lo.vend:]
        indent = _indent_of(text, app.children[0].kstart) if app.children else "\t\t\t\t\t"
        ins = f'\n{indent}"LaunchOptions"\t\t"{val}"'
        return text[:app.open + 1] + ins + text[app.open + 1:]
    if app is not None:                                          # "730" "something" (not a block): refuse rather than guess
        raise VdfError("the 730 entry is not a block")
    indent = "\t\t\t\t"
    ins = f'\n{indent}"{appid}"\n{indent}{{\n{indent}\t"LaunchOptions"\t\t"{val}"\n{indent}}}'
    return text[:apps.open + 1] + ins + text[apps.open + 1:]


def _indent_of(text: str, pos: int) -> str:
    line_start = text.rfind("\n", 0, max(pos, 0)) + 1
    m = re.match(r"[ \t]*", text[line_start:])
    return m.group(0) if m and m.group(0) else "\t\t\t\t\t"


def most_recent_user_id(steam_path: str) -> Optional[int]:
    """Steam's account number (the userdata folder name) of the account that logged in last, from config/loginusers.vdf."""
    try:
        path = os.path.join(steam_path, "config", "loginusers.vdf")
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            root = parse(fh.read())
        users = _find(root, "users")
        if users is None or users.children is None:
            return None
        newest = None
        for u in users.children:
            if not re.fullmatch(r"\d{17}", u.key) or u.children is None:
                continue
            flag = u.child("MostRecent")
            if flag is not None and flag.value == "1":
                return int(u.key) - STEAMID64_BASE
            ts = u.child("Timestamp")
            if ts is not None and (ts.value or "").isdigit():
                if newest is None or int(ts.value) > newest[0]:
                    newest = (int(ts.value), int(u.key) - STEAMID64_BASE)
        return newest[1] if newest else None
    except (OSError, VdfError):
        return None


def localconfig_path(steam_path: Optional[str]) -> Optional[str]:
    """localconfig.vdf of the account that logged in last; falls back to the most recently changed one."""
    if not steam_path or not os.path.isdir(steam_path):
        return None
    uid = most_recent_user_id(steam_path)
    if uid is not None:
        p = os.path.join(steam_path, "userdata", str(uid), "config", "localconfig.vdf")
        if os.path.isfile(p):
            return p
    found = glob.glob(os.path.join(steam_path, "userdata", "*", "config", "localconfig.vdf"))
    return max(found, key=os.path.getmtime) if found else None
