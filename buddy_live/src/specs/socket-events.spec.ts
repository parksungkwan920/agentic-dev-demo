/**
 * SDD - Socket.io 이벤트 전체 계약서
 * 클라이언트 ↔ 서버 간 모든 이벤트를 이 파일에서 정의합니다.
 */

import type { UserRegisterPayload, UserRegisterResult, UserSearchPayload, UserSearchResult, UserStatusChangePayload } from './user.spec'
import type { BuddyRequestPayload, BuddyRequestResult, BuddyRespondPayload, BuddyRespondResult, BuddyInfo } from './buddy.spec'
import type { MessageSendPayload, MessageSendResult, MessageReceivePayload, MessageReadPayload, MessageSpec } from './message.spec'
import type {
  GroupCreatePayload, GroupCreateResult,
  GroupMessageSendPayload, GroupMessageSendResult, GroupMessageReceivePayload,
  GroupInvitePayload, GroupInviteResult,
  GroupLeavePayload, GroupLeaveResult,
  GroupRoomSummary, GroupMessageSpec,
} from './group.spec'

// 클라이언트 → 서버 이벤트
export interface ClientToServerEvents {
  // 유저
  'user:register': (payload: UserRegisterPayload, cb: (result: UserRegisterResult) => void) => void
  'user:search': (payload: UserSearchPayload, cb: (result: UserSearchResult) => void) => void
  // 버디
  'buddy:request': (payload: BuddyRequestPayload, cb: (result: BuddyRequestResult) => void) => void
  'buddy:respond': (payload: BuddyRespondPayload, cb: (result: BuddyRespondResult) => void) => void
  // 1:1 메시지
  'message:send': (payload: MessageSendPayload, cb: (result: MessageSendResult) => void) => void
  'message:read': (payload: MessageReadPayload) => void
  'chat:history': (buddyId: string, cb: (messages: MessageSpec[]) => void) => void
  // 그룹
  'buddy:list': (cb: (buddies: BuddyInfo[]) => void) => void
  'group:create': (payload: GroupCreatePayload, cb: (result: GroupCreateResult) => void) => void
  'group:list': (cb: (rooms: GroupRoomSummary[]) => void) => void
  'group:history': (roomId: string, cb: (messages: GroupMessageSpec[]) => void) => void
  'group:message:send': (payload: GroupMessageSendPayload, cb: (result: GroupMessageSendResult) => void) => void
  'group:invite': (payload: GroupInvitePayload, cb: (result: GroupInviteResult) => void) => void
  'group:leave': (payload: GroupLeavePayload, cb: (result: GroupLeaveResult) => void) => void
}

// 서버 → 클라이언트 이벤트
export interface ServerToClientEvents {
  // 유저
  'user:status-changed': (payload: UserStatusChangePayload) => void
  // 버디
  'buddy:request-received': (payload: { requestId: string; from: BuddyInfo }) => void
  'buddy:request-accepted': (payload: { buddy: BuddyInfo }) => void
  'buddy:request-rejected': (payload: { requestId: string }) => void
  'buddy:list-updated': (payload: { buddies: BuddyInfo[] }) => void
  // 1:1 메시지
  'message:receive': (payload: MessageReceivePayload) => void
  'message:read-ack': (payload: { messageIds: string[] }) => void
  // 그룹
  'group:invited': (payload: { room: GroupRoomSummary }) => void
  'group:message:receive': (payload: GroupMessageReceivePayload) => void
  'group:member:joined': (payload: { roomId: string; userId: string; username: string }) => void
  'group:member:left': (payload: { roomId: string; userId: string; username: string }) => void
  // 오류
  'server:error': (payload: { code: string; message: string }) => void
}

// 소켓 데이터 (연결당 저장되는 서버사이드 정보)
export interface SocketData {
  userId: string
  username: string
}
