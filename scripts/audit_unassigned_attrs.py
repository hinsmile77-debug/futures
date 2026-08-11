# -*- coding: utf-8 -*-
"""[MW0602 463차 후속] getattr(self, "_x", default) 중 할당부가 없는 속성 전수 조사.

실행: python scripts/audit_unassigned_attrs.py   (인자 없음, 읽기 전용)

왜 필요한가 — 이 저장소에 반복되는 결함 유형이 있다. "선언·읽기는 있는데 배선이
없어 영원히 폴백값이 쓰이는" 상태이고, 겉보기에는 구현된 것처럼 보여 문서에
"완료 ✅"로 기록되기까지 한다:
  · `allow_new_entry`      선언만, 진입 차단에 미배선          (462차)
  · `_entry_horizon_pre`   read 2 / write 0 → MetaGate 항상 1m (463차 C3)
  · `_entry_horizon`       read 1 / write 0 → SHAP 표시 고정    (463차 C4)
  · FP-CRITICAL PSI=0.0    학습분포 저장 함수 미호출로 2개월 미발동 (303차)
이 스크립트는 그 유형을 기계적으로 훑는다.

⚠ 오탐 억제를 위해 세 패턴을 인정한다 — 초안이 이 셋 때문에 7건 중 6건을 잘못 올렸다:
  ① mixin        모듈레벨 `def _ts_xxx(self, ...)` (나중에 클래스에 바인딩)
  ② 교차객체     `system._futures_code = code` (broker_runtime_service.py)
  ③ 계산된 이름  `setattr(self, _attr + "_label", v)` (main_dashboard.py L2 라벨)
그래도 남는 것은 수동 확인이 필요하다 — 이 도구는 후보를 좁힐 뿐 판정하지 않는다.


C3(_entry_horizon_pre)·C4(_entry_horizon)와 같은 유형 —
placeholder로 도입됐으나 write가 한 번도 배선되지 않아 영구히 폴백값이 쓰이는 결함.

판정 규칙:
  read  = getattr(self, "name", ...) / getattr(self, 'name')
  write = self.name = / self.name: T = / self.name += / setattr(self, "name", ...)
          / for self.name in / with ... as self.name
  클래스 단위로 집계하고, 상속 부모가 같은 파일에 있으면 부모 write도 인정한다.
  (부모가 다른 파일이면 'BASE_EXTERNAL'로 표시 — 오탐 가능성 고지)
"""
import ast
import io
import os
import sys

# PC별 경로 하드코딩 금지 — 스크립트 위치에서 저장소 루트를 동적 해석한다.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔴 **py37_32에서 돌리면 조용히 "없음"이 나온다 — 반드시 py310_64로 실행할 것.**
# 3.7의 `ast.parse()`는 문자열 리터럴을 `ast.Str`로 만들지만 이 스크립트는
# `ast.Constant`로 검사한다(3.8+ 표현). 그래서 getattr 이름 인자를 하나도 못 잡아
# read 0건 → "없음"으로 끝난다. 실측: py37_32에서 억제 0건 / 발견 0건,
# 같은 코드가 py310_64에서는 억제 16건 / 발견 1건.
# 이 도구가 잡으려는 결함(“구현된 것처럼 보이지만 실은 안 도는 코드”)을 도구 자신이
# 저지르는 셈이라 조용한 폴백 대신 **즉시 중단**한다.
if sys.version_info < (3, 9):
    sys.stderr.write(
        "[audit_unassigned_attrs] Python 3.9+ 필요 (현재 %d.%d).\n"
        "  py37_32에서는 ast.Constant 미생성으로 결과가 항상 0건이 되어 오보한다.\n"
        "  실행: <py310_64>/python.exe scripts/audit_unassigned_attrs.py\n"
        % (sys.version_info[0], sys.version_info[1])
    )
    sys.exit(2)
SKIP_DIRS = {".git", "__pycache__", "_archive", "node_modules", ".venv", "venv"}


class ClassScan(ast.NodeVisitor):
    def __init__(self):
        self.reads = {}    # name -> [(lineno, default_repr)]
        self.writes = set()

    # ---- writes ----
    def visit_Assign(self, node):
        for t in node.targets:
            self._mark_write(t)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self._mark_write(node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self._mark_write(node.target)
        self.generic_visit(node)

    def visit_For(self, node):
        self._mark_write(node.target)
        self.generic_visit(node)

    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars is not None:
                self._mark_write(item.optional_vars)
        self.generic_visit(node)

    def _mark_write(self, t):
        if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
            self.writes.add(t.attr)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                self._mark_write(e)

    # ---- reads + setattr ----
    def visit_Call(self, node):
        f = node.func
        if isinstance(f, ast.Name) and f.id == "getattr" and len(node.args) >= 2:
            obj, name = node.args[0], node.args[1]
            if (isinstance(obj, ast.Name) and obj.id == "self"
                    and isinstance(name, ast.Constant) and isinstance(name.value, str)):
                dflt = "<없음>"
                if len(node.args) >= 3:
                    try:
                        dflt = ast.unparse(node.args[2])
                    except Exception:
                        dflt = "?"
                self.reads.setdefault(name.value, []).append((node.lineno, dflt))
        if isinstance(f, ast.Name) and f.id == "setattr" and len(node.args) >= 2:
            obj, name = node.args[0], node.args[1]
            if (isinstance(obj, ast.Name) and obj.id == "self"
                    and isinstance(name, ast.Constant) and isinstance(name.value, str)):
                self.writes.add(name.value)
        self.generic_visit(node)


def scan_file(path):
    try:
        src = io.open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except Exception:
        return []
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            s = ClassScan()
            for ch in node.body:
                s.visit(ch)
            bases = []
            for b in node.bases:
                try:
                    bases.append(ast.unparse(b))
                except Exception:
                    pass
            classes[node.name] = (s, bases, node.lineno)

    # [보완] mixin 패턴 — 모듈레벨 `def _ts_xxx(self, ...)` 은 나중에 클래스에 붙는다.
    # 이걸 빼면 main.py의 `_ts_*` 함수군에 있는 read/write를 통째로 놓친다
    # (463차 후속 초안이 실제로 _last_exit_ts 등을 오탐으로 올렸다).
    # 파일 단위 하나의 가상 버킷으로 모아 모든 클래스의 write에 합산한다.
    mixin = ClassScan()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args.args
            if args and args[0].arg == "self":
                mixin.visit(node)
    if mixin.reads or mixin.writes:
        classes["<mixin:%s>" % os.path.basename(path)] = (mixin, [], 0)
    # mixin write는 같은 파일 모든 클래스에 인정 (실제로 그 클래스에 바인딩된다)
    for _cn, (_s, _b, _l) in classes.items():
        if not _cn.startswith("<mixin:"):
            _s.writes |= mixin.writes

    out = []
    for cname, (s, bases, cline) in classes.items():
        # 같은 파일 내 부모 클래스의 write 합산
        inherited = set()
        ext_base = False
        for b in bases:
            root = b.split(".")[0].split("[")[0]
            if root in classes:
                inherited |= classes[root][0].writes
            elif root not in ("object",):
                ext_base = True
        for attr, sites in s.reads.items():
            if attr in s.writes or attr in inherited:
                continue
            out.append({
                "file": os.path.relpath(path, ROOT),
                "cls": cname,
                "attr": attr,
                "sites": sites,
                "ext_base": ext_base,
                "bases": bases,
            })
    return out


def _repo_dynamic_writes():
    """저장소 전체에서 동적/교차객체 할당으로 생기는 속성명 집합.

    이 셋에 걸리면 '할당 없음'으로 단정할 수 없다 — 초안이 놓친 3가지 패턴이다:
      ① 교차객체    `system._futures_code = code` (broker_runtime_service.py)
      ② 계산된 이름 `setattr(self, _attr + "_label", v)` (main_dashboard.py L2 라벨)
      ③ 문자열 접미  위 ②의 접미사만 아는 경우
    """
    names, suffixes = set(), set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                tree = ast.parse(io.open(p, encoding="utf-8").read())
            except Exception:
                continue
            for node in ast.walk(tree):
                # ① 임의 객체에 대한 속성 할당
                if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in tgts:
                        if isinstance(t, ast.Attribute):
                            names.add(t.attr)
                # ②③ setattr 계산 이름 — 상수 접미사만 추출
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == "setattr" and len(node.args) >= 2):
                    nm = node.args[1]
                    if isinstance(nm, ast.Constant) and isinstance(nm.value, str):
                        names.add(nm.value)
                    elif isinstance(nm, ast.BinOp) and isinstance(nm.op, ast.Add):
                        for side in (nm.left, nm.right):
                            if isinstance(side, ast.Constant) and isinstance(side.value, str):
                                suffixes.add(side.value)
    return names, suffixes


def main():
    findings = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                findings.extend(scan_file(os.path.join(dirpath, fn)))

    dyn_names, dyn_suffixes = _repo_dynamic_writes()
    kept, suppressed = [], []
    for f in findings:
        a = f["attr"]
        if a in dyn_names or any(a.endswith(s) for s in dyn_suffixes if s):
            suppressed.append(f)
        else:
            kept.append(f)
    findings = kept
    print("동적/교차객체 할당으로 억제된 오탐: %d건 (%s)" % (
        len(suppressed), ", ".join(sorted({x["attr"] for x in suppressed})) or "-"))

    # 전 저장소에서 self.<attr> = 형태가 아예 없는지 교차 확인(동적 배선 오탐 줄이기)
    print("=" * 78)
    print("getattr(self, ...) read 있으나 같은 클래스(+동일파일 부모)에 write 없음")
    print("=" * 78)
    if not findings:
        print("없음")
        return
    findings.sort(key=lambda x: (x["file"], x["cls"], x["attr"]))
    for f in findings:
        flag = "  ⚠상속외부" if f["ext_base"] else ""
        print("\n[%s] %s.%s%s" % (f["file"], f["cls"], f["attr"], flag))
        for ln, d in f["sites"]:
            print("    read L%-6d default=%s" % (ln, d))
        if f["ext_base"]:
            print("    bases=%s" % f["bases"])
    print("\n총 %d건" % len(findings))


if __name__ == "__main__":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
