'use client'
import { useEffect, useRef, useState } from 'react'
import { useGroupStore } from '@/stores/groupStore'
import { useUserStore } from '@/stores/userStore'
import { getSocket } from '@/lib/socket'
import { verify } from '@/lib/verify'
import { messageContentSchema } from '@/schemas/message.schema'
import { cn, formatTime, formatDate } from '@/lib/utils'
import type { GroupMessageSpec } from '@/specs/group.spec'

export default function GroupChatWindow() {
  const { activeRoomId, rooms, conversations, addMessage, removeRoom } = useGroupStore()
  const { me } = useUserStore()
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [inputError, setInputError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const activeRoom = rooms.find((r) => r.id === activeRoomId)
  const messages = activeRoomId ? (conversations[activeRoomId] ?? []) : []

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!activeRoomId || !me) return

    const v = verify(messageContentSchema, input.trim())
    if (!v.success) {
      setInputError(v.errors?.[0] ?? '입력 오류')
      return
    }
    setInputError(null)

    const socket = getSocket()
    setSending(true)
    socket.emit('group:message:send', { roomId: activeRoomId, content: input.trim() }, (result) => {
      setSending(false)
      if (result.success && result.message) {
        addMessage(activeRoomId, result.message)
        setInput('')
      } else {
        setInputError(result.error ?? '전송 실패')
      }
    })
  }

  const handleLeave = () => {
    if (!activeRoomId) return
    if (!confirm(`"${activeRoom?.name}" 그룹에서 나가겠습니까?`)) return
    const socket = getSocket()
    socket.emit('group:leave', { roomId: activeRoomId }, (result) => {
      if (result.success) removeRoom(activeRoomId)
    })
  }

  if (!activeRoomId || !activeRoom) {
    return (
      <div className="flex-1 flex items-center justify-center bg-buddy-bg">
        <div className="text-center">
          <p className="text-6xl mb-4">👥</p>
          <p className="text-lg font-semibold text-gray-600">그룹 채팅방을 선택하세요</p>
          <p className="text-sm text-gray-400 mt-1">왼쪽 목록에서 그룹 채팅방을 선택하거나 새로 만드세요</p>
        </div>
      </div>
    )
  }

  // 날짜별 그룹핑
  const grouped = messages.reduce<Array<{ date: string; msgs: GroupMessageSpec[] }>>((acc, msg) => {
    const date = formatDate(msg.timestamp)
    const last = acc[acc.length - 1]
    if (!last || last.date !== date) acc.push({ date, msgs: [msg] })
    else last.msgs.push(msg)
    return acc
  }, [])

  return (
    <div className="flex-1 flex flex-col bg-buddy-bg">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-buddy-secondary flex items-center justify-center text-white text-lg">
            👥
          </div>
          <div>
            <p className="font-semibold text-gray-800">{activeRoom.name}</p>
            <p className="text-xs text-gray-400">멤버 {activeRoom.memberCount}명</p>
          </div>
        </div>
        <button
          onClick={handleLeave}
          className="text-xs text-gray-400 hover:text-red-500 transition-colors px-3 py-1.5 rounded-lg hover:bg-red-50"
        >
          나가기
        </button>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <p className="text-4xl mb-2">🎉</p>
            <p className="text-sm text-gray-500">그룹 채팅이 시작되었습니다!</p>
          </div>
        )}

        {grouped.map(({ date, msgs }) => (
          <div key={date}>
            <div className="text-center mb-4">
              <span className="text-xs text-gray-400 bg-white px-3 py-1 rounded-full shadow-sm">{date}</span>
            </div>
            <div className="space-y-1">
              {msgs.map((msg, i) => {
                const isMine = msg.senderId === me?.id
                const isSystem = msg.senderId === 'system'
                const showName = !isMine && !isSystem && (i === 0 || msgs[i - 1]?.senderId !== msg.senderId)

                if (isSystem) {
                  return (
                    <div key={msg.id} className="text-center py-1">
                      <span className="text-xs text-gray-400 bg-gray-100 px-3 py-1 rounded-full">
                        {msg.content}
                      </span>
                    </div>
                  )
                }

                return (
                  <div key={msg.id} className={cn('flex items-end gap-2', isMine ? 'flex-row-reverse' : 'flex-row')}>
                    {/* 아바타 */}
                    {!isMine && (
                      <div className="w-7 flex-shrink-0 self-end">
                        {showName && (
                          <div className="w-7 h-7 rounded-full bg-buddy-secondary flex items-center justify-center text-white text-xs font-bold">
                            {msg.senderName[0].toUpperCase()}
                          </div>
                        )}
                      </div>
                    )}

                    <div className={cn('flex flex-col gap-0.5 max-w-[70%]', isMine ? 'items-end' : 'items-start')}>
                      {showName && (
                        <span className="text-xs text-gray-500 px-1">{msg.senderName}</span>
                      )}
                      <div
                        className={cn(
                          'px-4 py-2.5 rounded-2xl text-sm break-words',
                          isMine
                            ? 'bg-buddy-primary text-white rounded-br-sm'
                            : 'bg-white text-gray-800 shadow-sm rounded-bl-sm'
                        )}
                      >
                        {msg.content}
                      </div>
                      <span className="text-[10px] text-gray-400 px-1">{formatTime(msg.timestamp)}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* 입력창 */}
      <div className="bg-white border-t border-gray-100 p-4">
        {inputError && <p className="text-xs text-red-500 mb-2">{inputError}</p>}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => { setInput(e.target.value); setInputError(null) }}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="그룹에 메시지 보내기..."
            maxLength={500}
            disabled={sending}
            className="flex-1 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-buddy-secondary outline-none text-sm transition-all disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className={cn(
              'px-5 py-3 rounded-xl font-medium text-sm transition-all',
              sending || !input.trim()
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-buddy-secondary text-white hover:opacity-90 active:scale-95 shadow-md'
            )}
          >
            전송
          </button>
        </div>
      </div>
    </div>
  )
}
