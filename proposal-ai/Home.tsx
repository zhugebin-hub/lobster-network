import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import {
  FileText,
  Plus,
  ChevronRight,
  BookOpen,
  Sparkles,
  Clock,
  CheckCircle2,
  Loader2,
  FlaskConical,
  Microscope,
  GraduationCap,
  ArrowRight,
  LogIn,
} from "lucide-react";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";

const PROPOSAL_TYPE_LABELS: Record<string, string> = {
  national_key_rd: "国家重点研发计划",
  national_sci_tech: "国家科技重大专项",
  nsfc: "国家自然科学基金",
};

const PROPOSAL_TYPE_COLORS: Record<string, string> = {
  national_key_rd: "bg-blue-100 text-blue-700 border-blue-200",
  national_sci_tech: "bg-purple-100 text-purple-700 border-purple-200",
  nsfc: "bg-emerald-100 text-emerald-700 border-emerald-200",
};

function getProgressFromSections(sections: Array<{ status: string }>): number {
  if (!sections || sections.length === 0) return 0;
  const confirmed = sections.filter(s => s.status === "confirmed").length;
  return Math.round((confirmed / 17) * 100);
}

export default function Home() {
  const { user, loading, isAuthenticated } = useAuth();
  const [, navigate] = useLocation();

  const { data: proposals, isLoading: proposalsLoading } = trpc.proposal.list.useQuery(undefined, {
    enabled: isAuthenticated,
  });

  const deleteMutation = trpc.proposal.delete.useMutation({
    onSuccess: () => {
      toast.success("申报书已删除");
      utils.proposal.list.invalidate();
    },
    onError: (err) => toast.error(err.message),
  });

  const utils = trpc.useUtils();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航 */}
      <header className="sticky top-0 z-50 border-b border-border bg-white/80 backdrop-blur-md">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <FlaskConical className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <span className="text-lg font-bold text-foreground">科研申报书</span>
              <span className="ml-1 text-sm text-muted-foreground">AI智能助手</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-muted-foreground hidden sm:block">
                  欢迎，{user?.name || "研究员"}
                </span>
                <Button
                  onClick={() => navigate("/proposal/new")}
                  size="sm"
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  新建申报书
                </Button>
              </>
            ) : (
              <Button
                onClick={() => (window.location.href = getLoginUrl())}
                size="sm"
                className="gap-2"
              >
                <LogIn className="h-4 w-4" />
                登录
              </Button>
            )}
          </div>
        </div>
      </header>

      {!isAuthenticated ? (
        /* 未登录：展示落地页 */
        <div>
          {/* Hero Section */}
          <section className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950" />
            <div className="absolute inset-0 opacity-20"
              style={{
                backgroundImage: `radial-gradient(circle at 20% 50%, rgba(99,102,241,0.4) 0%, transparent 50%),
                  radial-gradient(circle at 80% 20%, rgba(59,130,246,0.3) 0%, transparent 50%),
                  radial-gradient(circle at 60% 80%, rgba(139,92,246,0.2) 0%, transparent 50%)`
              }}
            />
            <div className="relative container py-24 md:py-36">
              <div className="max-w-3xl">
                <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-400/30 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300">
                  <Sparkles className="h-3.5 w-3.5" />
                  基于国家重点研发计划官方模板
                </div>
                <h1 className="mb-6 text-4xl font-bold leading-tight text-white md:text-6xl">
                  AI 驱动的
                  <br />
                  <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                    科研申报书
                  </span>
                  <br />
                  智能撰写平台
                </h1>
                <p className="mb-10 text-lg text-slate-300 leading-relaxed max-w-2xl">
                  基于大语言模型，覆盖国家重点研发计划17个核心章节，从项目简介到组织实施，
                  全程AI辅助生成，让申报书撰写更高效、更专业。
                </p>
                <div className="flex flex-wrap gap-4">
                  <Button
                    size="lg"
                    onClick={() => (window.location.href = getLoginUrl())}
                    className="gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8"
                  >
                    <LogIn className="h-5 w-5" />
                    立即开始
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </section>

          {/* 功能特性 */}
          <section className="py-20 bg-background">
            <div className="container">
              <div className="text-center mb-14">
                <h2 className="text-3xl font-bold text-foreground mb-4">核心功能</h2>
                <p className="text-muted-foreground max-w-xl mx-auto">
                  专为科研人员设计，覆盖申报书撰写全流程
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    icon: <BookOpen className="h-6 w-6 text-blue-600" />,
                    title: "17章节全覆盖",
                    desc: "严格按照国家重点研发计划官方模板，涵盖项目简介、研究内容、可行性分析等全部17个章节。",
                    bg: "bg-blue-50",
                  },
                  {
                    icon: <Sparkles className="h-6 w-6 text-purple-600" />,
                    title: "AI智能生成",
                    desc: "基于大语言模型，根据项目信息自动生成专业内容，支持修改反馈和多轮迭代优化。",
                    bg: "bg-purple-50",
                  },
                  {
                    icon: <FileText className="h-6 w-6 text-emerald-600" />,
                    title: "Word文档导出",
                    desc: "一键导出符合官方规范的.docx格式文档，格式标准，可直接用于申报提交。",
                    bg: "bg-emerald-50",
                  },
                  {
                    icon: <CheckCircle2 className="h-6 w-6 text-amber-600" />,
                    title: "依赖关系管理",
                    desc: "智能检测章节依赖关系，确保生成顺序合理，前置章节内容自动作为后续章节的上下文。",
                    bg: "bg-amber-50",
                  },
                  {
                    icon: <Microscope className="h-6 w-6 text-rose-600" />,
                    title: "专业提示词库",
                    desc: "针对每个章节定制专业提示词，深度理解评审标准，生成内容符合科研申报规范。",
                    bg: "bg-rose-50",
                  },
                  {
                    icon: <GraduationCap className="h-6 w-6 text-indigo-600" />,
                    title: "多项目管理",
                    desc: "支持同时管理多个申报书项目，进度可视化，历史操作记录完整保存。",
                    bg: "bg-indigo-50",
                  },
                ].map((feature, i) => (
                  <Card key={i} className="border-border hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                      <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl ${feature.bg} mb-4`}>
                        {feature.icon}
                      </div>
                      <h3 className="font-semibold text-foreground mb-2">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">{feature.desc}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </section>

          {/* 申报类型 */}
          <section className="py-16 bg-slate-50">
            <div className="container">
              <div className="text-center mb-12">
                <h2 className="text-2xl font-bold text-foreground mb-3">支持的申报类型</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-3xl mx-auto">
                {Object.entries(PROPOSAL_TYPE_LABELS).map(([key, label]) => (
                  <div key={key} className={`rounded-xl border p-5 text-center ${PROPOSAL_TYPE_COLORS[key]}`}>
                    <div className="font-semibold">{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      ) : (
        /* 已登录：展示项目列表 */
        <div className="container py-10">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-foreground">我的申报书</h1>
              <p className="text-muted-foreground mt-1">管理您的科研项目申报书</p>
            </div>
            <Button onClick={() => navigate("/proposal/new")} className="gap-2">
              <Plus className="h-4 w-4" />
              新建申报书
            </Button>
          </div>

          {proposalsLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : !proposals || proposals.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10">
                <FileText className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">还没有申报书</h3>
              <p className="text-muted-foreground mb-6 max-w-sm">
                创建您的第一个科研申报书项目，AI将帮助您完成17个章节的专业内容撰写。
              </p>
              <Button onClick={() => navigate("/proposal/new")} size="lg" className="gap-2">
                <Plus className="h-5 w-5" />
                创建第一个申报书
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {proposals.map((proposal) => {
                const typeLabel = PROPOSAL_TYPE_LABELS[proposal.proposalType] || proposal.proposalType;
                const typeColor = PROPOSAL_TYPE_COLORS[proposal.proposalType] || "bg-slate-100 text-slate-700 border-slate-200";
                return (
                  <Card
                    key={proposal.id}
                    className="group cursor-pointer border-border hover:shadow-lg hover:border-primary/30 transition-all duration-200"
                    onClick={() => navigate(`/proposal/${proposal.id}`)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-base font-semibold text-foreground line-clamp-2 group-hover:text-primary transition-colors">
                          {proposal.title}
                        </CardTitle>
                        <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5 group-hover:text-primary transition-colors" />
                      </div>
                      <Badge variant="outline" className={`w-fit text-xs ${typeColor}`}>
                        {typeLabel}
                      </Badge>
                    </CardHeader>
                    <CardContent className="pt-0">
                      {proposal.abstract && (
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                          {proposal.abstract}
                        </p>
                      )}
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="h-3.5 w-3.5" />
                        <span>
                          {formatDistanceToNow(new Date(proposal.createdAt), {
                            addSuffix: true,
                            locale: zhCN,
                          })}
                        </span>
                        {proposal.applicantUnit && (
                          <>
                            <span className="text-border">·</span>
                            <span className="truncate">{proposal.applicantUnit}</span>
                          </>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}

              {/* 新建卡片 */}
              <Card
                className="cursor-pointer border-dashed border-2 border-border hover:border-primary/50 hover:bg-primary/5 transition-all duration-200 flex items-center justify-center min-h-[180px]"
                onClick={() => navigate("/proposal/new")}
              >
                <div className="text-center">
                  <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                    <Plus className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-foreground">新建申报书</p>
                  <p className="text-sm text-muted-foreground mt-1">开始新的科研项目</p>
                </div>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-border bg-white py-8 mt-auto">
        <div className="container text-center text-sm text-muted-foreground">
          <p>科研申报书AI智能助手 · 基于国家重点研发计划官方模板</p>
        </div>
      </footer>
    </div>
  );
}
