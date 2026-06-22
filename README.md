# agentic-dev-demo

SDD × Claude Code 강의의 **클론-앤-런 데모 타깃**입니다. 각 데모는 **자바(Spring Boot)와 파이썬 두 버전**으로,
각 언어 아래에 **init · learning · complete** 세 단계로 준비돼 있어, 원하는 언어를 골라 클론 즉시 실습할 수 있습니다.

> 모든 데이터는 강의용 **가상**입니다. 실재 기관·시스템·개인정보·실명은 없습니다.

## 폴더 구조

```
<데모>/<언어>/<단계>
   예) auth/java/complete,  auth/python/learning,  finance/java/init
```

- **언어**: `java`(Spring Boot · Gradle, JDK 17), `python`(표준 라이브러리 + pytest).
- **단계**: `init`(시작 골격), `learning`(직접 채우는 실습본), `complete`(정답·완성본).
- complete 는 클론 즉시 빌드·테스트가 통과합니다. learning 에서 출발해 complete 로 가는 것이 실습입니다.

## 데모 목록

| 데모 | 예제 | 언어 | 강의 |
| --- | --- | --- | --- |
| `tetris/` | 줄 삭제 규칙으로 'SDD가 무엇을 적는가'를 연습하는 핸즈온(도메인 지식 불필요) | java · python | S02 |
| `sdd-contrast/` | 명세 없이(vibe) vs 명세대로(SDD)를 같은 채점기로 대조하는 핸즈온 | java · python | S03 |
| `auth/` | 회원가입 OTP 서비스 | java · python | S05·07·08·09·11·12·16 |
| `ecommerce/` | 이커머스 모놀리식 DDD(상품·재고·장바구니·주문·결제·체크아웃) | java · python | S10 |
| `library/` | 레거시 도서관 strangler 전환 | java | S13 |
| `finance/` | 금융·공공 대규모(MyLink) 동의 후 전자민원 자동 발급 | java · python | 금융·공공 데모 |
| `realestate/` | 부동산 실거래가 Spring Cloud MSA(시세 추정 analytics 포함) | java · python | S15·16 |

## 클론-앤-런

### 자바 (Spring Boot · Gradle)

```bash
git clone https://github.com/say828/agentic-dev-demo.git
cd agentic-dev-demo/auth/java/complete    # 또는 learning 에서 시작

./gradlew build -x test    # contract: build
./gradlew test             # contract: proof
./gradlew uiParity         # contract: verify_dev (auth·finance)
```

JDK 17 만 있으면 Gradle Wrapper(`./gradlew`)가 의존성을 모두 처리합니다. 별도 설치가 없습니다.

### 파이썬 (표준 라이브러리 + pytest)

```bash
cd agentic-dev-demo/auth/python/complete

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # pytest (테스트에만 필요)
python3 -m compileall -q server           # contract: build
python3 proof/run_proof.py                # contract: proof  (auth 10/10 · finance 14/14)
```

도메인 코드는 표준 라이브러리만 씁니다. pytest 는 테스트 실행에만 필요합니다.
각 단계 폴더의 `.agentic-dev/contract.json` 에 `build · proof · verify_dev` 명령이 그대로 들어 있습니다.

### sdd-contrast (S03 핸즈온)

명세 유무를 직접 대조하는 경량 데모입니다. 학습자가 Claude Code로 구현을 두 번(명세 없이 → 명세대로)
만들어 같은 채점기로 점수를 비교합니다.

```bash
cd agentic-dev-demo/sdd-contrast/python/complete   # 파이썬 표준 라이브러리만
python3 grade.py        # 학습자가 만든 구현 채점 (라운드 1 → 1/4, 라운드 2 → 4/4)
python3 contrast.py     # 강사 폴백: vibe 1/4 vs SDD 4/4 결정적 재현
```

## 구조 (각 단계 폴더)

- `.agentic-dev/contract.json` : build·proof·deploy_dev·verify_dev 명령
- `.claude/skills/sdd`·`.codex/skills/sdd` : 적용된 SDD 스킬
- 자바: `src/main/java` 도메인 · `src/test/java` proof 게이트(JUnit) · `build.gradle`·`gradlew`
- 파이썬: `server/` 도메인 · `tests/` proof 게이트(pytest) · `proof/run_proof.py`
- `sdd/` : SDD 5단계 산출물(`00_sources → 01_planning → 02_plan → 03_build → 04_verify → 05_operate → 99_toolchain`)

## 경계

브라우저(Playwright exactness)·docker compose 부팅·GitHub Action 배포는 강사 환경에서 다룹니다.
이 repo 는 백엔드 로직을 **결정적 테스트**(자바 JUnit · 파이썬 pytest)로, 화면 정합을 **HTML 스냅샷 parity**로,
배포를 **로컬 스텁**으로 대체해 어디서든 클론 즉시 검증되도록 했습니다.
