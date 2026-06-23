/**
 * 클라이언트 API 래퍼. 게이트웨이(8080)를 직접 부르지 않고,
 * Next route handler 프록시(/api/gateway/...)를 통해 호출합니다. (CORS 회피)
 */
import type { AptTransaction, IngestResult, MarketStat, QueryParams } from "./types";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = "";
    try {
      detail = await res.text();
    } catch {
      /* ignore */
    }
    throw new Error(
      `요청 실패 (${res.status} ${res.statusText})${detail ? `: ${detail.slice(0, 300)}` : ""}`,
    );
  }
  return (await res.json()) as T;
}

/**
 * 실거래 수집 트리거. 수집은 lawdCd 파라미터명을 씁니다.
 * @returns upserted 건수를 포함한 결과 (재수집 시 멱등으로 0)
 */
export async function ingestAptTrade(
  lawdCd: string,
  dealYmd: string,
): Promise<IngestResult> {
  const qs = new URLSearchParams({ lawdCd, dealYmd });
  const res = await fetch(`/api/gateway/ingest/apt-trade?${qs.toString()}`, {
    method: "POST",
  });
  return handle<IngestResult>(res);
}

/** 거래원장 조회. 조회는 sggCd 파라미터명을 씁니다. */
export async function getTransactions(
  params: QueryParams,
): Promise<AptTransaction[]> {
  const qs = new URLSearchParams({
    sggCd: params.sggCd,
    dealYear: String(params.dealYear),
    dealMonth: String(params.dealMonth),
  });
  const res = await fetch(`/api/gateway/transactions?${qs.toString()}`, {
    cache: "no-store",
  });
  return handle<AptTransaction[]>(res);
}

/** 시세 통계 조회. 조회는 sggCd 파라미터명을 씁니다. */
export async function getMarketStats(params: QueryParams): Promise<MarketStat> {
  const qs = new URLSearchParams({
    sggCd: params.sggCd,
    dealYear: String(params.dealYear),
    dealMonth: String(params.dealMonth),
  });
  const res = await fetch(`/api/gateway/market-stats?${qs.toString()}`, {
    cache: "no-store",
  });
  return handle<MarketStat>(res);
}
