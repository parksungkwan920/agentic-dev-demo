'use client'
import { useEffect } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import { connectSocket } from '@/lib/socket'
import { loadUser } from '@/lib/storage'
import { useUserStore } from '@/stores/userStore'
import { useGroupStore } from '@/stores/groupStore'
import { useSocketEvents } from '@/lib/useSocketEvents'
import GroupChatPopup from '@/components/GroupChatPopup'

export default function GroupChatPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const roomId = params.id as string
  const roomName = searchParams.get('name') ?? '그룹 채팅'

  const { setMe } = useUserStore()
  const { addRoom, setActiveRoom, loadHistory } = useGroupStore()

  useSocketEvents()

  useEffect(() => {
    const saved = loadUser()
    if (!saved) return

    const socket = connectSocket()

    const doRegister = () => {
      socket.emit('user:register', { username: saved.username }, (result) => {
        if (!result.success || !result.user) return
        setMe(result.user)
        setActiveRoom(roomId)

        // group:list 와 group:history 병렬 요청 (순차 → 동시)
        socket.emit('group:list', (rooms) => rooms.forEach((r) => addRoom(r)))
        socket.emit('group:history', roomId, (messages) => loadHistory(roomId, messages))
      })
    }

    if (socket.connected) doRegister()
    else socket.once('connect', doRegister)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (typeof window !== 'undefined' && !loadUser()) {
    return (
      <div className="h-screen flex items-center justify-center bg-buddy-bg p-4">
        <div className="bg-white rounded-xl shadow p-6 text-center">
          <p className="text-3xl mb-3">⚠️</p>
          <p className="text-sm text-gray-700">버디버디 메인 창에서 먼저 로그인해주세요.</p>
        </div>
      </div>
    )
  }

  // 즉시 그룹 채팅 UI 표시
  return <GroupChatPopup roomId={roomId} roomName={roomName} />
}
