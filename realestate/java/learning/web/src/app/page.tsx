import Link from "next/link";
import { Download, Table2, BarChart3, ArrowRight } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const FEATURES = [
  {
    href: "/ingest",
    title: "데이터 수집",
    desc: "지역코드(lawdCd)와 계약월(dealYmd)로 국토부 실거래를 수집합니다. 멱등 적재라 재실행해도 안전합니다.",
    icon: Download,
    cta: "수집 시작",
  },
  {
    href: "/transactions",
    title: "거래 조회",
    desc: "시군구코드·년·월로 거래 원장을 조회합니다. 동/단지 검색, 면적 필터, 정렬, 페이징을 지원합니다.",
    icon: Table2,
    cta: "거래 보기",
  },
  {
    href: "/analytics",
    title: "시세 분석",
    desc: "해제거래를 제외한 거래건수·중위가·㎡당 단가를 집계하고 가격 분포 차트를 그립니다.",
    icon: BarChart3,
    cta: "분석 보기",
  },
] as const;

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="space-y-3">
        <span className="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary">
          MSA 게이트웨이 연동 데모
        </span>
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          아파트 실거래, 수집부터 시세 분석까지
        </h1>
        <p className="max-w-2xl text-muted-foreground">
          수집 · 거래원장 · 분석 세 마이크로서비스를 API 게이트웨이로 통합한
          부동산 데이터 파이프라인입니다. 아래 세 화면에서 전체 흐름을
          체험하세요.
        </p>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {FEATURES.map((f) => {
          const Icon = f.icon;
          return (
            <Link key={f.href} href={f.href} className="group">
              <Card className="h-full transition-all group-hover:border-primary/40 group-hover:shadow-md">
                <CardHeader>
                  <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <CardTitle>{f.title}</CardTitle>
                  <CardDescription>{f.desc}</CardDescription>
                </CardHeader>
                <CardContent>
                  <span className="inline-flex items-center gap-1 text-sm font-medium text-primary">
                    {f.cta}
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </section>

      <section className="rounded-xl border bg-muted/30 p-6">
        <h2 className="mb-2 text-sm font-semibold">사용 순서</h2>
        <ol className="space-y-1 text-sm text-muted-foreground">
          <li>
            1. <span className="font-medium text-foreground">수집</span> 화면에서
            지역·월 데이터를 적재합니다. (예: lawdCd 11110, dealYmd 202405)
          </li>
          <li>
            2. <span className="font-medium text-foreground">거래</span> 화면에서
            동일 코드를 sggCd로 조회해 원장을 확인합니다.
          </li>
          <li>
            3. <span className="font-medium text-foreground">분석</span> 화면에서
            시세 통계와 가격 분포를 살펴봅니다.
          </li>
        </ol>
      </section>
    </div>
  );
}
