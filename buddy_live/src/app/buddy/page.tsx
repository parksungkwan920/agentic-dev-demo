'use client'
import { useEffect, useState } from 'react'
import { connectSocket } from '@/lib/socket'
import { loadUser } from '@/lib/storage'
import { useUserStore } from '@/stores/userStore'
import { useGroupStore } from '@/stores/groupStore'
import { useSocketEvents } from '@/lib/useSocketEvents'
import BuddyList from '@/components/BuddyList'

export default function BuddyPage() {
  const { setMe, setBuddies } = useUserStore()
  const { setRooms } = useGroupStore()
  const [ready, setReady] = useState(false)
  const [error, setError] = useState('')

  useSocketEvents()

  useEffect(() => {
    // window.open()으로 열린 창이므로 resizeTo/moveTo 가능
    window.resizeTo(300, 530)
    window.moveTo(0, 0)

    const saved = loadUser()
    if (!saved) {
      setError('버디버디 로그인 페이지에서 먼저 로그인해주세요.')
      return
    }

    const socket = connectSocket()

    const doRegister = () => {
      socket.emit('user:register', { username: saved.username }, (result) => {
        if (!result.success || !result.user) {
          setError(result.error ?? '연결 실패')
          return
        }
        setMe(result.user)
        // buddy:list 와 group:list 병렬 요청
        let done = 0
        const checkDone = () => { if (++done === 2) setReady(true) }
        socket.emit('buddy:list', (buddies) => { setBuddies(buddies); checkDone() })
        socket.emit('group:list', (rooms) => { setRooms(rooms); checkDone() })
      })
    }

    if (socket.connected) doRegister()
    else {
      socket.once('connect', doRegister)
      socket.once('connect_error', () => setError('서버에 연결할 수 없습니다.'))
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-buddy-bg p-4">
        <div className="bg-white rounded-xl shadow p-6 text-center">
          <p className="text-3xl mb-3">⚠️</p>
          <p className="text-sm text-gray-700">{error}</p>
        </div>
      </div>
    )
  }

  if (!ready) {
    return (
      <div className="h-screen flex items-center justify-center bg-buddy-bg">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-buddy-primary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-500">연결 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <BuddyList />
    </div>
  )
}
