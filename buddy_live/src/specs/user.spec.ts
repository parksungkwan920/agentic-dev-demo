/**
 * SDD - User 도메인 명세서 (Specification)
 * 이 파일이 진실의 단일 소스(Single Source of Truth)입니다.
 * 모든 구현은 이 명세를 만족해야 합니다.
 */

// ── 제약 조건 ────────────────────────────────────────────────
export const USER_CONSTRAINTS = {
  USERNAME_MIN: 2,
  USERNAME_MAX: 20,
  USERNAME_PATTERN: /^[a-zA-Z0-9_가-힣]+$/,
  STATUS_VALUES: ['online', 'offline', 'away'] as const,
} as const

// ── 핵심 타입 ─────────────────────────────────────────────────
export type UserStatus = typeof USER_CONSTRAINTS.STATUS_VALUES[number]

export interface UserSpec {
  id: string
  username: string
  status: UserStatus
  buddyIds: string[]
  pendingReceived: string[]  // 나에게 온 버디 요청 (상대방 ID)
  pendingSent: string[]      // 내가 보낸 버디 요청 (상대방 ID)
  socketId: string | null
  createdAt: string          // ISO 8601
}

// ── 이벤트 계약 (Event Contracts) ────────────────────────────
export interface UserRegisterPayload {
  username: string
}

export interface UserRegisterResult {
  success: boolean
  user?: UserSpec
  error?: string
}

export interface UserSearchPayload {
  query: string
}

export interface UserSearchResult {
  users: Pick<UserSpec, 'id' | 'username' | 'status'>[]
}

export interface UserStatusChangePayload {
  userId: string
  status: UserStatus
}
