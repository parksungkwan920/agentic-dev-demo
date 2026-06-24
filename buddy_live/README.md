# 버디버디 (Buddy Live)

SDD(Specification-Driven Development) 방법론으로 구현한 로컬 네트워크 실시간 채팅 앱

## 실행 방법

```bash
cd buddy_live
npm install
npm run dev
```

서버 시작 시 터미널에 접속 URL이 출력됩니다.

```
🚀 버디버디 서버 시작!
─────────────────────────────────
  http://localhost:3000
  http://192.168.x.x:3000   ← 같은 네트워크 친구는 이 주소로 접속
─────────────────────────────────
```

## 사용 방법

1. 한 컴퓨터에서 `npm run dev` 실행
2. 같은 Wi-Fi/네트워크의 두 기기에서 `http://[서버IP]:3000` 접속
3. 각자 닉네임 입력 후 입장
4. `+` 버튼 → 닉네임 검색 → 버디 추가
5. 상대방이 수락하면 채팅 가능

## SDD 아키텍처

```
src/specs/          ← 명세서 (단일 진실 소스)
  user.spec.ts      ← 유저 도메인 계약
  buddy.spec.ts     ← 버디 관계 계약  
  message.spec.ts   ← 메시지 도메인 계약
  socket-events.spec.ts ← 소켓 이벤트 전체 계약

src/schemas/        ← Zod 런타임 verify 스키마
  user.schema.ts
  message.schema.ts

src/lib/verify.ts   ← SDD verify() 유틸리티
```

### verify() 사용 예시

```typescript
import { verify } from '@/lib/verify'
import { messageContentSchema } from '@/schemas/message.schema'

const result = verify(messageContentSchema, input)
if (!result.success) {
  // result.errors 에 구체적 위반 내용
}
```

## 기술 스택

- Next.js 15 + React 19
- Socket.io 4 (WebSocket)
- Zustand (상태관리)
- Zod (런타임 검증 / SDD verify)
- React Hook Form + Zod (폼 검증)
- Tailwind CSS
