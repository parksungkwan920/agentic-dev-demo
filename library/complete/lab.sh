#!/usr/bin/env bash
# 레거시 strangler 전환 실습 하네스: 실습을 몇 번이든 같은 결과로 반복(멱등)하게 만든다.
#
#   ./lab.sh reset    깨끗한 시작 상태로 되돌린다. springboot 신규 구현과 실습 중 생성된
#                     산출물(스펙·증거)을 지우고, migration.properties 를 세 모듈 모두 legacy 로 돌린다.
#                     legacy 코드·테스트(수용기준)·라우터·게이트·toolchain 은 그대로 둔다.
#   ./lab.sh solve    ../complete 의 신규 구현을 src 아래 springboot 폴더로 복원하고,
#                     세 모듈을 모두 new 로 전환한다. 서브에이전트가 막혔을 때의 폴백이자 완성본 확인용.
#   ./lab.sh verify   strangler 게이트 + gradle 수용기준 테스트를 돌린다.
#   ./lab.sh status   현재 전환 상태(모듈별 legacy|new, springboot 구현 수)를 보여준다.
#
# reset/solve 는 실습 사본(learning)에서만 동작한다. complete 는 완성본 레퍼런스이자 solve 의
# 정답 소스이므로, complete 안에서 reset/solve 를 막아 정답이 지워지지 않게 한다.
# 어느 상태에서든 수용기준(AC-1 한도 5권 · AC-2 연체 거부)은 통과해야 한다.
# reset(legacy) → solve(new) → reset 을 반복해도 매번 같은 결과로 수렴한다.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
SB="src/main/java/kr/elice/library/springboot"
SOL="../complete/src/main/java/kr/elice/library/springboot"
PROPS="src/main/resources/migration.properties"
SPEC_DIR="sdd/01_planning/01_feature"
PROOF="sdd/04_verify/10_test/proof_evidence.md"
: "${JAVA_HOME:=$(/usr/libexec/java_home -v 17 2>/dev/null || true)}"
export JAVA_HOME

# reset/solve 는 complete 레퍼런스에서 실행하면 정답이 지워지므로 막는다.
guard_practice() {
  if [ "$(basename "$HERE")" = "complete" ]; then
    echo "[$1] complete 는 완성본 레퍼런스입니다. reset/solve 는 learning 에서 실행하세요." >&2
    exit 2
  fi
}

write_modes() {  # $1 = legacy | new
  cat > "$PROPS" <<EOF
# strangler 라우팅 상태입니다. 모듈별로 legacy 또는 new 를 가리킵니다.
# 실습에서 한 모듈을 전환할 때마다 해당 값을 legacy 에서 new 로 바꿉니다.
# 라우터(platform/CatalogRouter·LoanRouter)와 전환 게이트(run_strangler_check.py)가 같은 파일을 읽습니다.
module.books=$1
module.members=$1
module.loans=$1
EOF
}

reset() {
  guard_practice reset
  mkdir -p "$SB"
  find "$SB" -name 'New*.java' -delete
  # 실습 중 생성기가 만든 산출물도 함께 지워 매 회차 같은 시작 상태로 수렴시킨다.
  rm -f "$SPEC_DIR"/book.md "$SPEC_DIR"/member.md "$SPEC_DIR"/loan.md
  rm -f "$PROOF"
  rm -rf build/test-results
  # 생성으로 만들어진 빈 디렉터리는 정리해 init 과 동일한 형태로 맞춘다(비었을 때만).
  rmdir "$SPEC_DIR" sdd/01_planning 2>/dev/null || true
  write_modes legacy
  echo "[reset] springboot 신규 구현 + 생성 산출물(스펙·증거) 제거 + 세 모듈 모두 legacy 로 되돌림."
  echo "        남아 있는 것: legacy 코드, src/test (수용기준), 라우터, 게이트, toolchain."
  status
}

solve() {
  guard_practice solve
  if [ ! -d "$SOL" ]; then echo "[solve] ../complete 폴더를 찾을 수 없습니다: $SOL" >&2; exit 1; fi
  mkdir -p "$SB"
  cp "$SOL"/New*.java "$SB"/
  write_modes new
  echo "[solve] 정답 신규 구현 복원 + 세 모듈 모두 new 로 전환."
  status
}

status() {
  echo "[status] 모듈 라우팅:"
  grep -E '^module\.' "$PROPS" | sed 's/^/         /'
  local n; n=$(find "$SB" -name '*.java' 2>/dev/null | wc -l | tr -d ' ')
  echo "[status] springboot 신규 구현: ${n}개 .java"
}

verify() {
  echo "[verify] 1/2 strangler 게이트"
  python3 sdd/99_toolchain/01_automation/run_strangler_check.py | tail -2
  echo "[verify] 2/2 gradle 수용기준 테스트"
  ./gradlew clean test --console=plain -q
  echo "[verify] 통과: 수용기준 3개(AC-1·AC-2·정상흐름) green"
}

case "${1:-}" in
  reset)  reset ;;
  solve)  solve ;;
  verify) verify ;;
  status) status ;;
  *) echo "사용법: ./lab.sh {reset|solve|verify|status}"; exit 2 ;;
esac
