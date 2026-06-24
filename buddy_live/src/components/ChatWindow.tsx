'use client'
import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/stores/chatStore'
import { useUserStore } from '@/stores/userStore'
import { getSocket } from '@/lib/socket'
import { messageContentSchema } from '@/schemas/message.schema'
import { verify } from '@/lib/verify'
import { cn, formatTime, formatDate } from '@/lib/utils'
import type { MessageSpec } from '@/specs/message.spec'

const STATUS_ICON: Record<MessageSpec['status'], string> = {
  sent: '✓',
  delivered: '✓✓',
  read: '✓✓',
}

export default function ChatWindow() {
  const { activeBuddyId, conversations, addMessage } = useChatStore()
  const { me, buddies } = useUserStore()
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [inputError, setInputError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const activeBuddy = buddies.find((b) => b.id === activeBuddyId)
  const messages = activeBuddyId ? (conversations[activeBuddyId] ?? []) : []

  // 새 메시지 시 스크롤
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 채팅창 진입 시 읽음 처리
  useEffect(() => {
    if (!activeBuddyId || !me) return
    const socket = getSocket()
    const unread = messages
      .filter((m) => m.receiverId === me.id && m.status !== 'read')
      .map((m) => m.id)
    if (unread.length > 0) {
      socket.emit('message:read', {
        messageIds: unread,
        chatRoomId: [me.id, activeBuddyId].sort().join('::'),
      })
    }
  }, [activeBuddyId, me, messages])

  const handleSend = () => {
    if (!activeBuddyId || !me) return

    // SDD verify: 메시지 내용 검증
    const v = verify(messageContentSchema, input.trim())
    if (!v.success) {
      setInputError(v.errors?.[0] ?? '입력 오류')
      return
    }
    setInputError(null)

    const socket = getSocket()
    setSending(true)

    socket.emit('message:send', { receiverId: activeBuddyId, content: input.trim() }, (result) => {
      setSending(false)
      if (result.success && result.message) {
        addMessage(activeBuddyId, result.message)
        setInput('')
      } else {
        setInputError(result.error ?? '전송 실패')
      }
    })
  }

  if (!activeBuddyId || !activeBuddy) {
    return (
      <div className="flex-1 flex items-center justify-center bg-buddy-bg">
        <div className="text-center">
          <p className="text-6xl mb-4">💬</p>
          <p className="text-lg font-semibold text-gray-600">버디를 선택하세요</p>
          <p className="text-sm text-gray-400 mt-1">왼쪽 목록에서 대화할 버디를 선택하세요</p>
        </div>
      </div>
    )
  }

  // 날짜별 메시지 그룹핑
  const grouped = messages.reduce<Array<{ date: string; msgs: MessageSpec[] }>>((acc, msg) => {
    const date = formatDate(msg.timestamp)
    const last = acc[acc.length - 1]
    if (!last || last.date !== date) {
      acc.push({ date, msgs: [msg] })
    } else {
      last.msgs.push(msg)
    }
    return acc
  }, [])

  return (
    <div className="flex-1 flex flex-col bg-buddy-bg">
      {/* 채팅 헤더 */}
      <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center gap-3 shadow-sm">
        <div className="relative">
          <div className="w-10 h-10 rounded-full bg-buddy-gradient flex items-center justify-center text-white font-bold">
            {activeBuddy.username[0].toUpperCase()}
          </div>
          <span
            className={cn(
              'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white',
              activeBuddy.status === 'online'
                ? 'bg-buddy-online'
                : activeBuddy.status === 'away'
                ? 'bg-buddy-away'
                : 'bg-buddy-offline'
            )}
          />
        </div>
        <div>
          <p className="font-semibold text-gray-800">{activeBuddy.username}</p>
          <p className="text-xs text-gray-400">
            {activeBuddy.status === 'online'
              ? '온라인'
              : activeBuddy.status === 'away'
              ? '자리비움'
              : '오프라인'}
          </p>
        </div>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <p className="text-4xl mb-2">👋</p>
            <p className="text-sm text-gray-500">
              {activeBuddy.username}님과의 대화를 시작하세요
            </p>
          </div>
        )}

        {grouped.map(({ date, msgs }) => (
          <div key={date}>
            <div className="text-center mb-4">
              <span className="text-xs text-gray-400 bg-white px-3 py-1 rounded-full shadow-sm">
                {date}
              </span>
            </div>
            <div className="space-y-1">
              {msgs.map((msg, i) => {
                const isMine = msg.senderId === me?.id
                const showAvatar =
                  !isMine && (i === 0 || msgs[i - 1]?.senderId !== msg.senderId)

                return (
                  <div
                    key={msg.id}
                    className={cn('flex items-end gap-2', isMine ? 'flex-row-reverse' : 'flex-row')}
                  >
                    {/* 상대방 아바타 */}
                    {!isMine && (
                      <div className="w-7 flex-shrink-0">
                        {showAvatar && (
                          <div className="w-7 h-7 rounded-full bg-buddy-gradient flex items-center justify-center text-white text-xs font-bold">
                            {activeBuddy.username[0].toUpperCase()}
                          </div>
                        )}
                      </div>
                    )}

                    <div className={cn('flex flex-col gap-0.5 max-w-[70%]', isMine ? 'items-end' : 'items-start')}>
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
                      <div className={cn('flex items-center gap-1 text-[10px] text-gray-400', isMine ? 'flex-row-reverse' : '')}>
                        <span>{formatTime(msg.timestamp)}</span>
                        {isMine && (
                          <span className={cn(msg.status === 'read' ? 'text-buddy-primary' : 'text-gray-400')}>
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
      <div className="bg-white border-t border-gray-100 p-4">
        {inputError && (
          <p className="text-xs text-red-500 mb-2">{inputError}</p>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => { setInput(e.target.value); setInputError(null) }}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="메시지를 입력하세요..."
            maxLength={500}
            disabled={sending}
            className="flex-1 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-buddy-primary outline-none text-sm transition-all disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className={cn(
              'px-5 py-3 rounded-xl font-medium text-sm transition-all',
              sending || !input.trim()
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-buddy-gradient text-white hover:opacity-90 active:scale-95 shadow-md'
            )}
          >
            전송
          </button>
        </div>
        {input.length > 400 && (
          <p className="text-xs text-gray-400 mt-1 text-right">{input.length}/500</p>
        )}
      </div>
    </div>
  )
}
