/**
 * SDD - Group Chat 도메인 명세서
 */

export const GROUP_CONSTRAINTS = {
  NAME_MIN: 2,
  NAME_MAX: 30,
  MEMBER_MIN: 2,   // 나 포함 최소 2명 (상대방 최소 1명)
  MEMBER_MAX: 20,
} as const

export interface GroupMessageSpec {
  id: string
  roomId: string
  senderId: string
  senderName: string
  content: string
  timestamp: string
}

export interface GroupRoomSpec {
  id: string
  name: string
  creatorId: string
  memberIds: string[]
  messages: GroupMessageSpec[]
  createdAt: string
  lastActivity: string
}

// 클라이언트에서 표시할 요약 정보
export interface GroupRoomSummary {
  id: string
  name: string
  memberCount: number
  lastMessage?: Pick<GroupMessageSpec, 'senderName' | 'content' | 'timestamp'>
}

// ── 이벤트 계약 ───────────────────────────────────────────────
export interface GroupCreatePayload {
  name: string
  memberIds: string[]   // 초대할 버디 IDs (나 자신 제외)
}

export interface GroupCreateResult {
  success: boolean
  room?: GroupRoomSummary
  error?: string
}

export interface GroupMessageSendPayload {
  roomId: string
  content: string
}

export interface GroupMessageSendResult {
  success: boolean
  message?: GroupMessageSpec
  error?: string
}

export interface GroupMessageReceivePayload {
  message: GroupMessageSpec
}

export interface GroupInvitePayload {
  roomId: string
  memberIds: string[]
}

export interface GroupInviteResult {
  success: boolean
  error?: string
}

export interface GroupLeavePayload {
  roomId: string
}

export interface GroupLeaveResult {
  success: boolean
  error?: string
}
