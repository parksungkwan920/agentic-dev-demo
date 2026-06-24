'use client'
import { useState } from 'react'
import { getSocket } from '@/lib/socket'
import { cn } from '@/lib/utils'

interface Props {
  onClose: () => void
}

interface SearchResult {
  id: string
  username: string
  status: 'online' | 'offline' | 'away'
}

const STATUS_LABEL = { online: '온라인', offline: '오프라인', away: '자리비움' }
const STATUS_COLOR = { online: 'bg-buddy-online', offline: 'bg-buddy-offline', away: 'bg-buddy-away' }

export default function AddBuddyModal({ onClose }: Props) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)
  const [sentTo, setSentTo] = useState<Set<string>>(new Set())

  const handleSearch = () => {
    if (!query.trim()) return
    setSearching(true)
    setMessage(null)
    const socket = getSocket()
    socket.emit('user:search', { query: query.trim() }, ({ users }) => {
      setSearching(false)
      setResults(users as SearchResult[])
      if (users.length === 0) setMessage({ text: '검색 결과가 없습니다', type: 'error' })
    })
  }

  const handleRequest = (toUsername: string, toId: string) => {
    const socket = getSocket()
    socket.emit('buddy:request', { toUsername }, (result) => {
      if (result.success) {
        setSentTo((prev) => new Set(prev).add(toId))
        setMessage({ text: `${toUsername}에게 버디 요청을 보냈습니다`, type: 'success' })
      } else {
        setMessage({ text: result.error ?? '요청 실패', type: 'error' })
      }
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-800">버디 추가</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              ×
            </button>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="닉네임으로 검색..."
              className="flex-1 px-4 py-2.5 rounded-xl border-2 border-gray-200 focus:border-buddy-primary outline-none text-sm"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="px-4 py-2.5 bg-buddy-gradient text-white rounded-xl text-sm font-medium hover:opacity-90 disabled:opacity-50"
            >
              {searching ? '...' : '검색'}
            </button>
          </div>

          {message && (
            <div
              className={cn(
                'rounded-lg p-3 text-sm',
                message.type === 'success'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-600 border border-red-200'
              )}
            >
              {message.text}
            </div>
          )}

          <div className="space-y-2 max-h-60 overflow-y-auto">
            {results.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-buddy-gradient flex items-center justify-center text-white font-bold text-sm">
                    {user.username[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-800 text-sm">{user.username}</p>
                    <div className="flex items-center gap-1">
                      <span className={cn('w-1.5 h-1.5 rounded-full', STATUS_COLOR[user.status])} />
                      <span className="text-xs text-gray-500">{STATUS_LABEL[user.status]}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleRequest(user.username, user.id)}
                  disabled={sentTo.has(user.id)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                    sentTo.has(user.id)
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-buddy-primary text-white hover:opacity-90 active:scale-95'
                  )}
                >
                  {sentTo.has(user.id) ? '요청됨' : '추가'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
