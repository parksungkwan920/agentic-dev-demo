'use client'
import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/stores/chatStore'
import { useUserStore } from '@/stores/userStore'
import { getSocket } from '@/lib/socket'
import { verify } from '@/lib/verify'
import { messageContentSchema } from '@/schemas/message.schema'
import { cn, formatTime, formatDate } from '@/lib/utils'
import type { MessageSpec } from '@/specs/message.spec'

const STATUS_ICON: Record<MessageSpec['status'], string> = {
  sent: '✓', delivered: '✓✓', read: '✓✓',
}

interface Props {
  buddyId: string
  buddyName: string
}

export default function BuddyChatPopup({ buddyId, buddyName }: Props) {
  const { conversations, addMessage, markRead } = useChatStore()
  const { me, buddies } = useUserStore()
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [inputError, setInputError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const buddy = buddies.find((b) => b.id === buddyId)
  const messages = conversations[buddyId] ?? []

  // 새 메시지 시 스크롤
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 입장 시 읽음 처리
  useEffect(() => {
    if (!me) return
    const socket = getSocket()
    const unread = messages
      .filter((m) => m.receiverId === me.id && m.status !== 'read')
      .map((m) => m.id)
    if (unread.length > 0) {
      socket.emit('message:read', {
        messageIds: unread,
        chatRoomId: [me.id, buddyId].sort().join('::'),
      })
    }
  }, [buddyId, me, messages])

  const handleSend = () => {
    if (!me) return
    const v = verify(messageContentSchema, input.trim())
    if (!v.success) { setInputError(v.errors?.[0] ?? '입력 오류'); return }
    setInputError(null)

    const socket = getSocket()
    setSending(true)
    socket.emit('message:send', { receiverId: buddyId, content: input.trim() }, (result) => {
      setSending(false)
      if (result.success && result.message) {
        addMessage(buddyId, result.message)
        setInput('')
      } else {
        setInputError(result.error ?? '전송 실패')
      }
    })
  }

  const statusColor = buddy?.status === 'online'
    ? 'bg-buddy-online' : buddy?.status === 'away' ? 'bg-buddy-away' : 'bg-buddy-offline'

  // 날짜별 그룹핑
  const grouped = messages.reduce<Array<{ date: string; msgs: MessageSpec[] }>>((acc, msg) => {
    const date = formatDate(msg.timestamp)
    const last = acc[acc.length - 1]
    if (!last || last.date !== date) acc.push({ date, msgs: [msg] })
    else last.msgs.push(msg)
    return acc
  }, [])

  return (
    <div className="flex flex-col h-screen bg-buddy-bg">
      {/* 컴팩트 헤더 */}
      <div className="bg-buddy-gradient text-white px-3 py-2.5 flex items-center gap-2.5 flex-shrink-0 shadow-sm">
        <div className="relative flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center font-bold text-sm">
            {buddyName[0].toUpperCase()}
          </div>
          <span className={cn('absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-buddy-primary', statusColor)} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-sm truncate">{buddyName}</p>
          <p className="text-[10px] text-white/70">
            {buddy?.status === 'online' ? '온라인' : buddy?.status === 'away' ? '자리비움' : '오프라인'}
          </p>
        </div>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-3xl mb-2">💬</p>
            <p className="text-xs text-gray-500">{buddyName}님과 대화를 시작하세요</p>
          </div>
        )}

        {grouped.map(({ date, msgs }) => (
          <div key={date}>
            <div className="text-center mb-2">
              <span className="text-[10px] text-gray-400 bg-white px-2 py-0.5 rounded-full shadow-sm">{date}</span>
            </div>
            <div className="space-y-0.5">
              {msgs.map((msg) => {
                const isMine = msg.senderId === me?.id
                return (
                  <div key={msg.id} className={cn('flex items-end gap-1.5', isMine ? 'flex-row-reverse' : 'flex-row')}>
                    <div className={cn('flex flex-col gap-0.5 max-w-[75%]', isMine ? 'items-end' : 'items-start')}>
                      <div className={cn(
                        'px-3 py-2 rounded-2xl text-sm break-words leading-snug',
                        isMine
                          ? 'bg-buddy-primary text-white rounded-br-sm'
                          : 'bg-white text-gray-800 shadow-sm rounded-bl-sm'
                      )}>
                        {msg.content}
                      </div>
                      <div className={cn('flex items-center gap-0.5 text-[10px] text-gray-400', isMine ? 'flex-row-reverse' : '')}>
                        <span>{formatTime(msg.timestamp)}</span>
                        {isMine && (
                          <span className={cn(msg.status === 'read' ? 'text-buddy-primary' : 'text-gray-300')}>
                            {STATUS_ICON[msg.status]}
                          </span>
                        )}
                      </div>
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
            placeholder="메시지 입력..."
            maxLength={500}
            disabled={sending}
            className="flex-1 px-3 py-2 rounded-xl border border-gray-200 focus:border-buddy-primary outline-none text-sm disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className={cn(
              'px-3 py-2 rounded-xl text-sm font-medium transition-all',
              sending || !input.trim()
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-buddy-primary text-white hover:opacity-90 active:scale-95'
            )}
          >
            전송
          </button>
        </div>
      </div>
    </div>
  )
}
