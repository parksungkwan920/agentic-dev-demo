/**
 * SDD - Buddy(친구) 관계 도메인 명세서
 */

export type BuddyRequestStatus = 'pending' | 'accepted' | 'rejected'

export interface BuddyRequestSpec {
  id: string
  fromId: string
  toId: string
  status: BuddyRequestStatus
  createdAt: string
}

// ── 이벤트 계약 ───────────────────────────────────────────────
export interface BuddyRequestPayload {
  toUsername: string
}

export interface BuddyRequestResult {
  success: boolean
  requestId?: string
  error?: string
}

export interface BuddyRespondPayload {
  requestId: string
  fromId: string
  accept: boolean
}

export interface BuddyRespondResult {
  success: boolean
  error?: string
}

// 버디 목록에서 보여줄 정보
export interface BuddyInfo {
  id: string
  username: string
  status: 'online' | 'offline' | 'away'
}
