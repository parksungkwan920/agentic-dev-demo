/**
 * 채팅 팝업 창 관리
 * 같은 대화를 두 번 열지 않고, 이미 열린 창은 포커스만 줍니다.
 */

const openWindows = new Map<string, Window>()

const POPUP_WIDTH = 380
const POPUP_HEIGHT = 530

function popupFeatures(w: number, h: number): string {
  const left = Math.round(window.screenX + (window.outerWidth - w) / 2)
  const top = Math.round(window.screenY + (window.outerHeight - h) / 2)
  return `width=${w},height=${h},left=${left},top=${top},resizable=yes,scrollbars=no,status=no,toolbar=no,menubar=no,location=no`
}

export function openChatWindow(
  type: 'buddy' | 'group',
  id: string,
  name: string
): void {
  const key = `${type}:${id}`
  const existing = openWindows.get(key)

  // 이미 열려있으면 포커스
  if (existing && !existing.closed) {
    existing.focus()
    return
  }

  const url = `/chat/${type}/${encodeURIComponent(id)}?name=${encodeURIComponent(name)}`
  const win = window.open(url, key, popupFeatures(POPUP_WIDTH, POPUP_HEIGHT))

  if (win) {
    openWindows.set(key, win)
    // 창이 닫히면 맵에서 제거
    const timer = setInterval(() => {
      if (win.closed) {
        openWindows.delete(key)
        clearInterval(timer)
      }
    }, 1000)
  }
}
