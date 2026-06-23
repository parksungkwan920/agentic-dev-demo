"use client";

import * as React from "react";
import { Search, Loader2 } from "lucide-react";

import type { QueryParams } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface QueryFormProps {
  /** data-testid 접두어 ("tx" 또는 "an") */
  testPrefix: "tx" | "an";
  /** 조회 버튼 testid */
  searchTestId: string;
  /** 조회 버튼 라벨 */
  submitLabel: string;
  loading: boolean;
  onSubmit: (params: QueryParams) => void;
  defaultValues?: Partial<QueryParams>;
}

const SGG_PATTERN = /^\d{5}$/;

export function QueryForm({
  testPrefix,
  searchTestId,
  submitLabel,
  loading,
  onSubmit,
  defaultValues,
}: QueryFormProps) {
  const [sggCd, setSggCd] = React.useState(defaultValues?.sggCd ?? "11110");
  const [dealYear, setDealYear] = React.useState(
    String(defaultValues?.dealYear ?? 2024),
  );
  const [dealMonth, setDealMonth] = React.useState(
    String(defaultValues?.dealMonth ?? 5),
  );

  const sggValid = SGG_PATTERN.test(sggCd);
  const yearNum = Number(dealYear);
  const monthNum = Number(dealMonth);
  const yearValid = yearNum >= 2006 && yearNum <= 2100;
  const monthValid = monthNum >= 1 && monthNum <= 12;
  const canSubmit = sggValid && yearValid && monthValid && !loading;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onSubmit({ sggCd, dealYear: yearNum, dealMonth: monthNum });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-wrap items-end gap-3 rounded-xl border bg-card p-4"
    >
      <div className="space-y-1.5">
        <Label htmlFor={`${testPrefix}-sggcd`}>시군구코드 (sggCd)</Label>
        <Input
          id={`${testPrefix}-sggcd`}
          data-testid={`${testPrefix}-sggcd`}
          className="w-36"
          inputMode="numeric"
          maxLength={5}
          placeholder="11110"
          value={sggCd}
          onChange={(e) =>
            setSggCd(e.target.value.replace(/[^0-9]/g, "").slice(0, 5))
          }
          aria-invalid={sggCd.length > 0 && !sggValid}
        />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor={`${testPrefix}-year`}>계약년</Label>
        <Input
          id={`${testPrefix}-year`}
          data-testid={`${testPrefix}-year`}
          className="w-28"
          inputMode="numeric"
          maxLength={4}
          placeholder="2024"
          value={dealYear}
          onChange={(e) =>
            setDealYear(e.target.value.replace(/[^0-9]/g, "").slice(0, 4))
          }
          aria-invalid={dealYear.length > 0 && !yearValid}
        />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor={`${testPrefix}-month`}>계약월</Label>
        <Input
          id={`${testPrefix}-month`}
          data-testid={`${testPrefix}-month`}
          className="w-24"
          inputMode="numeric"
          maxLength={2}
          placeholder="5"
          value={dealMonth}
          onChange={(e) =>
            setDealMonth(e.target.value.replace(/[^0-9]/g, "").slice(0, 2))
          }
          aria-invalid={dealMonth.length > 0 && !monthValid}
        />
      </div>
      <Button type="submit" data-testid={searchTestId} disabled={!canSubmit}>
        {loading ? <Loader2 className="animate-spin" /> : <Search />}
        {submitLabel}
      </Button>
    </form>
  );
}
