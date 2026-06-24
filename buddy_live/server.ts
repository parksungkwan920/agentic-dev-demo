/**
 * 버디버디 커스텀 서버 (Next.js + Socket.io)
 * SDD: 모든 이벤트 핸들러는 specs/에 정의된 계약을 따릅니다.
 */
import { createServer } from 'http'
import { parse } from 'url'
import next from 'next'
import { Server, Socket } from 'socket.io'
import { v4 as uuidv4 } from 'uuid'

import type { ClientToServerEvents, ServerToClientEvents, SocketData } from './src/specs/socket-events.spec'
import type { UserSpec } from './src/specs/user.spec'
import type { BuddyRequestSpec, BuddyInfo } from './src/specs/buddy.spec'
import type { MessageSpec, ChatRoomSpec } from './src/specs/message.spec'
import type { GroupRoomSpec, GroupMessageSpec, GroupRoomSummary } from './src/specs/group.spec'

// ── 인메모리 스토어 ──────────────────────────────────────────
const users = new Map<string, UserSpec>()
const usersByName = new Map<string, string>()
const buddyRequests = new Map<string, BuddyRequestSpec>()
const chatRooms = new Map<string, ChatRoomSpec>()
const groupRooms = new Map<string, GroupRoomSpec>()
// 멀티 윈도우: 유저 ID → 열린 소켓 수 (버디 목록창 + 채팅 팝업창 모두 포함)
const userSocketCount = new Map<string, number>()

// ── 유틸 ─────────────────────────────────────────────────────
function getChatRoomId(id1: string, id2: string): string {
  return [id1, id2].sort().join('::')
}

function getOrCreateChatRoom(id1: string, id2: string): ChatRoomSpec {
  const roomId = getChatRoomId(id1, id2)
  if (!chatRooms.has(roomId)) {
    chatRooms.set(roomId, {
      id: roomId,
      participantIds: [id1, id2] as [string, string],
      messages: [],
      lastActivity: new Date().toISOString(),
    })
  }
  return chatRooms.get(roomId)!
}

function toGroupSummary(room: GroupRoomSpec): GroupRoomSummary {
  const last = room.messages[room.messages.length - 1]
  return {
    id: room.id,
    name: room.name,
    memberCount: room.memberIds.length,
    lastMessage: last
      ? { senderName: last.senderName, content: last.content, timestamp: last.timestamp }
      : undefined,
  }
}

// ── 서버 시작 ────────────────────────────────────────────────
const dev = process.env.NODE_ENV !== 'production'
const port = parseInt(process.env.PORT ?? '3000', 10)
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const httpServer = createServer((req, res) => {
    const parsedUrl = parse(req.url!, true)
    handle(req, res, parsedUrl)
  })

  const io = new Server<ClientToServerEvents, ServerToClientEvents, Record<string, never>, SocketData>(
    httpServer,
    { cors: { origin: '*', methods: ['GET', 'POST'] } }
  )

  io.on('connection', (socket: Socket<ClientToServerEvents, ServerToClientEvents, Record<string, never>, SocketData>) => {
    console.log(`[소켓] 연결: ${socket.id}`)

    // ── user:register ─────────────────────────────────────────
    socket.on('user:register', ({ username }, cb) => {
      if (!username || username.trim().length < 2 || username.trim().length > 20) {
        return cb({ success: false, error: '닉네임은 2~20자여야 합니다' })
      }
      if (!/^[a-zA-Z0-9_가-힣]+$/.test(username.trim())) {
        return cb({ success: false, error: '닉네임은 영문, 숫자, 밑줄, 한글만 사용 가능합니다' })
      }

      const clean = username.trim()

      if (usersByName.has(clean)) {
        const existingId = usersByName.get(clean)!
        const existing = users.get(existingId)!
        const wasOffline = existing.status === 'offline'

        // 멀티 윈도우 허용: 같은 닉네임으로 여러 창에서 접속 가능
        existing.socketId = socket.id
        existing.status = 'online'
        socket.data.userId = existing.id
        socket.data.username = existing.username
        socket.join(existing.id)

        // 소켓 카운트 증가
        userSocketCount.set(existing.id, (userSocketCount.get(existing.id) ?? 0) + 1)

        // 참여 중인 그룹방 재입장
        groupRooms.forEach((room) => {
          if (room.memberIds.includes(existing.id)) socket.join(room.id)
        })

        // 오프라인→온라인 전환 시에만 버디에게 알림
        if (wasOffline) {
          existing.buddyIds.forEach((bid) => {
            io.to(bid).emit('user:status-changed', { userId: existing.id, status: 'online' })
          })
        }

        return cb({ success: true, user: existing })
      }

      const newUser: UserSpec = {
        id: uuidv4(),
        username: clean,
        status: 'online',
        buddyIds: [],
        pendingReceived: [],
        pendingSent: [],
        socketId: socket.id,
        createdAt: new Date().toISOString(),
      }

      users.set(newUser.id, newUser)
      usersByName.set(clean, newUser.id)
      socket.data.userId = newUser.id
      socket.data.username = clean
      socket.join(newUser.id)
      userSocketCount.set(newUser.id, 1)

      console.log(`[등록] ${clean} (${newUser.id})`)
      cb({ success: true, user: newUser })
    })

    // ── buddy:list ────────────────────────────────────────────
    socket.on('buddy:list', (cb) => {
      const myId = socket.data.userId
      if (!myId) return cb([])
      const user = users.get(myId)
      if (!user) return cb([])
      const buddyList = user.buddyIds
        .map((id) => users.get(id))
        .filter((u): u is UserSpec => !!u)
        .map((u) => ({ id: u.id, username: u.username, status: u.status }))
      cb(buddyList)
    })

    // ── user:search ───────────────────────────────────────────
    socket.on('user:search', ({ query }, cb) => {
      const myId = socket.data.userId
      const results = Array.from(users.values())
        .filter((u) => u.id !== myId && u.username.toLowerCase().includes(query.toLowerCase()))
        .slice(0, 10)
        .map((u) => ({ id: u.id, username: u.username, status: u.status }))
      cb({ users: results })
    })

    // ── buddy:request ─────────────────────────────────────────
    socket.on('buddy:request', ({ toUsername }, cb) => {
      const fromId = socket.data.userId
      if (!fromId) return cb({ success: false, error: '인증이 필요합니다' })

      const toId = usersByName.get(toUsername.trim())
      if (!toId) return cb({ success: false, error: '해당 사용자를 찾을 수 없습니다' })
      if (toId === fromId) return cb({ success: false, error: '자기 자신에게 요청할 수 없습니다' })

      const fromUser = users.get(fromId)!
      const toUser = users.get(toId)!

      if (fromUser.buddyIds.includes(toId)) return cb({ success: false, error: '이미 버디입니다' })
      if (fromUser.pendingSent.includes(toId)) return cb({ success: false, error: '이미 버디 요청을 보냈습니다' })

      const requestId = uuidv4()
      buddyRequests.set(requestId, { id: requestId, fromId, toId, status: 'pending', createdAt: new Date().toISOString() })
      fromUser.pendingSent.push(toId)
      toUser.pendingReceived.push(fromId)

      io.to(toId).emit('buddy:request-received', {
        requestId,
        from: { id: fromUser.id, username: fromUser.username, status: fromUser.status },
      })
      console.log(`[버디요청] ${fromUser.username} → ${toUser.username}`)
      cb({ success: true, requestId })
    })

    // ── buddy:respond ─────────────────────────────────────────
    socket.on('buddy:respond', ({ requestId, fromId, accept }, cb) => {
      const myId = socket.data.userId
      if (!myId) return cb({ success: false, error: '인증이 필요합니다' })

      const request = buddyRequests.get(requestId)
      if (!request || request.toId !== myId) return cb({ success: false, error: '유효하지 않은 요청입니다' })

      const toUser = users.get(myId)!
      const fromUser = users.get(fromId)!
      if (!fromUser) return cb({ success: false, error: '요청자를 찾을 수 없습니다' })

      toUser.pendingReceived = toUser.pendingReceived.filter((id) => id !== fromId)
      fromUser.pendingSent = fromUser.pendingSent.filter((id) => id !== myId)
      request.status = accept ? 'accepted' : 'rejected'

      if (accept) {
        toUser.buddyIds.push(fromId)
        fromUser.buddyIds.push(myId)
        io.to(myId).emit('buddy:request-accepted', { buddy: { id: fromUser.id, username: fromUser.username, status: fromUser.status } })
        io.to(fromId).emit('buddy:request-accepted', { buddy: { id: toUser.id, username: toUser.username, status: toUser.status } })
        console.log(`[버디수락] ${fromUser.username} ↔ ${toUser.username}`)
      } else {
        io.to(fromId).emit('buddy:request-rejected', { requestId })
      }
      cb({ success: true })
    })

    // ── message:send (1:1) ────────────────────────────────────
    socket.on('message:send', ({ receiverId, content }, cb) => {
      const senderId = socket.data.userId
      if (!senderId) return cb({ success: false, error: '인증이 필요합니다' })
      if (!content || content.trim().length === 0) return cb({ success: false, error: '메시지를 입력하세요' })
      if (content.length > 500) return cb({ success: false, error: '메시지는 최대 500자까지 가능합니다' })

      const sender = users.get(senderId)
      const receiver = users.get(receiverId)
      if (!sender || !receiver) return cb({ success: false, error: '사용자를 찾을 수 없습니다' })
      if (!sender.buddyIds.includes(receiverId)) return cb({ success: false, error: '버디가 아닌 사용자에게는 메시지를 보낼 수 없습니다' })

      const message: MessageSpec = {
        id: uuidv4(),
        senderId,
        receiverId,
        content: content.trim(),
        type: 'text',
        status: receiver.status === 'online' ? 'delivered' : 'sent',
        timestamp: new Date().toISOString(),
      }

      const room = getOrCreateChatRoom(senderId, receiverId)
      room.messages.push(message)
      room.lastActivity = message.timestamp

      io.to(receiverId).emit('message:receive', { message })
      cb({ success: true, message })
    })

    // ── chat:history ──────────────────────────────────────────
    socket.on('chat:history', (buddyId, cb) => {
      const myId = socket.data.userId
      if (!myId) return cb([])
      cb(chatRooms.get(getChatRoomId(myId, buddyId))?.messages ?? [])
    })

    // ── message:read ──────────────────────────────────────────
    socket.on('message:read', ({ messageIds, chatRoomId }) => {
      const room = chatRooms.get(chatRoomId)
      if (!room) return
      const myId = socket.data.userId
      room.messages.forEach((m) => {
        if (messageIds.includes(m.id) && m.receiverId === myId) m.status = 'read'
      })
      const firstMsg = room.messages.find((m) => messageIds.includes(m.id))
      if (firstMsg) io.to(firstMsg.senderId).emit('message:read-ack', { messageIds })
    })

    // ── group:create ──────────────────────────────────────────
    socket.on('group:create', ({ name, memberIds }, cb) => {
      const myId = socket.data.userId
      if (!myId) return cb({ success: false, error: '인증이 필요합니다' })

      // SDD verify
      if (!name || name.trim().length < 2 || name.trim().length > 30) {
        return cb({ success: false, error: '방 이름은 2~30자여야 합니다' })
      }
      if (!memberIds || memberIds.length === 0) {
        return cb({ success: false, error: '최소 1명 이상을 초대해야 합니다' })
      }

      const allMemberIds = [...new Set([myId, ...memberIds])]
      const room: GroupRoomSpec = {
        id: uuidv4(),
        name: name.trim(),
        creatorId: myId,
        memberIds: allMemberIds,
        messages: [],
        createdAt: new Date().toISOString(),
        lastActivity: new Date().toISOString(),
      }

      groupRooms.set(room.id, room)

      // 모든 멤버를 Socket.io room에 join + 초대 알림
      allMemberIds.forEach((uid) => {
        io.in(uid).socketsJoin(room.id)
        if (uid !== myId) {
          io.to(uid).emit('group:invited', { room: toGroupSummary(room) })
        }
      })

      const myUser = users.get(myId)!
      console.log(`[그룹생성] "${room.name}" by ${myUser.username} (${allMemberIds.length}명)`)
      cb({ success: true, room: toGroupSummary(room) })
    })

    // ── group:list ────────────────────────────────────────────
    socket.on('group:list', (cb) => {
      const myId = socket.data.userId
      if (!myId) return cb([])
      const myRooms = Array.from(groupRooms.values())
        .filter((r) => r.memberIds.includes(myId))
        .map(toGroupSummary)
      cb(myRooms)
    })

    // ── group:history ─────────────────────────────────────────
    socket.on('group:history', (roomId, cb) => {
      const myId = socket.data.userId
      if (!myId) return cb([])
      const room = groupRooms.get(roomId)
      if (!room || !room.memberIds.includes(myId)) return cb([])
      cb(room.messages)
    })

    // ── group:message:send ────────────────────────────────────
    socket.on('group:message:send', ({ roomId, content }, cb) => {
      const senderId = socket.data.userId
      if (!senderId) return cb({ success: false, error: '인증이 필요합니다' })
      if (!content || content.trim().length === 0) return cb({ success: false, error: '메시지를 입력하세요' })
      if (content.length > 500) return cb({ success: false, error: '메시지는 최대 500자까지 가능합니다' })

      const room = groupRooms.get(roomId)
      if (!room) return cb({ success: false, error: '존재하지 않는 그룹방입니다' })
      if (!room.memberIds.includes(senderId)) return cb({ success: false, error: '그룹 멤버가 아닙니다' })

      const sender = users.get(senderId)!
      const message: GroupMessageSpec = {
        id: uuidv4(),
        roomId,
        senderId,
        senderName: sender.username,
        content: content.trim(),
        timestamp: new Date().toISOString(),
      }

      room.messages.push(message)
      room.lastActivity = message.timestamp

      // 방 전체에 브로드캐스트 (나 제외)
      socket.to(roomId).emit('group:message:receive', { message })

      console.log(`[그룹메시지] "${room.name}" ${sender.username}: ${content.substring(0, 30)}`)
      cb({ success: true, message })
    })

    // ── group:invite ──────────────────────────────────────────
    socket.on('group:invite', ({ roomId, memberIds }, cb) => {
      const myId = socket.data.userId
      if (!myId) return cb({ success: false, error: '인증이 필요합니다' })

      const room = groupRooms.get(roomId)
      if (!room) return cb({ success: false, error: '존재하지 않는 그룹방입니다' })
      if (!room.memberIds.includes(myId)) return cb({ success: false, error: '그룹 멤버가 아닙니다' })

      const newMembers = memberIds.filter((id) => !room.memberIds.includes(id))
      newMembers.forEach((uid) => {
        room.memberIds.push(uid)
        io.in(uid).socketsJoin(roomId)
        io.to(uid).emit('group:invited', { room: toGroupSummary(room) })
      })

      // 시스템 메시지
      if (newMembers.length > 0) {
        const names = newMembers.map((id) => users.get(id)?.username ?? id).join(', ')
        const sysMsg: GroupMessageSpec = {
          id: uuidv4(), roomId, senderId: 'system', senderName: 'system',
          content: `${names}님이 초대되었습니다`,
          timestamp: new Date().toISOString(),
        }
        room.messages.push(sysMsg)
        io.to(roomId).emit('group:message:receive', { message: sysMsg })
      }

      cb({ success: true })
    })

    // ── group:leave ───────────────────────────────────────────
    socket.on('group:leave', ({ roomId }, cb) => {
      const myId = socket.data.userId
      if (!myId) return cb({ success: false, error: '인증이 필요합니다' })

      const room = groupRooms.get(roomId)
      if (!room || !room.memberIds.includes(myId)) return cb({ success: false, error: '그룹 멤버가 아닙니다' })

      room.memberIds = room.memberIds.filter((id) => id !== myId)
      socket.leave(roomId)

      const me = users.get(myId)!
      const sysMsg: GroupMessageSpec = {
        id: uuidv4(), roomId, senderId: 'system', senderName: 'system',
        content: `${me.username}님이 나갔습니다`,
        timestamp: new Date().toISOString(),
      }
      room.messages.push(sysMsg)
      io.to(roomId).emit('group:message:receive', { message: sysMsg })
      io.to(roomId).emit('group:member:left', { roomId, userId: myId, username: me.username })

      if (room.memberIds.length === 0) groupRooms.delete(roomId)

      console.log(`[그룹나가기] "${room.name}" ${me.username}`)
      cb({ success: true })
    })

    // ── disconnect ────────────────────────────────────────────
    socket.on('disconnect', () => {
      const userId = socket.data.userId
      if (!userId) return
      const user = users.get(userId)
      if (!user) return

      // 소켓 카운트 감소: 마지막 창이 닫혔을 때만 오프라인 처리
      const count = (userSocketCount.get(userId) ?? 1) - 1
      userSocketCount.set(userId, Math.max(0, count))

      if (count <= 0) {
        userSocketCount.delete(userId)
        user.status = 'offline'
        user.socketId = null
        user.buddyIds.forEach((bid) => {
          io.to(bid).emit('user:status-changed', { userId, status: 'offline' })
        })
        console.log(`[연결해제] ${user.username} (모든 창 닫힘)`)
      } else {
        console.log(`[창닫기] ${user.username} (남은 창: ${count}개)`)
      }
    })
  })

  httpServer.listen(port, '0.0.0.0', () => {
    const interfaces = require('os').networkInterfaces()
    const ips: string[] = ['localhost']
    Object.values(interfaces).forEach((iface: unknown) => {
      (iface as Array<{ family: string; address: string; internal: boolean }>).forEach((addr) => {
        if (addr.family === 'IPv4' && !addr.internal) ips.push(addr.address)
      })
    })
    console.log('\n🚀 버디버디 서버 시작!')
    console.log('─────────────────────────────────')
    ips.forEach((ip) => console.log(`  http://${ip}:${port}`))
    console.log('─────────────────────────────────\n')
  })
})
