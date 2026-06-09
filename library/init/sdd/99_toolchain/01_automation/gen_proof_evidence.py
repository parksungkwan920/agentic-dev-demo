# -*- coding: utf-8 -*-
"""생성기(generator): Gradle 테스트 결과에서 proof_evidence.md 를 자동 생성합니다.

toolchain 세 갈래 중 '생성기' 역할을 담당합니다. 사람이 테스트 결과를 보고
손으로 증거 문서를 작성하는 대신, 이 스크립트가 Gradle 이 남긴 JUnit XML 을
파싱해 sdd/04_verify/10_test/proof_evidence.md 를 만들어냅니다.

agentic-core 의 spec_asset_builder.py 패턴을 따라, 입력(테스트 결과 XML) →
출력(검증 증거 마크다운)의 단방향 흐름으로 동작합니다. 이 스크립트가 생성한
파일이 SDD 에서 '코드가 통과시켰다'의 공식 증거가 됩니다.

사용법:
    ./gradlew test                          # 먼저 테스트를 실행합니다
    python3 sdd/99_toolchain/01_automation/gen_proof_evidence.py
    python3 sdd/99_toolchain/01_automation/gen_proof_evidence.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = ROOT / "build/test-results/test"
OUT_FILE = ROOT / "sdd/04_verify/10_test/proof_evidence.md"


# ── XML 파서 ──────────────────────────────────────────────────────────────────

def _class_short(classname: str) -> str:
    return classname.split(".")[-1]


def parse_results(results_dir: Path) -> list[dict]:
    """JUnit XML 파일들을 읽어 클래스별 통계를 돌려줍니다."""
    classes: list[dict] = []
    for xml_file in sorted(results_dir.glob("TEST-*.xml")):
        try:
            root = ET.parse(xml_file).getroot()
        except ET.ParseError:
            continue
        classname = root.get("name", xml_file.stem.replace("TEST-", ""))
        tests    = int(root.get("tests",    0))
        failures = int(root.get("failures", 0))
        errors   = int(root.get("errors",   0))
        skipped  = int(root.get("skipped",  0))
        passed   = tests - failures - errors - skipped
        cases = []
        for tc in root.findall("testcase"):
            status = "PASS"
            if tc.find("failure") is not None:
                status = "FAIL"
            elif tc.find("error") is not None:
                status = "ERROR"
            elif tc.find("skipped") is not None:
                status = "SKIP"
            cases.append({
                "name": tc.get("name", ""),
                "display": tc.get("name", tc.get("classname", "")),
                "status": status,
            })
        classes.append({
            "classname": classname,
            "short": _class_short(classname),
            "tests": tests,
            "passed": passed,
            "failures": failures,
            "errors": errors,
            "skipped": skipped,
            "cases": cases,
        })
    return classes


# ── 마크다운 생성기 ────────────────────────────────────────────────────────────

def render(classes: list[dict]) -> str:
    total      = sum(c["tests"]    for c in classes)
    total_pass = sum(c["passed"]   for c in classes)
    total_fail = sum(c["failures"] + c["errors"] for c in classes)

    status_line = "BUILD SUCCESSFUL" if total_fail == 0 else "BUILD FAILED"
    # 통합/E2E 여부는 짧은 이름이 아니라 전체 패키지명으로 판정합니다. acceptance·e2e 패키지의
    # @SpringBootTest 는 모두 통합 테스트입니다(AllNewModeTest 가 단위로 잘못 분류되지 않게).
    def _is_integration(c):
        name = c["classname"].lower()
        return "e2e" in name or "acceptance" in name
    e2e_classes  = [c for c in classes if _is_integration(c)]
    unit_classes = [c for c in classes if not _is_integration(c)]

    lines: list[str] = []
    lines += [
        "# 04_verify · proof 증빙",
        "",
        "> **생성기 산출물입니다.** `gen_proof_evidence.py` 가 Gradle JUnit XML 에서 자동 생성했습니다.",
        "> 이 파일은 'SDD가 코드로 통과시켰다'의 공식 증거입니다. 손으로 수정하지 않습니다.",
        "",
        "## 요약",
        "",
        "```",
        f"{status_line}",
        f"total tests = {total} · passed = {total_pass} · failed = {total_fail} · "
        f"errors = {sum(c['errors'] for c in classes)}",
    ]

    for c in classes:
        lines.append(f"{c['short']:<22}{c['passed']}/{c['tests']}")

    lines += [
        "```",
        "",
    ]

    if e2e_classes:
        lines += [
            f"## E2E 시나리오 ({sum(c['tests'] for c in e2e_classes)}개)",
            "",
            "| 테스트 이름 | 결과 |",
            "| --- | --- |",
        ]
        for c in e2e_classes:
            for case in c["cases"]:
                icon = "✅" if case["status"] == "PASS" else "❌"
                lines.append(f"| {case['display']} | {icon} {case['status']} |")
        lines.append("")

    if unit_classes:
        lines += [
            f"## 단위 테스트 ({sum(c['tests'] for c in unit_classes)}개)",
            "",
            "| 클래스 | 통과 | 실패 |",
            "| --- | --- | --- |",
        ]
        for c in unit_classes:
            lines.append(f"| {c['short']} | {c['passed']} | {c['failures'] + c['errors']} |")
        lines.append("")

    lines += [
        "## 게이트 판정",
        "",
        f"- 테스트 게이트: `./gradlew test` → **{status_line}**",
        f"- 전체 {total}개 중 {total_pass}개 통과, {total_fail}개 실패.",
        "",
    ]

    if total_fail == 0:
        lines.append("> **통과** — 모든 AC 가 JUnit 으로 검증되었습니다.")
    else:
        lines.append("> **실패** — 실패한 케이스를 수정한 뒤 다시 실행합니다.")

    lines.append("")
    return "\n".join(lines)


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Gradle 테스트 결과 → proof_evidence.md 생성기")
    parser.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 내용만 출력합니다")
    parser.add_argument("--results-dir", default=str(RESULTS_DIR),
                        help=f"JUnit XML 디렉터리 (기본: {RESULTS_DIR.relative_to(ROOT)})")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"[gen_proof_evidence] 테스트 결과 디렉터리가 없습니다: {results_dir}", file=sys.stderr)
        print("  먼저 ./gradlew test 를 실행해 주세요.", file=sys.stderr)
        return 1

    classes = parse_results(results_dir)
    if not classes:
        print(f"[gen_proof_evidence] XML 결과 파일을 찾을 수 없습니다: {results_dir}", file=sys.stderr)
        return 1

    content = render(classes)

    if args.dry_run:
        print(content)
        print("[dry-run] 실제 파일을 쓰지 않았습니다.")
        return 0

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(content, encoding="utf-8")
    total      = sum(c["tests"]  for c in classes)
    total_fail = sum(c["failures"] + c["errors"] for c in classes)
    print(f"[gen_proof_evidence] {total}개 테스트 결과 → {OUT_FILE.relative_to(ROOT)}")
    print(f"  {'PASS' if total_fail == 0 else 'FAIL'}: 통과 {total - total_fail}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
