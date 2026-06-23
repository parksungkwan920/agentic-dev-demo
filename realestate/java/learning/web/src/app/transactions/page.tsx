"use client";

import * as React from "react";
import { toast } from "sonner";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

import { getTransactions } from "@/lib/api";
import type { AptTransaction, QueryParams } from "@/lib/types";
import {
  formatWon,
  formatAreaShort,
  formatDealDate,
  formatPerM2,
} from "@/lib/format";
import { QueryForm } from "@/components/query-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type SortKey =
  | "umdNm"
  | "aptNm"
  | "exclusiveArea"
  | "floor"
  | "dealDay"
  | "dealAmountWon";
type SortDir = "asc" | "desc";

const PAGE_SIZES = [10, 20, 50] as const;

export default function TransactionsPage() {
  const [loading, setLoading] = React.useState(false);
  const [searched, setSearched] = React.useState(false);
  const [rows, setRows] = React.useState<AptTransaction[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  const [keyword, setKeyword] = React.useState("");
  const [includeCanceled, setIncludeCanceled] = React.useState(true);
  const [minArea, setMinArea] = React.useState("");
  const [maxArea, setMaxArea] = React.useState("");

  const [sortKey, setSortKey] = React.useState<SortKey>("dealDay");
  const [sortDir, setSortDir] = React.useState<SortDir>("asc");
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState<number>(20);

  async function search(params: QueryParams) {
    setLoading(true);
    setError(null);
    try {
      const data = await getTransactions(params);
      setRows(data);
      setSearched(true);
      setPage(1);
      toast.success(`거래 ${data.length.toLocaleString()}건 조회`);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setRows([]);
      toast.error("조회 실패", { description: msg });
    } finally {
      setLoading(false);
    }
  }

  const filtered = React.useMemo(() => {
    const kw = keyword.trim().toLowerCase();
    const min = minArea === "" ? null : Number(minArea);
    const max = maxArea === "" ? null : Number(maxArea);
    return rows.filter((r) => {
      if (!includeCanceled && r.canceled) return false;
      if (kw && !(`${r.umdNm} ${r.aptNm}`.toLowerCase().includes(kw)))
        return false;
      if (min != null && !Number.isNaN(min) && r.exclusiveArea < min)
        return false;
      if (max != null && !Number.isNaN(max) && r.exclusiveArea > max)
        return false;
      return true;
    });
  }, [rows, keyword, includeCanceled, minArea, maxArea]);

  const sorted = React.useMemo(() => {
    const copy = [...filtered];
    copy.sort((a, b) => {
      let av: number | string;
      let bv: number | string;
      if (sortKey === "umdNm" || sortKey === "aptNm") {
        av = a[sortKey];
        bv = b[sortKey];
        const cmp = String(av).localeCompare(String(bv), "ko");
        return sortDir === "asc" ? cmp : -cmp;
      }
      av = a[sortKey];
      bv = b[sortKey];
      const cmp = (av as number) - (bv as number);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return copy;
  }, [filtered, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageRows = sorted.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  const canceledCount = rows.filter((r) => r.canceled).length;

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">거래 조회</h1>
        <p className="text-sm text-muted-foreground">
          시군구코드·년·월로 거래 원장을 조회합니다. 결과는 동/단지 검색, 면적
          범위, 해제거래 포함 여부로 필터링할 수 있습니다.
        </p>
      </div>

      <QueryForm
        testPrefix="tx"
        searchTestId="btn-search"
        submitLabel="조회"
        loading={loading}
        onSubmit={search}
      />

      {error && (
        <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {searched && !error && (
        <>
          <div className="flex flex-wrap items-end gap-4 rounded-xl border bg-muted/30 p-4">
            <div className="space-y-1.5">
              <Label htmlFor="tx-keyword">동/단지 검색</Label>
              <Input
                id="tx-keyword"
                className="w-56"
                placeholder="예: 청운동, 래미안"
                value={keyword}
                onChange={(e) => {
                  setKeyword(e.target.value);
                  setPage(1);
                }}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="tx-minarea">최소 면적(㎡)</Label>
              <Input
                id="tx-minarea"
                className="w-28"
                inputMode="decimal"
                placeholder="0"
                value={minArea}
                onChange={(e) => {
                  setMinArea(e.target.value.replace(/[^0-9.]/g, ""));
                  setPage(1);
                }}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="tx-maxarea">최대 면적(㎡)</Label>
              <Input
                id="tx-maxarea"
                className="w-28"
                inputMode="decimal"
                placeholder="200"
                value={maxArea}
                onChange={(e) => {
                  setMaxArea(e.target.value.replace(/[^0-9.]/g, ""));
                  setPage(1);
                }}
              />
            </div>
            <div className="flex items-center gap-2 pb-2">
              <Switch
                id="filter-canceled"
                data-testid="filter-canceled"
                checked={includeCanceled}
                onCheckedChange={(v) => {
                  setIncludeCanceled(v);
                  setPage(1);
                }}
              />
              <Label htmlFor="filter-canceled" className="cursor-pointer">
                해제거래 포함
                {canceledCount > 0 && (
                  <span className="ml-1 text-xs text-muted-foreground">
                    ({canceledCount}건)
                  </span>
                )}
              </Label>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-muted-foreground">
              전체 {rows.length.toLocaleString()}건 중{" "}
              <span className="font-medium text-foreground">
                {sorted.length.toLocaleString()}건
              </span>{" "}
              표시
            </p>
            <div className="flex items-center gap-2">
              <Label htmlFor="tx-pagesize" className="text-muted-foreground">
                페이지당
              </Label>
              <Select
                value={String(pageSize)}
                onValueChange={(v) => {
                  setPageSize(Number(v));
                  setPage(1);
                }}
              >
                <SelectTrigger id="tx-pagesize" className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PAGE_SIZES.map((s) => (
                    <SelectItem key={s} value={String(s)}>
                      {s}개
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="rounded-xl border">
            <Table data-testid="transactions-table">
              <TableHeader>
                <TableRow>
                  <SortHeader
                    label="법정동"
                    active={sortKey === "umdNm"}
                    dir={sortDir}
                    onClick={() => toggleSort("umdNm")}
                  />
                  <SortHeader
                    label="단지명"
                    active={sortKey === "aptNm"}
                    dir={sortDir}
                    onClick={() => toggleSort("aptNm")}
                  />
                  <SortHeader
                    label="전용면적"
                    active={sortKey === "exclusiveArea"}
                    dir={sortDir}
                    onClick={() => toggleSort("exclusiveArea")}
                    className="text-right"
                  />
                  <SortHeader
                    label="층"
                    active={sortKey === "floor"}
                    dir={sortDir}
                    onClick={() => toggleSort("floor")}
                    className="text-right"
                  />
                  <SortHeader
                    label="계약일"
                    active={sortKey === "dealDay"}
                    dir={sortDir}
                    onClick={() => toggleSort("dealDay")}
                  />
                  <SortHeader
                    label="거래금액"
                    active={sortKey === "dealAmountWon"}
                    dir={sortDir}
                    onClick={() => toggleSort("dealAmountWon")}
                    className="text-right"
                  />
                  <TableHead className="text-right">㎡당</TableHead>
                  <TableHead>상태</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pageRows.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={8}
                      className="h-24 text-center text-muted-foreground"
                    >
                      조건에 맞는 거래가 없습니다.
                    </TableCell>
                  </TableRow>
                ) : (
                  pageRows.map((r, i) => {
                    const perM2 =
                      r.exclusiveArea > 0
                        ? r.dealAmountWon / r.exclusiveArea
                        : 0;
                    return (
                      <TableRow
                        key={`${r.aptNm}-${r.dealDay}-${r.floor}-${r.dealAmountWon}-${i}`}
                        data-testid="tx-row"
                        className={r.canceled ? "opacity-70" : undefined}
                      >
                        <TableCell>{r.umdNm}</TableCell>
                        <TableCell className="font-medium">
                          {r.aptNm}
                          <span className="ml-1 text-xs text-muted-foreground">
                            ({r.buildYear})
                          </span>
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {formatAreaShort(r.exclusiveArea)}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {r.floor}층
                        </TableCell>
                        <TableCell className="tabular-nums">
                          {formatDealDate(r.dealYear, r.dealMonth, r.dealDay)}
                        </TableCell>
                        <TableCell className="text-right font-medium tabular-nums">
                          {formatWon(r.dealAmountWon)}
                        </TableCell>
                        <TableCell className="text-right tabular-nums text-muted-foreground">
                          {formatPerM2(perM2)}
                        </TableCell>
                        <TableCell>
                          {r.canceled ? (
                            <Badge
                              variant="destructive"
                              data-testid="cancel-badge"
                            >
                              해제
                            </Badge>
                          ) : (
                            <Badge variant="secondary">정상</Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>

          {sorted.length > 0 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {currentPage} / {totalPages} 페이지
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  이전
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  다음
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function SortHeader({
  label,
  active,
  dir,
  onClick,
  className,
}: {
  label: string;
  active: boolean;
  dir: SortDir;
  onClick: () => void;
  className?: string;
}) {
  return (
    <TableHead className={className}>
      <button
        type="button"
        onClick={onClick}
        className="inline-flex items-center gap-1 font-medium hover:text-foreground"
      >
        {label}
        {active ? (
          dir === "asc" ? (
            <ArrowUp className="h-3.5 w-3.5" />
          ) : (
            <ArrowDown className="h-3.5 w-3.5" />
          )
        ) : (
          <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />
        )}
      </button>
    </TableHead>
  );
}
