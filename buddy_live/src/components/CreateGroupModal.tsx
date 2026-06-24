'use client'
import { useState } from 'react'
import { useUserStore } from '@/stores/userStore'
import { useGroupStore } from '@/stores/groupStore'
import { getSocket } from '@/lib/socket'
import { verify } from '@/lib/verify'
import { groupCreatePayloadSchema } from '@/schemas/group.schema'
import { cn } from '@/lib/utils'

interface Props {
  onClose: () => void
}

export default function CreateGroupModal({ onClose }: Props) {
  const { buddies } = useUserStore()
  const { addRoom } = useGroupStore()
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const toggle = (id: string) =>
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })

  const handleCreate = () => {
    setError(null)
    const memberIds = [...selected]

    // SDD verify
    const v = verify(groupCreatePayloadSchema, { name, memberIds })
    if (!v.success) {
      setError(v.errors?.[0] ?? '입력 오류')
      return
    }

    setCreating(true)
    const socket = getSocket()
    socket.emit('group:create', { name: name.trim(), memberIds }, (result) => {
      setCreating(false)
      if (result.success && result.room) {
        addRoom(result.room)
        onClose()
      } else {
        setError(result.error ?? '그룹 생성 실패')
      }
    })
  }

  const onlineBuddies = buddies.filter((b) => b.status === 'online')
  const offlineBuddies = buddies.filter((b) => b.status !== 'online')

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md flex flex-col max-h-[90vh]">
        {/* 헤더 */}
        <div className="p-6 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
          <h2 className="text-lg font-bold text-gray-800">그룹 채팅 만들기</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
        </div>

        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {/* 방 이름 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">방 이름</label>
            <input
              type="text"
              value={name}
              onChange={(e) => { setName(e.target.value); setError(null) }}
              placeholder="그룹 방 이름 (2~30자)"
              maxLength={30}
              className="w-full px-4 py-2.5 rounded-xl border-2 border-gray-200 focus:border-buddy-primary outline-none text-sm"
            />
          </div>

          {/* 버디 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              초대할 버디 선택
              {selected.size > 0 && (
                <span className="ml-2 text-buddy-primary font-semibold">{selected.size}명 선택</span>
              )}
            </label>

            {buddies.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">버디가 없습니다. 먼저 버디를 추가하세요.</p>
            ) : (
              <div className="space-y-1 max-h-52 overflow-y-auto">
                {onlineBuddies.length > 0 && (
                  <>
                    <p className="text-xs text-gray-400 px-1 pt-1">온라인</p>
                    {onlineBuddies.map((b) => (
                      <BuddyCheckItem
                        key={b.id}
                        username={b.username}
                        status={b.status}
                        checked={selected.has(b.id)}
                        onToggle={() => toggle(b.id)}
                      />
                    ))}
                  </>
                )}
                {offlineBuddies.length > 0 && (
                  <>
                    <p className="text-xs text-gray-400 px-1 pt-2">오프라인</p>
                    {offlineBuddies.map((b) => (
                      <BuddyCheckItem
                        key={b.id}
                        username={b.username}
                        status={b.status}
                        checked={selected.has(b.id)}
                        onToggle={() => toggle(b.id)}
                      />
                    ))}
                  </>
                )}
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">
              {error}
            </div>
          )}
        </div>

        {/* 하단 버튼 */}
        <div className="p-6 border-t border-gray-100 flex gap-2 flex-shrink-0">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border-2 border-gray-200 text-gray-600 text-sm font-medium hover:bg-gray-50"
          >
            취소
          </button>
          <button
            onClick={handleCreate}
            disabled={creating || !name.trim() || selected.size === 0}
            className={cn(
              'flex-1 py-2.5 rounded-xl text-white text-sm font-semibold transition-all',
              creating || !name.trim() || selected.size === 0
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-buddy-gradient hover:opacity-90 active:scale-95 shadow-md'
            )}
          >
            {creating ? '생성 중...' : `그룹 만들기 (${selected.size + 1}명)`}
          </button>
        </div>
      </div>
    </div>
  )
}

function BuddyCheckItem({
  username, status, checked, onToggle,
}: {
  username: string
  status: 'online' | 'offline' | 'away'
  checked: boolean
  onToggle: () => void
}) {
  const dotColor = status === 'online' ? 'bg-buddy-online' : status === 'away' ? 'bg-buddy-away' : 'bg-buddy-offline'

  return (
    <button
      onClick={onToggle}
      className={cn(
        'w-full flex items-center gap-3 p-2.5 rounded-xl transition-colors text-left',
        checked ? 'bg-buddy-primary/10 border border-buddy-primary/30' : 'hover:bg-gray-50 border border-transparent'
      )}
    >
      <div className="relative flex-shrink-0">
        <div className="w-8 h-8 rounded-full bg-buddy-gradient flex items-center justify-center text-white font-bold text-xs">
          {username[0].toUpperCase()}
        </div>
        <span className={cn('absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-white', dotColor)} />
      </div>
      <span className={cn('flex-1 text-sm font-medium', checked ? 'text-buddy-primary' : 'text-gray-700')}>
        {username}
      </span>
      <div className={cn(
        'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0',
        checked ? 'bg-buddy-primary border-buddy-primary' : 'border-gray-300'
      )}>
        {checked && <span className="text-white text-xs">✓</span>}
      </div>
    </button>
  )
}
