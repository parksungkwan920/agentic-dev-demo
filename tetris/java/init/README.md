# 테트리스 (자바) · 줄 삭제 핸즈온

요구사항 원문(`sdd/00_sources/tetris.md`)을 EARS 명세(`sdd/01_planning/tetris_spec.md`)로,
다시 할 일(`sdd/02_plan/tetris_todos.md`)로 내린 뒤, `Board.clearFullLines` 를 구현합니다.

```bash
./gradlew build -x test   # build
./gradlew test            # proof (AC-3·AC-4)
```

`init/` 에서 시작해 `clearFullLines` 를 명세대로 채우면 테스트가 통과합니다. `complete/` 는 정답입니다.
JDK 17 만 있으면 Gradle Wrapper가 의존성을 처리합니다.
