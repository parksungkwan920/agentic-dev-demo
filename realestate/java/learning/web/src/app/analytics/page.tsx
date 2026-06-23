"use client";

import * as React from "react";
import { toast } from "sonner";
import {
  CartesianGrid,
  Scatter,
  ScatterChart,
  XAxis,
  YAxis,
  ZAxis,
  Cell,
} from "recharts";
import { Hash, TrendingUp, Ruler } from "lucide-react";

import { getMarketStats, getTransactions } from "@/lib/api";
import type { AptTransaction, MarketStat, QueryParams } from "@/lib/types";
import {
  formatWon,
  formatPerM2,
  formatWonShort,
  formatAreaShort,
} from "@/lib/format";
import { QueryForm } from "@/components/query-form";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

const chartConfig = {
  price: {
    label: "거래금액",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig;

interface ScatterPoint {
  area: number;
  price: number;
  aptNm: string;
  canceled: boolean;
}

export default function AnalyticsPage() {
  const [loading, setLoading] = React.useState(false);
  const [searched, setSearched] = React.useState(false);
  const [stat, setStat] = React.useState<MarketStat | null>(null);
  const [points, setPoints] = React.useState<ScatterPoint[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  async function analyze(params: QueryParams) {
    setLoading(true);
    setError(null);
    try {
      const [marketStat, txs] = await Promise.all([
        getMarketStats(params),
        getTransactions(params),
      ]);
      setStat(marketStat);
      setPoints(
        txs
          .filter((t: AptTransaction) => t.exclusiveArea > 0)
          .map((t) => ({
            area: Number(t.exclusiveArea.toFixed(2)),
            price: t.dealAmountWon,
            aptNm: t.aptNm,
            canceled: t.canceled,
          })),
      );
      setSearched(true);
      toast.success(
        `시세 분석 완료 — 유효거래 ${marketStat.tradeCount.toLocaleString()}건`,
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setStat(null);
      setPoints([]);
      toast.error("분석 실패", { description: msg });
    } finally {
      setLoading(false);
    }
  }

  const validPoints = points.filter((p) => !p.canceled);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">시세 분석</h1>
        <p className="text-sm text-muted-foreground">
          해제거래를 제외한 거래건수·중위가·㎡당 중위단가를 집계하고, 전용면적과
          거래금액의 산점도를 그립니다.
        </p>
      </div>

      <QueryForm
        testPrefix="an"
        searchTestId="btn-analyze"
        submitLabel="분석"
        loading={loading}
        onSubmit={analyze}
      />

      {error && (
        <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {searched && stat && !error && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <StatCard
              testId="stat-tradecount"
              icon={<Hash className="h-5 w-5" />}
              label="유효 거래건수"
              value={`${stat.tradeCount.toLocaleString()}건`}
              hint="해제거래 제외"
            />
            <StatCard
              testId="stat-median"
              icon={<TrendingUp className="h-5 w-5" />}
              label="중위 거래금액"
              value={formatWon(stat.medianPriceWon)}
              hint="중앙값 기준"
            />
            <StatCard
              testId="stat-perm2"
              icon={<Ruler className="h-5 w-5" />}
              label="㎡당 중위단가"
              value={formatPerM2(stat.medianPricePerM2Won)}
              hint="중앙값 기준"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                면적 - 가격 산점도
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  전용면적(㎡) 대비 거래금액 분포
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {validPoints.length === 0 ? (
                <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
                  표시할 유효 거래 데이터가 없습니다.
                </div>
              ) : (
                <div data-testid="price-chart">
                  <ChartContainer
                    config={chartConfig}
                    className="aspect-[16/7] w-full"
                  >
                    <ScatterChart
                      margin={{ top: 10, right: 16, bottom: 24, left: 8 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        type="number"
                        dataKey="area"
                        name="전용면적"
                        unit="㎡"
                        tickLine={false}
                        axisLine={false}
                        tickMargin={8}
                        domain={["dataMin - 5", "dataMax + 5"]}
                      />
                      <YAxis
                        type="number"
                        dataKey="price"
                        name="거래금액"
                        tickLine={false}
                        axisLine={false}
                        tickMargin={8}
                        width={56}
                        tickFormatter={(v) => formatWonShort(Number(v))}
                      />
                      <ZAxis range={[60, 60]} />
                      <ChartTooltip
                        cursor={{ strokeDasharray: "3 3" }}
                        content={
                          <ChartTooltipContent
                            formatter={(value, name) =>
                              name === "거래금액"
                                ? formatWon(Number(value))
                                : formatAreaShort(Number(value))
                            }
                          />
                        }
                      />
                      <Scatter
                        name="거래"
                        data={points}
                        fillOpacity={0.75}
                      >
                        {points.map((p, i) => (
                          <Cell
                            key={i}
                            fill={
                              p.canceled
                                ? "hsl(var(--destructive))"
                                : "hsl(var(--chart-1))"
                            }
                          />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ChartContainer>
                  <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="h-2.5 w-2.5 rounded-full bg-[hsl(var(--chart-1))]" />
                      정상 거래
                    </span>
                    <span className="inline-flex items-center gap-1.5">
                      <span className="h-2.5 w-2.5 rounded-full bg-[hsl(var(--destructive))]" />
                      해제 거래 (집계 제외)
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function StatCard({
  testId,
  icon,
  label,
  value,
  hint,
}: {
  testId: string;
  icon: React.ReactNode;
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <Card data-testid={testId}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        <span className="text-primary">{icon}</span>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
      </CardContent>
    </Card>
  );
}
