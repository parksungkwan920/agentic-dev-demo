/**
 * SDD Verify 유틸리티
 * 스펙(명세)에 대한 런타임 검증을 수행합니다.
 * verify()는 ZodSchema를 받아 데이터가 명세를 만족하는지 확인합니다.
 */
import { z, ZodSchema, ZodError } from 'zod'

export interface VerifyResult<T> {
  success: boolean
  data?: T
  errors?: string[]
}

/**
 * SDD verify: 데이터가 명세(schema)를 만족하는지 검증합니다.
 * 실패 시 구체적인 오류 메시지를 반환합니다.
 */
export function verify<T>(schema: ZodSchema<T>, data: unknown): VerifyResult<T> {
  const result = schema.safeParse(data)

  if (result.success) {
    return { success: true, data: result.data }
  }

  const errors = result.error.errors.map(
    (e) => `[${e.path.join('.')}] ${e.message}`
  )

  return { success: false, errors }
}

/**
 * verify 실패 시 예외를 던지는 강한 검증
 * 서버사이드 내부 로직에서 사용 (외부 입력에는 사용 금지)
 */
export function verifyOrThrow<T>(schema: ZodSchema<T>, data: unknown): T {
  const result = verify(schema, data)
  if (!result.success || !result.data) {
    throw new Error(`SDD 명세 위반: ${result.errors?.join(', ')}`)
  }
  return result.data
}

/**
 * 여러 검증을 순서대로 실행하고 첫 번째 실패를 반환
 */
export function verifyAll(checks: Array<() => VerifyResult<unknown>>): VerifyResult<void> {
  for (const check of checks) {
    const result = check()
    if (!result.success) {
      return { success: false, errors: result.errors }
    }
  }
  return { success: true }
}
