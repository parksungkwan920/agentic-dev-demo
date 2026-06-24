'use client'
import { useEffect } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import { connectSocket } from '@/lib/socket'
import { loadUser } from '@/lib/storage'
import { useUserStore } from '@/stores/userStore'
import { useChatStore } from '@/stores/chatStore'
import { useSocketEvents } from '@/lib/useSocketEvents'
import BuddyChatPopup from '@/components/BuddyChatPopup'

export default function BuddyChatPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const buddyId = params.id as string
  const buddyName = searchParams.get('name') ?? '알 수 없음'

  const { setMe, addBuddy } = useUserStore()
  const { setActiveBuddy, loadHistory } = useChatStore()

  useSocketEvents()

  useEffect(() => {
    const saved = loadUser()
    if (!saved) return

    // autoConnect: true 덕분에 이미 연결 중 or 완료 상태
    const socket = connectSocket()

    const doRegister = () => {
      socket.emit('user:register', { username: saved.username }, (result) => {
        if (!result.success || !result.user) return
        setMe(result.user)
        // URL 파라미터로 이미 이름을 알고 있으므로 user:search 불필요
        addBuddy({ id: buddyId, username: buddyName, status: 'online' })
        setActiveBuddy(buddyId)
        // 히스토리 백그라운드 로드 (UI는 이미 표시 중)
        socket.emit('chat:history', buddyId, (messages) => loadHistory(buddyId, messages))
      })
    }

    // 이미 연결됐으면 즉시, 아니면 connect 이벤트 대기
    if (socket.connected) doRegister()
    else socket.once('connect', doRegister)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // 로그인 정보 없으면 에러 표시
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

  // 즉시 채팅 UI 표시 — 메시지는 백그라운드에서 채워짐
  return <BuddyChatPopup buddyId={buddyId} buddyName={buddyName} />
}
