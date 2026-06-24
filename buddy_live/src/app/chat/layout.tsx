/**
 * 채팅 팝업 창 전용 레이아웃
 * 주 창(버디 목록)과 다른 컴팩트 스타일을 적용합니다.
 */
export default function ChatPopupLayout({ children }: { children: React.ReactNode }) {
  return <div className="h-screen flex flex-col overflow-hidden">{children}</div>
}
