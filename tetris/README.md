# tetris · SDD 줄 삭제 핸즈온 (02강)

도메인 지식이 필요 없는 예제로, "요구사항 원문 → EARS 명세 → 할 일 → 통과하는 테스트"라는
SDD 한 흐름만 연습합니다. 누구나 규칙을 알기에 'SDD가 무엇을 적는가'에만 집중할 수 있습니다.

## 구조

```
tetris/<언어>/<단계>     예) tetris/java/init,  tetris/python/complete
```
- 언어: `java`(Gradle·JDK17), `python`(표준 라이브러리, pytest 선택)
- 단계: `init`(실습 시작점, 핵심 구현 비움) · `learning`(힌트 포함) · `complete`(정답)
- 공통 명세: 각 단계의 `sdd/00_sources·01_planning·02_plan` (요구원문·EARS·할 일)

## 실습 흐름

1. `sdd/00_sources/tetris.md` 의 요구 원문을 읽습니다.
2. `sdd/01_planning/tetris_spec.md` 의 EARS 수용기준(AC-3 줄 삭제, AC-4 다중 삭제)을 확인합니다.
3. `init/` 에서 줄 삭제 로직(`clearFullLines` / `clear_full_lines`)을 명세대로 구현합니다.
4. 자바는 `./gradlew test`, 파이썬은 `python3 run_proof.py` 로 통과를 확인합니다. 막히면 `complete/` 와 비교합니다.
