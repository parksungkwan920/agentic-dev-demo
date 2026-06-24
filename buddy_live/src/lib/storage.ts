/**
 * localStorage 기반 사용자 세션 유지
 * 팝업 창에서 동일 닉네임으로 소켓 재연결할 때 사용합니다.
 */

const KEY = 'buddy_live_user'

export interface StoredUser {
  username: string
}

export function saveUser(username: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(KEY, JSON.stringify({ username }))
}

export function loadUser(): StoredUser | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as StoredUser) : null
  } catch {
    return null
  }
}

export function clearUser(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(KEY)
}
