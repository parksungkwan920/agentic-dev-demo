'use client'
import { useState } from 'react'
import { useUserStore } from '@/stores/userStore'
import { useGroupStore } from '@/stores/groupStore'
import { openChatWindow } from '@/lib/windowManager'
import AddBuddyModal from './AddBuddyModal'
import BuddyRequestBanner from './BuddyRequestBanner'
import CreateGroupModal from './CreateGroupModal'
import { cn } from '@/lib/utils'

const STATUS_COLOR = { online: 'bg-buddy-online', offline: 'bg-buddy-offline', away: 'bg-buddy-away' }
const STATUS_LABEL = { online: '온라인', offline: '오프라인', away: '자리비움' }

export default function BuddyList() {
  const { me, buddies } = useUserStore()
  const { rooms } = useGroupStore()
  const [showAddModal, setShowAddModal] = useState(false)
  const [showGroupModal, setShowGroupModal] = useState(false)

  const online = buddies.filter((b) => b.status === 'online')
  const offline = buddies.filter((b) => b.status !== 'online')

  return (
    <div className="flex flex-col h-full bg-white">
      {/* 내 프로필 */}
      <div className="p-3 bg-buddy-gradient text-white flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center font-bold">
            {me?.username[0].toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-sm truncate">{me?.username}</p>
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-buddy-online" />
              <span className="text-xs text-white/80">온라인</span>
            </div>
          </div>
        </div>
      </div>

      {/* 버디 요청 알림 */}
      <BuddyRequestBanner />

      {/* 스크롤 목록 */}
      <div className="flex-1 overflow-y-auto">

        {/* ── 버디 섹션 ── */}
        <SectionHeader
          label="버디"
          count={buddies.length}
          onAdd={() => setShowAddModal(true)}
          color="bg-buddy-primary"
        />

        {buddies.length === 0 ? (
          <EmptyHint label="아직 버디가 없습니다" action="버디 추가" onAction={() => setShowAddModal(true)} />
        ) : (
          <div className="pb-1">
            {online.length > 0 && (
              <>
                <GroupLabel label={`온라인 — ${online.length}`} />
                {online.map((b) => (
                  <BuddyRow
                    key={b.id}
                    username={b.username}
                    status={b.status}
                    onClick={() => openChatWindow('buddy', b.id, b.username)}
                  />
                ))}
              </>
            )}
            {offline.length > 0 && (
              <>
                <GroupLabel label={`오프라인 — ${offline.length}`} />
                {offline.map((b) => (
                  <BuddyRow
                    key={b.id}
                    username={b.username}
                    status={b.status}
                    onClick={() => openChatWindow('buddy', b.id, b.username)}
                  />
                ))}
              </>
            )}
          </div>
        )}

        {/* ── 그룹 채팅 섹션 ── */}
        <SectionHeader
          label="그룹 채팅"
          count={rooms.length}
          onAdd={() => setShowGroupModal(true)}
          color="bg-buddy-secondary"
        />

        {rooms.length === 0 ? (
          <EmptyHint label="그룹 채팅이 없습니다" action="그룹 만들기" onAction={() => setShowGroupModal(true)} />
        ) : (
          <div className="pb-1">
            {rooms.map((room) => (
              <GroupRow
                key={room.id}
                name={room.name}
                memberCount={room.memberCount}
                lastMessage={room.lastMessage}
                onClick={() => openChatWindow('group', room.id, room.name)}
              />
            ))}
          </div>
        )}
      </div>

      {showAddModal && <AddBuddyModal onClose={() => setShowAddModal(false)} />}
      {showGroupModal && <CreateGroupModal onClose={() => setShowGroupModal(false)} />}
    </div>
  )
}

// ── 서브 컴포넌트 ─────────────────────────────────────────────

function SectionHeader({ label, count, onAdd, color }: {
  label: string; count: number; onAdd: () => void; color: string
}) {
  return (
    <div className="flex items-center justify-between px-3 py-2 border-t border-gray-100 bg-gray-50">
      <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
        {label}{count > 0 && ` (${count})`}
      </span>
      <button
        onClick={onAdd}
        className={cn('w-5 h-5 rounded-full text-white text-sm leading-none flex items-center justify-center hover:opacity-80', color)}
        title={`${label} 추가`}
      >+</button>
    </div>
  )
}

function GroupLabel({ label }: { label: string }) {
  return <p className="px-3 pt-1.5 pb-0.5 text-[10px] text-gray-400 font-medium">{label}</p>
}

function EmptyHint({ label, action, onAction }: { label: string; action: string; onAction: () => void }) {
  return (
    <div className="px-3 py-3 text-center">
      <p className="text-xs text-gray-400">{label}</p>
      <button onClick={onAction} className="mt-1 text-[11px] text-buddy-primary hover:underline">{action}</button>
    </div>
  )
}

function BuddyRow({ username, status, onClick }: {
  username: string
  status: 'online' | 'offline' | 'away'
  onClick: () => void
}) {
  return (
    <button
      onDoubleClick={onClick}
      onClick={onClick}
      className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-buddy-bg transition-colors text-left group"
    >
      <div className="relative flex-shrink-0">
        <div className="w-8 h-8 rounded-full bg-buddy-gradient flex items-center justify-center text-white font-bold text-xs">
          {username[0].toUpperCase()}
        </div>
        <span className={cn('absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-white', STATUS_COLOR[status])} />
      </div>
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm font-medium truncate', status === 'offline' ? 'text-gray-400' : 'text-gray-800')}>
          {username}
        </p>
        <p className="text-[10px] text-gray-400">{STATUS_LABEL[status]}</p>
      </div>
      <span className="text-[10px] text-gray-300 group-hover:text-buddy-primary opacity-0 group-hover:opacity-100 transition-opacity">
        대화
      </span>
    </button>
  )
}

function GroupRow({ name, memberCount, lastMessage, onClick }: {
  name: string
  memberCount: number
  lastMessage?: { senderName: string; content: string }
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-buddy-bg transition-colors text-left group"
    >
      <div className="w-8 h-8 rounded-full bg-buddy-secondary flex items-center justify-center text-white text-sm flex-shrink-0">
        👥
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800 truncate">{name}</p>
        <p className="text-[10px] text-gray-400 truncate">
          {lastMessage
            ? `${lastMessage.senderName}: ${lastMessage.content}`
            : `멤버 ${memberCount}명`}
        </p>
      </div>
    </button>
  )
}
