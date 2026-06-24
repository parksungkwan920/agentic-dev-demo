import { create } from 'zustand'
import type { MessageSpec } from '@/specs/message.spec'

interface ChatState {
  activeBuddyId: string | null
  conversations: Record<string, MessageSpec[]>  // buddyId → messages

  setActiveBuddy: (buddyId: string | null) => void
  loadHistory: (buddyId: string, messages: MessageSpec[]) => void
  addMessage: (buddyId: string, message: MessageSpec) => void
  markRead: (buddyId: string, messageIds: string[]) => void
  updateStatus: (buddyId: string, messageIds: string[], status: MessageSpec['status']) => void
  getUnreadCount: (buddyId: string, myId: string) => number
}

export const useChatStore = create<ChatState>((set, get) => ({
  activeBuddyId: null,
  conversations: {},

  setActiveBuddy: (buddyId) => set({ activeBuddyId: buddyId }),

  loadHistory: (buddyId, messages) =>
    set((s) => ({
      conversations: { ...s.conversations, [buddyId]: messages },
    })),

  addMessage: (buddyId, message) =>
    set((s) => {
      const prev = s.conversations[buddyId] ?? []
      // 중복 방지
      if (prev.some((m) => m.id === message.id)) return s
      return {
        conversations: {
          ...s.conversations,
          [buddyId]: [...prev, message],
        },
      }
    }),

  markRead: (buddyId, messageIds) =>
    set((s) => {
      const msgs = s.conversations[buddyId] ?? []
      return {
        conversations: {
          ...s.conversations,
          [buddyId]: msgs.map((m) =>
            messageIds.includes(m.id) ? { ...m, status: 'read' as const } : m
          ),
        },
      }
    }),

  updateStatus: (buddyId, messageIds, status) =>
    set((s) => {
      const msgs = s.conversations[buddyId] ?? []
      return {
        conversations: {
          ...s.conversations,
          [buddyId]: msgs.map((m) =>
            messageIds.includes(m.id) ? { ...m, status } : m
          ),
        },
      }
    }),

  getUnreadCount: (buddyId, myId) => {
    const msgs = get().conversations[buddyId] ?? []
    return msgs.filter((m) => m.receiverId === myId && m.status !== 'read').length
  },
}))
