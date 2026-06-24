'use client'
import { getSocket } from '@/lib/socket'
import { useUserStore } from '@/stores/userStore'
import { useChatStore } from '@/stores/chatStore'

export default function BuddyRequestBanner() {
  const { pendingRequests, removePendingRequest, addBuddy, me } = useUserStore()
  const { addMessage } = useChatStore()

  if (pendingRequests.length === 0) return null

  const handleRespond = (requestId: string, fromId: string, accept: boolean) => {
    const socket = getSocket()
    socket.emit('buddy:respond', { requestId, fromId, accept }, (result) => {
      if (result.success) {
        removePendingRequest(requestId)
      }
    })
  }

  return (
    <div className="space-y-2 p-3">
      {pendingRequests.map((req) => (
        <div
          key={req.requestId}
          className="bg-buddy-primary/10 border border-buddy-primary/30 rounded-xl p-3 flex items-center justify-between gap-3"
        >
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-full bg-buddy-gradient flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
              {req.from.username[0].toUpperCase()}
            </div>
            <p className="text-sm text-gray-700 truncate">
              <span className="font-semibold">{req.from.username}</span>님의 버디 요청
            </p>
          </div>
          <div className="flex gap-1.5 flex-shrink-0">
            <button
              onClick={() => handleRespond(req.requestId, req.from.id, true)}
              className="px-2.5 py-1 bg-buddy-online text-white rounded-lg text-xs font-medium hover:opacity-90"
            >
              수락
            </button>
            <button
              onClick={() => handleRespond(req.requestId, req.from.id, false)}
              className="px-2.5 py-1 bg-gray-200 text-gray-600 rounded-lg text-xs font-medium hover:bg-gray-300"
            >
              거절
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
