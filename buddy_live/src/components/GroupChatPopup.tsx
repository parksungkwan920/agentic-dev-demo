'use client'
import { useEffect, useRef, useState } from 'react'
import { useGroupStore } from '@/stores/groupStore'
import { useUserStore } from '@/stores/userStore'
import { getSocket } from '@/lib/socket'
import { verify } from '@/lib/verify'
import { messageContentSchema } from '@/schemas/message.schema'
import { cn, formatTime, formatDate } from '@/lib/utils'
import type { GroupMessageSpec } from '@/specs/group.spec'

interface Props {
  roomId: string
  roomName: string
}

export default function GroupChatPopup({ roomId, roomName }: Props) {
  const { rooms, conversations, addMessage, removeRoom } = useGroupStore()
  const { me } = useUserStore()
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [inputError, setInputError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const room = rooms.find((r) => r.id === roomId)
  const messages = conversations[roomId] ?? []

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    const v = verify(messageContentSchema, input.trim())
    if (!v.success) { setInputError(v.errors?.[0] ?? '입력 오류'); return }
    setInputError(null)

    const socket = getSocket()
    setSending(true)
    socket.emit('group:message:send', { roomId, content: input.trim() }, (result) => {
      setSending(false)
      if (result.success && result.message) {
        addMessage(roomId, result.message)
        setInput('')
      } else {
        setInputError(result.error ?? '전송 실패')
      }
    })
  }

  const handleLeave = () => {
    if (!confirm(`"${roomName}" 그룹에서 나가겠습니까?`)) return
    const socket = getSocket()
    socket.emit('group:leave', { roomId }, (result) => {
      if (result.success) {
        removeRoom(roomId)
        window.close()
      }
    })
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
    <div className="flex flex-col h-screen bg-buddy-bg">
      {/* 컴팩트 헤더 */}
      <div className="bg-gradient-to-r from-buddy-secondary to-buddy-primary text-white px-3 py-2.5 flex items-center gap-2.5 flex-shrink-0 shadow-sm">
        <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm flex-shrink-0">
          👥
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-sm truncate">{roomName}</p>
          <p className="text-[10px] text-white/70">
            {room ? `멤버 ${room.memberCount}명` : '그룹 채팅'}
          </p>
        </div>
        <button
          onClick={handleLeave}
          className="text-[11px] text-white/60 hover:text-white transition-colors"
        >
          나가기
        </button>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-3xl mb-2">🎉</p>
            <p className="text-xs text-gray-500">그룹 채팅이 시작되었습니다!</p>
          </div>
        )}

        {grouped.map(({ date, msgs }) => (
          <div key={date}>
            <div className="text-center mb-2">
              <span className="text-[10px] text-gray-400 bg-white px-2 py-0.5 rounded-full shadow-sm">{date}</span>
            </div>
            <div className="space-y-0.5">
              {msgs.map((msg, i) => {
                const isMine = msg.senderId === me?.id
                const isSystem = msg.senderId === 'system'
                const showName = !isMine && !isSystem && (i === 0 || msgs[i - 1]?.senderId !== msg.senderId)

                if (isSystem) {
                  return (
                    <div key={msg.id} className="text-center py-1">
                      <span className="text-[10px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{msg.content}</span>
                    </div>
                  )
                }

                return (
                  <div key={msg.id} className={cn('flex items-end gap-1.5', isMine ? 'flex-row-reverse' : 'flex-row')}>
                    {!isMine && (
                      <div className="w-6 flex-shrink-0 self-end">
                        {showName && (
                          <div className="w-6 h-6 rounded-full bg-buddy-secondary flex items-center justify-center text-white text-[10px] font-bold">
                            {msg.senderName[0].toUpperCase()}
                          </div>
                        )}
                      </div>
                    )}
                    <div className={cn('flex flex-col gap-0.5 max-w-[78%]', isMine ? 'items-end' : 'items-start')}>
                      {showName && (
                        <span className="text-[10px] text-gray-500 px-1">{msg.senderName}</span>
                      )}
                      <div className={cn(
                        'px-3 py-2 rounded-2xl text-sm break-words leading-snug',
                        isMine
                          ? 'bg-buddy-secondary text-white rounded-br-sm'
                          : 'bg-white text-gray-800 shadow-sm rounded-bl-sm'
                      )}>
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
      <div className="bg-white border-t border-gray-100 p-2 flex-shrink-0">
        {inputError && <p className="text-[11px] text-red-500 mb-1 px-1">{inputError}</p>}
        <div className="flex gap-1.5">
          <input
            type="text"
            value={input}
            onChange={(e) => { setInput(e.target.value); setInputError(null) }}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="그룹에 메시지 보내기..."
            maxLength={500}
            disabled={sending}
            className="flex-1 px-3 py-2 rounded-xl border border-gray-200 focus:border-buddy-secondary outline-none text-sm disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className={cn(
              'px-3 py-2 rounded-xl text-sm font-medium transition-all',
              sending || !input.trim()
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-buddy-secondary text-white hover:opacity-90 active:scale-95'
            )}
          >
            전송
          </button>
        </div>
      </div>
    </div>
  )
}
