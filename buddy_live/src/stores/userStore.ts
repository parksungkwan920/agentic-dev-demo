import { create } from 'zustand'
import type { UserSpec } from '@/specs/user.spec'
import type { BuddyInfo } from '@/specs/buddy.spec'
import { saveUser } from '@/lib/storage'

interface PendingRequest {
  requestId: string
  from: BuddyInfo
}

interface UserState {
  me: UserSpec | null
  buddies: BuddyInfo[]
  pendingRequests: PendingRequest[]   // 받은 버디 요청

  setMe: (user: UserSpec) => void
  setBuddies: (buddies: BuddyInfo[]) => void
  addBuddy: (buddy: BuddyInfo) => void
  updateBuddyStatus: (userId: string, status: BuddyInfo['status']) => void
  addPendingRequest: (req: PendingRequest) => void
  removePendingRequest: (requestId: string) => void
  reset: () => void
}

export const useUserStore = create<UserState>((set) => ({
  me: null,
  buddies: [],
  pendingRequests: [],

  setMe: (user) => {
    saveUser(user.username)
    set({ me: user })
  },

  setBuddies: (buddies) => set({ buddies }),

  addBuddy: (buddy) =>
    set((s) => ({
      buddies: s.buddies.some((b) => b.id === buddy.id)
        ? s.buddies.map((b) => (b.id === buddy.id ? buddy : b))
        : [...s.buddies, buddy],
    })),

  updateBuddyStatus: (userId, status) =>
    set((s) => ({
      buddies: s.buddies.map((b) => (b.id === userId ? { ...b, status } : b)),
    })),

  addPendingRequest: (req) =>
    set((s) => ({
      pendingRequests: s.pendingRequests.some((r) => r.requestId === req.requestId)
        ? s.pendingRequests
        : [...s.pendingRequests, req],
    })),

  removePendingRequest: (requestId) =>
    set((s) => ({
      pendingRequests: s.pendingRequests.filter((r) => r.requestId !== requestId),
    })),

  reset: () => set({ me: null, buddies: [], pendingRequests: [] }),
}))
