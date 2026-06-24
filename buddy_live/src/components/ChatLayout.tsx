'use client'
import { useEffect } from 'react'
import { useSocketEvents } from '@/lib/useSocketEvents'
import { useUserStore } from '@/stores/userStore'
import { useGroupStore } from '@/stores/groupStore'
import { getSocket } from '@/lib/socket'
import BuddyList from './BuddyList'

/**
 * 메인 창: 버디 목록만 표시합니다.
 * 대화는 window.open()으로 별도 팝업 창에서 열립니다.
 */
export default function ChatLayout() {
  const { me, setBuddies } = useUserStore()
  const { setRooms } = useGroupStore()

  useSocketEvents()

  useEffect(() => {
    if (!me) return

    const socket = getSocket()
    // 기존 버디 목록 복원 (재접속 포함)
    socket.emit('buddy:list', (buddies) => setBuddies(buddies))
    socket.emit('group:list', (rooms) => setRooms(rooms))
  }, [me, setBuddies, setRooms])

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <BuddyList />
    </div>
  )
}
