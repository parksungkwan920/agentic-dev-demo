# 05_operate · 인도 상태

> 아래 표는 완성본(reference target)의 인도 상태입니다.
>
> **현재 learning 워크스페이스 실제 상태 (STEP 2 · 도메인 구역):** 롤아웃은 일어나지
> 않았습니다. 도메인 구역만 구현돼 도메인 단위 14/14 가 green 이고(`04_verify/10_test/
> proof_evidence.md`), 전체 `./gradlew test`·E2E·bootRun·배포는 다음 청크(web + checkout)
> 이후로 보류된 상태입니다. 이 단계에서는 배포 대상이 없으므로 운영 베이스라인을 갱신하지
> 않습니다.

| 항목 | 상태 |
| --- | --- |
| 컴파일 | ✅ BUILD SUCCESSFUL (JDK 17 · Gradle 8.5) |
| 단위 테스트 | ✅ 14/14 |
| E2E 테스트 | ✅ 9/9 |
| 합계 | ✅ 23/23 PASS |
| DDD 경계 게이트 | ✅ run_arch_check.py PASS |
| 컨텍스트 | ✅ 6개 (catalog·inventory·cart·ordering·payment·checkout) |
| API 엔드포인트 | ✅ 21개 |

## 남은 운영 과제 (데모 범위 밖)

- 영속 저장소(JPA + DB) 전환
- 실제 PG 게이트웨이 연동
- 분산 멱등 저장소
- 컨테이너 이미지·CI 파이프라인 (대규모 프로젝트 세션에서 별도 다룸)
