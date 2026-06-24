import { z } from 'zod'
import { GROUP_CONSTRAINTS } from '@/specs/group.spec'
import { messageContentSchema } from './message.schema'

export const groupNameSchema = z
  .string()
  .min(GROUP_CONSTRAINTS.NAME_MIN, `방 이름은 최소 ${GROUP_CONSTRAINTS.NAME_MIN}자 이상이어야 합니다`)
  .max(GROUP_CONSTRAINTS.NAME_MAX, `방 이름은 최대 ${GROUP_CONSTRAINTS.NAME_MAX}자까지 가능합니다`)

export const groupCreatePayloadSchema = z.object({
  name: groupNameSchema,
  memberIds: z
    .array(z.string().uuid())
    .min(GROUP_CONSTRAINTS.MEMBER_MIN - 1, '최소 1명 이상을 초대해야 합니다')
    .max(GROUP_CONSTRAINTS.MEMBER_MAX - 1, `최대 ${GROUP_CONSTRAINTS.MEMBER_MAX - 1}명까지 초대 가능합니다`),
})

export const groupMessageSendPayloadSchema = z.object({
  roomId: z.string().uuid(),
  content: messageContentSchema,
})
