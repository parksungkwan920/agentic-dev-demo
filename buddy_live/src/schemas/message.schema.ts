import { z } from 'zod'
import { MESSAGE_CONSTRAINTS } from '@/specs/message.spec'

export const messageTypeSchema = z.enum(MESSAGE_CONSTRAINTS.TYPE_VALUES)
export const messageStatusSchema = z.enum(MESSAGE_CONSTRAINTS.STATUS_VALUES)

export const messageContentSchema = z
  .string()
  .min(MESSAGE_CONSTRAINTS.CONTENT_MIN, '메시지를 입력하세요')
  .max(MESSAGE_CONSTRAINTS.CONTENT_MAX, `메시지는 최대 ${MESSAGE_CONSTRAINTS.CONTENT_MAX}자까지 가능합니다`)

export const messageSpecSchema = z.object({
  id: z.string().uuid(),
  senderId: z.string().uuid(),
  receiverId: z.string().uuid(),
  content: messageContentSchema,
  type: messageTypeSchema,
  status: messageStatusSchema,
  timestamp: z.string().datetime(),
})

export const messageSendPayloadSchema = z.object({
  receiverId: z.string().uuid('유효하지 않은 수신자 ID입니다'),
  content: messageContentSchema,
})

export const messageReadPayloadSchema = z.object({
  messageIds: z.array(z.string().uuid()).min(1),
  chatRoomId: z.string().min(1),
})
