'use client'
import { useEffect } from 'react'
import { getSocket } from './socket'
import { useUserStore } from '@/stores/userStore'
import { useChatStore } from '@/stores/chatStore'
import { useGroupStore } from '@/stores/groupStore'
import { openChatWindow } from './windowManager'

/** 메인 버디 목록 창인지 확인 (팝업 채팅창에서는 자동 열기 불필요) */
function isMainWindow(): boolean {
  return typeof window !== 'undefined' && !window.location.pathname.startsWith('/chat/')
}

export function useSocketEvents() {
  const { addBuddy, updateBuddyStatus, addPendingRequest, removePendingRequest, buddies, me } = useUserStore()
  const { addMessage, markRead, activeBuddyId } = useChatStore()
  const { addRoom, addMessage: addGroupMessage, removeRoom, rooms } = useGroupStore()

  useEffect(() => {
    const socket = getSocket()

    // ── 버디 이벤트 ───────────────────────────────────────────
    socket.on('user:status-changed', ({ userId, status }) => {
      updateBuddyStatus(userId, status)
    })

    socket.on('buddy:request-received', ({ requestId, from }) => {
      addPendingRequest({ requestId, from })
    })

    socket.on('buddy:request-accepted', ({ buddy }) => {
      addBuddy(buddy)
    })

    socket.on('buddy:request-rejected', ({ requestId }) => {
      removePendingRequest(requestId)
    })

    // ── 1:1 메시지 이벤트 ─────────────────────────────────────
    socket.on('message:receive', ({ message }) => {
      addMessage(message.senderId, message)

      // 메인 창에서만: 메시지가 오면 해당 버디 채팅창을 자동으로 열기
      if (isMainWindow()) {
        const sender = buddies.find((b) => b.id === message.senderId)
        if (sender) {
          openChatWindow('buddy', sender.id, sender.username)
        }
      }

      // 현재 활성 채팅창이 발신자라면 즉시 읽음 처리
      if (activeBuddyId === message.senderId) {
        socket.emit('message:read', {
          messageIds: [message.id],
          chatRoomId: [message.senderId, message.receiverId].sort().join('::'),
        })
      }
    })

    socket.on('message:read-ack', ({ messageIds }) => {
      if (activeBuddyId) markRead(activeBuddyId, messageIds)
    })

    // ── 그룹 이벤트 ───────────────────────────────────────────
    socket.on('group:invited', ({ room }) => {
      addRoom(room)
    })

    socket.on('group:message:receive', ({ message }) => {
      addGroupMessage(message.roomId, message)

      // 메인 창에서만: 다른 사람의 메시지가 오면 해당 그룹 채팅창 자동 열기
      if (isMainWindow() && message.senderId !== me?.id && message.senderId !== 'system') {
        const room = rooms.find((r) => r.id === message.roomId)
        if (room) {
          openChatWindow('group', room.id, room.name)
        }
      }
    })

    socket.on('group:member:left', () => {
      // 시스템 메시지로 이미 전달됨
    })

    return () => {
      socket.off('user:status-changed')
      socket.off('buddy:request-received')
      socket.off('buddy:request-accepted')
      socket.off('buddy:request-rejected')
      socket.off('message:receive')
      socket.off('message:read-ack')
      socket.off('group:invited')
      socket.off('group:message:receive')
      socket.off('group:member:left')
    }
  }, [activeBuddyId, addBuddy, addGroupMessage, addMessage, addPendingRequest, addRoom, buddies, markRead, me, removeRoom, removePendingRequest, rooms, updateBuddyStatus])
}
