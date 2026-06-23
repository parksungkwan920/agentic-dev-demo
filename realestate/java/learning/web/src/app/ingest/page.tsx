"use client";

import * as React from "react";
import { toast } from "sonner";
import { Download, Loader2, RefreshCw, CheckCircle2 } from "lucide-react";

import { ingestAptTrade } from "@/lib/api";
import type { IngestResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const LAWD_PATTERN = /^\d{5}$/;
const YMD_PATTERN = /^\d{6}$/;

export default function IngestPage() {
  const [lawdCd, setLawdCd] = React.useState("11110");
  const [dealYmd, setDealYmd] = React.useState("202405");
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<IngestResult | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const lawdValid = LAWD_PATTERN.test(lawdCd);
  const ymdValid = YMD_PATTERN.test(dealYmd);
  const canSubmit = lawdValid && ymdValid && !loading;

  async function runIngest() {
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      const res = await ingestAptTrade(lawdCd, dealYmd);
      setResult(res);
      if (res.upserted > 0) {
        toast.success(`수집 완료 — ${res.upserted.toLocaleString()}건 신규 적재`);
      } else {
        toast.info("이미 적재된 데이터입니다 (멱등: 신규 0건)");
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      toast.error("수집 실패", { description: msg });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">데이터 수집</h1>
        <p className="text-sm text-muted-foreground">
          지역코드와 계약월로 국토부 아파트 실거래를 수집합니다. 동일 조건을
          다시 수집해도 멱등하게 처리됩니다(신규 0건).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>수집 트리거</CardTitle>
          <CardDescription>
            lawdCd는 5자리 법정동 시군구코드, dealYmd는 YYYYMM 형식입니다.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="lawdCd">지역코드 (lawdCd)</Label>
              <Input
                id="lawdCd"
                data-testid="ingest-lawdcd"
                inputMode="numeric"
                maxLength={5}
                placeholder="11110"
                value={lawdCd}
                onChange={(e) =>
                  setLawdCd(e.target.value.replace(/[^0-9]/g, "").slice(0, 5))
                }
                aria-invalid={lawdCd.length > 0 && !lawdValid}
              />
              {lawdCd.length > 0 && !lawdValid && (
                <p className="text-xs text-destructive">5자리 숫자여야 합니다.</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="dealYmd">계약월 (dealYmd)</Label>
              <Input
                id="dealYmd"
                data-testid="ingest-dealymd"
                inputMode="numeric"
                maxLength={6}
                placeholder="202405"
                value={dealYmd}
                onChange={(e) =>
                  setDealYmd(e.target.value.replace(/[^0-9]/g, "").slice(0, 6))
                }
                aria-invalid={dealYmd.length > 0 && !ymdValid}
              />
              {dealYmd.length > 0 && !ymdValid && (
                <p className="text-xs text-destructive">
                  YYYYMM 6자리여야 합니다.
                </p>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              data-testid="btn-ingest"
              onClick={runIngest}
              disabled={!canSubmit}
            >
              {loading ? (
                <Loader2 className="animate-spin" />
              ) : (
                <Download />
              )}
              수집하기
            </Button>
            <Button
              variant="outline"
              onClick={runIngest}
              disabled={!canSubmit || !result}
              title="동일 조건으로 다시 수집해 멱등성을 확인합니다"
            >
              <RefreshCw />한 번 더 수집
            </Button>
          </div>
        </CardContent>
      </Card>

      {result && (
        <Card
          data-testid="ingest-result"
          className="border-primary/30 bg-primary/5"
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <CheckCircle2 className="h-5 w-5 text-primary" />
              수집 결과
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-3 gap-3 text-center">
              <Stat label="지역코드" value={result.lawdCd} />
              <Stat label="계약월" value={result.dealYmd} />
              <Stat
                label="신규 적재 (upserted)"
                value={`${result.upserted.toLocaleString()}건`}
                accent
              />
            </div>
            <p className="text-sm text-muted-foreground">
              {result.upserted > 0
                ? `${result.upserted.toLocaleString()}건이 새로 적재되었습니다. 같은 조건으로 다시 수집하면 신규 건수가 0이 됩니다(멱등).`
                : "신규 적재 0건 — 이미 동일 데이터가 적재되어 있습니다(멱등 동작 확인됨)."}
            </p>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="pt-6 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-lg border bg-background p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div
        className={
          accent
            ? "mt-1 text-lg font-bold text-primary"
            : "mt-1 text-lg font-semibold"
        }
      >
        {value}
      </div>
    </div>
  );
}
