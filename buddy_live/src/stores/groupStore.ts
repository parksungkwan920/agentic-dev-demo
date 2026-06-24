import { create } from 'zustand'
import type { GroupRoomSummary, GroupMessageSpec } from '@/specs/group.spec'

interface GroupState {
  rooms: GroupRoomSummary[]
  activeRoomId: string | null
  conversations: Record<string, GroupMessageSpec[]>   // roomId → messages

  setRooms: (rooms: GroupRoomSummary[]) => void
  addRoom: (room: GroupRoomSummary) => void
  updateRoom: (room: GroupRoomSummary) => void
  removeRoom: (roomId: string) => void
  setActiveRoom: (roomId: string | null) => void
  loadHistory: (roomId: string, messages: GroupMessageSpec[]) => void
  addMessage: (roomId: string, message: GroupMessageSpec) => void
  getUnreadCount: (roomId: string, myId: string) => number
}

export const useGroupStore = create<GroupState>((set, get) => ({
  rooms: [],
  activeRoomId: null,
  conversations: {},

  setRooms: (rooms) => set({ rooms }),

  addRoom: (room) =>
    set((s) => ({
      rooms: s.rooms.some((r) => r.id === room.id)
        ? s.rooms.map((r) => (r.id === room.id ? room : r))
        : [...s.rooms, room],
    })),

  updateRoom: (room) =>
    set((s) => ({
      rooms: s.rooms.map((r) => (r.id === room.id ? room : r)),
    })),

  removeRoom: (roomId) =>
    set((s) => ({
      rooms: s.rooms.filter((r) => r.id !== roomId),
      activeRoomId: s.activeRoomId === roomId ? null : s.activeRoomId,
      conversations: Object.fromEntries(
        Object.entries(s.conversations).filter(([id]) => id !== roomId)
      ),
    })),

  setActiveRoom: (roomId) => set({ activeRoomId: roomId }),

  loadHistory: (roomId, messages) =>
    set((s) => ({ conversations: { ...s.conversations, [roomId]: messages } })),

  addMessage: (roomId, message) =>
    set((s) => {
      const prev = s.conversations[roomId] ?? []
      if (prev.some((m) => m.id === message.id)) return s

      // lastMessage 업데이트
      const updatedRooms = s.rooms.map((r) =>
        r.id === roomId
          ? { ...r, lastMessage: { senderName: message.senderName, content: message.content, timestamp: message.timestamp } }
          : r
      )

      return {
        rooms: updatedRooms,
        conversations: { ...s.conversations, [roomId]: [...prev, message] },
      }
    }),

  // 그룹은 읽음 추적 없이 단순 카운트 (활성방이 아닌 경우)
  getUnreadCount: (roomId, _myId) => {
    const { activeRoomId, conversations } = get()
    if (activeRoomId === roomId) return 0
    const msgs = conversations[roomId]
    if (!msgs) return 0
    // 마지막으로 열어본 이후 메시지 수 (간단 구현: 단순히 미열람 여부)
    return msgs.length > 0 ? 1 : 0
  },
}))
