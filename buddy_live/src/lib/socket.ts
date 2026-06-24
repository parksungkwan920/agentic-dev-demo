/**
 * 클라이언트 Socket.io 인스턴스 싱글톤
 */
import { io, Socket } from 'socket.io-client'
import type { ClientToServerEvents, ServerToClientEvents } from '@/specs/socket-events.spec'

type BuddySocket = Socket<ServerToClientEvents, ClientToServerEvents>

let socket: BuddySocket | null = null

export function getSocket(): BuddySocket {
  if (!socket) {
    // 같은 호스트의 서버에 연결 (로컬 네트워크 자동 감지)
    socket = io(window.location.origin, {
      transports: ['websocket', 'polling'],
      autoConnect: true,  // 페이지 로드 즉시 연결 시작 → 팝업 체감 속도 향상
    })
  }
  return socket
}

export function connectSocket(): BuddySocket {
  const s = getSocket()
  if (!s.connected) s.connect()
  return s
}

export function disconnectSocket(): void {
  if (socket?.connected) {
    socket.disconnect()
  }
}
