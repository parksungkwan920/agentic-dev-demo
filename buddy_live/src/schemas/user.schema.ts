import { z } from 'zod'
import { USER_CONSTRAINTS } from '@/specs/user.spec'

export const userStatusSchema = z.enum(USER_CONSTRAINTS.STATUS_VALUES)

export const usernameSchema = z
  .string()
  .min(USER_CONSTRAINTS.USERNAME_MIN, `닉네임은 최소 ${USER_CONSTRAINTS.USERNAME_MIN}자 이상이어야 합니다`)
  .max(USER_CONSTRAINTS.USERNAME_MAX, `닉네임은 최대 ${USER_CONSTRAINTS.USERNAME_MAX}자까지 가능합니다`)
  .regex(USER_CONSTRAINTS.USERNAME_PATTERN, '닉네임은 영문, 숫자, 밑줄, 한글만 사용 가능합니다')

export const userSpecSchema = z.object({
  id: z.string().uuid(),
  username: usernameSchema,
  status: userStatusSchema,
  buddyIds: z.array(z.string().uuid()),
  pendingReceived: z.array(z.string().uuid()),
  pendingSent: z.array(z.string().uuid()),
  socketId: z.string().nullable(),
  createdAt: z.string().datetime(),
})

export const userRegisterPayloadSchema = z.object({
  username: usernameSchema,
})

export const userSearchPayloadSchema = z.object({
  query: z.string().min(1).max(50),
})
