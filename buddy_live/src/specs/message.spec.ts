/**
 * SDD - Message 도메인 명세서
 */

export const MESSAGE_CONSTRAINTS = {
  CONTENT_MIN: 1,
  CONTENT_MAX: 500,
  TYPE_VALUES: ['text', 'system'] as const,
  STATUS_VALUES: ['sent', 'delivered', 'read'] as const,
} as const

export type MessageType = typeof MESSAGE_CONSTRAINTS.TYPE_VALUES[number]
export type MessageStatus = typeof MESSAGE_CONSTRAINTS.STATUS_VALUES[number]

export interface MessageSpec {
  id: string
  senderId: string
  receiverId: string
  content: string
  type: MessageType
  status: MessageStatus
  timestamp: string  // ISO 8601
}

export interface ChatRoomSpec {
  id: string         // 항상 두 userId를 정렬 후 join한 값
  participantIds: [string, string]
  messages: MessageSpec[]
  lastActivity: string
}

// ── 이벤트 계약 ───────────────────────────────────────────────
export interface MessageSendPayload {
  receiverId: string
  content: string
}

export interface MessageSendResult {
  success: boolean
  message?: MessageSpec
  error?: string
}

export interface MessageReceivePayload {
  message: MessageSpec
}

export interface MessageReadPayload {
  messageIds: string[]
  chatRoomId: string
}
