'use client'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { connectSocket, disconnectSocket } from '@/lib/socket'
import { saveUser } from '@/lib/storage'
import { userRegisterPayloadSchema } from '@/schemas/user.schema'
import { cn } from '@/lib/utils'

type FormData = z.infer<typeof userRegisterPayloadSchema>

const POPUP_FEATURES = 'width=300,height=530,left=0,top=0,resizable=yes,toolbar=no,menubar=no,location=no,status=no,scrollbars=no'

export default function LoginForm() {
  const [error, setError] = useState<string | null>(null)
  const [connecting, setConnecting] = useState(false)
  const [done, setDone] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(userRegisterPayloadSchema),
  })

  const onSubmit = (data: FormData) => {
    setConnecting(true)
    setError(null)

    const socket = connectSocket()

    const doRegister = () => {
      socket.emit('user:register', { username: data.username }, (result) => {
        setConnecting(false)
        if (result.success && result.user) {
          // localStorage에 저장 → 팝업 창이 자동 로그인에 사용
          saveUser(result.user.username)
          // 버디 목록을 팝업 창으로 열기 (클릭 핸들러 내부라 팝업 차단 안 됨)
          window.open('/buddy', 'buddylist', POPUP_FEATURES)
          disconnectSocket()
          setDone(true)
        } else {
          setError(result.error ?? '등록에 실패했습니다')
          disconnectSocket()
        }
      })
    }

    if (socket.connected) {
      doRegister()
    } else {
      socket.once('connect', doRegister)
      socket.once('connect_error', () => {
        setConnecting(false)
        setError('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.')
      })
    }
  }

  // 팝업 오픈 후 안내 화면
  if (done) {
    return (
      <div className="min-h-screen bg-buddy-gradient flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm text-center">
          <div className="text-5xl mb-4">🎉</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">버디버디가 열렸습니다!</h2>
          <p className="text-sm text-gray-500">
            왼쪽 상단의 버디 목록 창을 확인하세요.
          </p>
          <p className="text-xs text-gray-400 mt-4">
            팝업이 차단됐다면 주소창의 팝업 허용 버튼을 클릭하세요.
          </p>
          <button
            onClick={() => window.open('/buddy', 'buddylist', POPUP_FEATURES)}
            className="mt-4 px-4 py-2 bg-buddy-gradient text-white rounded-xl text-sm font-medium hover:opacity-90"
          >
            다시 열기
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-buddy-gradient flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-buddy-gradient rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-3xl">💬</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-800">버디버디</h1>
          <p className="text-gray-500 text-sm mt-1">친구와 실시간으로 대화하세요</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">닉네임</label>
            <input
              {...register('username')}
              type="text"
              placeholder="닉네임을 입력하세요 (2~20자)"
              className={cn(
                'w-full px-4 py-3 rounded-xl border-2 text-sm outline-none transition-all',
                errors.username
                  ? 'border-red-400 focus:border-red-500'
                  : 'border-gray-200 focus:border-buddy-primary'
              )}
              autoComplete="off"
            />
            {errors.username && (
              <p className="text-red-500 text-xs mt-1">{errors.username.message}</p>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={connecting}
            className={cn(
              'w-full py-3 rounded-xl font-semibold text-white transition-all',
              connecting
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-buddy-gradient hover:opacity-90 active:scale-95 shadow-md'
            )}
          >
            {connecting ? '연결 중...' : '입장하기'}
          </button>
        </form>

        <p className="text-center text-xs text-gray-400 mt-6">
          같은 네트워크의 친구와 대화할 수 있습니다
        </p>
      </div>
    </div>
  )
}
