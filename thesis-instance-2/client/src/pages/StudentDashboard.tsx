import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import {
  FileCheck, CheckCircle, LogOut, Globe, GraduationCap, Settings,
  Upload, FileEdit, BookOpen, ShoppingCart, LucideIcon, Clock,
  AlertCircle, CircleDot, Loader2, XCircle, ArrowRight, NotebookPen,
} from "lucide-react";
import { useEffect, ReactNode, useMemo } from "react";

// ── Section wrapper ──
function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="mb-10">
      <div className="flex items-center gap-3 mb-4">
        <div className="h-px flex-1 bg-gray-200" />
        <h2 className="text-base font-semibold text-gray-500 tracking-wide whitespace-nowrap">
          {title}
        </h2>
        <div className="h-px flex-1 bg-gray-200" />
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {children}
      </div>
    </div>
  );
}

// ── Module card ──
function ModuleCard({
  icon: Icon, iconBg, iconColor, title, description, onClick, badge, actionButton, disabled,
}: {
  icon: LucideIcon; iconBg: string; iconColor: string; title: string; description: string;
  onClick: () => void; badge?: ReactNode; actionButton?: ReactNode; disabled?: boolean;
}) {
  return (
    <Card
      className={`hover:shadow-lg transition-shadow relative group ${disabled ? "opacity-60" : "cursor-pointer"}`}
      onClick={disabled ? undefined : onClick}
    >
      {badge}
      <CardHeader>
        <div className={`w-12 h-12 ${iconBg} rounded-lg flex items-center justify-center mb-4 transition-transform group-hover:scale-105`}>
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      {actionButton && <CardContent>{actionButton}</CardContent>}
    </Card>
  );
}

// ── 时间阶段提示横幅 ──
function TimePhaseBar({ phase, extendedPhase, phaseData, isZh }: {
  phase: string;
  extendedPhase: string;
  phaseData: {
    topicPublishStart?: string | null;
    topicPublishEnd?: string | null;
    studentSelectionStart?: string | null;
    studentSelectionEnd?: string | null;
    teacherConfirmStart?: string | null;
    teacherConfirmEnd?: string | null;
    thesisUploadStart?: string | null;
    thesisUploadEnd?: string | null;
    scoringStart?: string | null;
    scoringEnd?: string | null;
  };
  isZh: boolean;
}) {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return d.toLocaleDateString(isZh ? "zh-CN" : "en-US", {
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit",
    });
  };

  const phaseConfig: Record<string, { label: string; labelEn: string; bg: string; border: string; text: string; icon: typeof Clock; dateRange?: string }> = {
    topic_publish: {
      label: "当前处于 — 导师发布题目阶段",
      labelEn: "Current Phase — Topic Publishing Period",
      bg: "bg-teal-50", border: "border-teal-300", text: "text-teal-800", icon: NotebookPen,
      dateRange: phaseData.topicPublishStart && phaseData.topicPublishEnd
        ? `${formatDate(phaseData.topicPublishStart)} ~ ${formatDate(phaseData.topicPublishEnd)}`
        : undefined,
    },
    student_selection: {
      label: "当前处于 — 志愿填报阶段",
      labelEn: "Current Phase — Wish Submission Period",
      bg: "bg-blue-50", border: "border-blue-300", text: "text-blue-800", icon: FileCheck,
      dateRange: phaseData.studentSelectionStart && phaseData.studentSelectionEnd
        ? `${formatDate(phaseData.studentSelectionStart)} ~ ${formatDate(phaseData.studentSelectionEnd)}`
        : undefined,
    },
    teacher_confirm: {
      label: "当前处于 — 导师确认志愿阶段",
      labelEn: "Current Phase — Supervisor Confirmation Period",
      bg: "bg-amber-50", border: "border-amber-300", text: "text-amber-800", icon: Clock,
      dateRange: phaseData.teacherConfirmStart && phaseData.teacherConfirmEnd
        ? `${formatDate(phaseData.teacherConfirmStart)} ~ ${formatDate(phaseData.teacherConfirmEnd)}`
        : undefined,
    },
    thesis_upload: {
      label: "当前处于 — 论文提交阶段",
      labelEn: "Current Phase — Thesis Submission Period",
      bg: "bg-green-50", border: "border-green-300", text: "text-green-800", icon: Upload,
      dateRange: phaseData.thesisUploadStart && phaseData.thesisUploadEnd
        ? `${formatDate(phaseData.thesisUploadStart)} ~ ${formatDate(phaseData.thesisUploadEnd)}`
        : undefined,
    },
    scoring: {
      label: "当前处于 — 论文评分阶段",
      labelEn: "Current Phase — Thesis Scoring Period",
      bg: "bg-purple-50", border: "border-purple-300", text: "text-purple-800", icon: FileEdit,
      dateRange: phaseData.scoringStart && phaseData.scoringEnd
        ? `${formatDate(phaseData.scoringStart)} ~ ${formatDate(phaseData.scoringEnd)}`
        : undefined,
    },
    closed: {
      label: "当前阶段已结束",
      labelEn: "Current Phase — Closed",
      bg: "bg-gray-50", border: "border-gray-300", text: "text-gray-600", icon: Clock,
    },
    none: {
      label: "暂无进行中的阶段",
      labelEn: "No Active Phase",
      bg: "bg-gray-50", border: "border-gray-300", text: "text-gray-500", icon: Clock,
    },
  };

  // 优先使用 extendedPhase（包含论文上传/评分阶段）
  const displayPhase = extendedPhase || phase;
  const config = phaseConfig[displayPhase] || phaseConfig.none;
  const PhaseIcon = config.icon;

  return (
    <div className={`${config.bg} ${config.border} border rounded-xl px-5 py-4 mb-6 flex items-center gap-4`}>
      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${config.bg} ${config.text}`}>
        <PhaseIcon className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <p className={`font-semibold text-base ${config.text}`}>
          {isZh ? config.label : config.labelEn}
        </p>
        {config.dateRange && (
          <p className={`text-sm mt-0.5 ${config.text} opacity-75`}>
            {config.dateRange}
          </p>
        )}
      </div>
    </div>
  );
}

// ── 选题进度状态卡片 ──
function WishProgressCard({ wishes, match, currentReviewPriority, phase, isZh, onNavigate }: {
  wishes: any[] | undefined;
  match: any;
  currentReviewPriority: number;
  phase: string;
  isZh: boolean;
  onNavigate: (path: string) => void;
}) {
  // 计算进度状态
  const progressStatus = useMemo(() => {
    // 1. 已确认课题
    if (match) {
      return {
        key: "matched",
        icon: CheckCircle,
        iconColor: "text-green-600",
        iconBg: "bg-green-100",
        borderColor: "border-green-300",
        bgColor: "bg-green-50",
        title: isZh ? "已确认课题" : "Topic Confirmed",
        titleEn: "Topic Confirmed",
        description: isZh
          ? `您已成功匹配课题「${match.topic?.title || match.topic?.titleEn || ""}」，导师：${match.teacher?.name || ""}`
          : `Matched with topic "${match.topic?.titleEn || match.topic?.title || ""}", Supervisor: ${match.teacher?.name || ""}`,
        action: null,
      };
    }

    // 2. 志愿未提交
    if (!wishes || wishes.length === 0) {
      return {
        key: "not_submitted",
        icon: AlertCircle,
        iconColor: "text-gray-500",
        iconBg: "bg-gray-100",
        borderColor: "border-gray-300",
        bgColor: "bg-gray-50",
        title: isZh ? "志愿未提交" : "Wishes Not Submitted",
        titleEn: "Wishes Not Submitted",
        description: isZh
          ? "您尚未提交选题志愿，请尽快前往志愿填报页面完成填报。"
          : "You have not submitted your wishes yet. Please go to the wish submission page.",
        action: phase === "student_selection" ? {
          label: isZh ? "前往填报" : "Submit Now",
          path: "/student/wishes",
        } : null,
      };
    }

    // 3. 检查是否所有志愿都被拒绝
    const allRejected = wishes.every((w: any) => w.teacherDecision === "rejected");
    if (allRejected) {
      return {
        key: "all_rejected",
        icon: XCircle,
        iconColor: "text-red-600",
        iconBg: "bg-red-100",
        borderColor: "border-red-300",
        bgColor: "bg-red-50",
        title: isZh ? "志愿已全部落选" : "All Wishes Rejected",
        titleEn: "All Wishes Rejected",
        description: isZh
          ? "很遗憾，您提交的所有志愿均已被导师拒绝，请重新提交新的志愿。"
          : "Unfortunately, all your wishes have been rejected. Please submit new wishes.",
        action: phase === "student_selection" ? {
          label: isZh ? "重新填报" : "Resubmit",
          path: "/student/wishes",
        } : null,
      };
    }

    // 4. 有已批准的志愿（等待系统匹配）
    const hasApproved = wishes.some((w: any) => w.teacherDecision === "approved");
    if (hasApproved) {
      return {
        key: "approved_waiting",
        icon: CheckCircle,
        iconColor: "text-blue-600",
        iconBg: "bg-blue-100",
        borderColor: "border-blue-300",
        bgColor: "bg-blue-50",
        title: isZh ? "志愿已被导师接受" : "Wish Accepted by Supervisor",
        titleEn: "Wish Accepted",
        description: isZh
          ? "您有志愿已被导师接受，等待系统最终匹配确认。"
          : "Your wish has been accepted by the supervisor, waiting for final matching.",
        action: null,
      };
    }

    // 5. 志愿已提交，正在审核中
    const hasPending = wishes.some((w: any) => w.teacherDecision === "pending");
    if (hasPending && phase === "teacher_confirm") {
      // 显示当前审核轮次
      const roundLabel = currentReviewPriority > 0 && currentReviewPriority <= 6
        ? (isZh ? `第${currentReviewPriority}轮` : `Round ${currentReviewPriority}`)
        : "";
      return {
        key: "reviewing",
        icon: Loader2,
        iconColor: "text-amber-600",
        iconBg: "bg-amber-100",
        borderColor: "border-amber-300",
        bgColor: "bg-amber-50",
        title: isZh
          ? `志愿${roundLabel}导师确认中`
          : `Wishes Under Review ${roundLabel}`,
        titleEn: `Wishes Under Review ${roundLabel}`,
        description: isZh
          ? `您的志愿正在${roundLabel}导师确认阶段，请耐心等待导师审核结果。`
          : `Your wishes are under ${roundLabel} supervisor review. Please wait for the result.`,
        action: null,
      };
    }

    // 6. 志愿已提交（默认状态）
    return {
      key: "submitted",
      icon: CircleDot,
      iconColor: "text-blue-600",
      iconBg: "bg-blue-100",
      borderColor: "border-blue-300",
      bgColor: "bg-blue-50",
      title: isZh ? "志愿已提交" : "Wishes Submitted",
      titleEn: "Wishes Submitted",
      description: isZh
        ? `您已提交 ${wishes.length} 个志愿，等待进入导师确认阶段。`
        : `You have submitted ${wishes.length} wish(es), waiting for supervisor confirmation phase.`,
      action: phase === "student_selection" ? {
        label: isZh ? "修改志愿" : "Edit Wishes",
        path: "/student/wishes",
      } : null,
    };
  }, [wishes, match, currentReviewPriority, phase, isZh]);

  const StatusIcon = progressStatus.icon;

  return (
    <div className={`${progressStatus.bgColor} ${progressStatus.borderColor} border rounded-xl px-5 py-5 mb-6`}>
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${progressStatus.iconBg}`}>
          <StatusIcon className={`w-6 h-6 ${progressStatus.iconColor} ${progressStatus.key === "reviewing" ? "animate-spin" : ""}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-bold ${progressStatus.iconColor}`}>
            {progressStatus.title}
          </h3>
          <p className="text-sm text-gray-600 mt-1 leading-relaxed">
            {progressStatus.description}
          </p>
          {/* 志愿明细 */}
          {wishes && wishes.length > 0 && !match && (
            <div className="mt-3 space-y-1.5">
              {wishes.map((w: any, idx: number) => {
                const statusMap: Record<string, { label: string; color: string }> = {
                  pending: { label: isZh ? "待审核" : "Pending", color: "text-amber-600 bg-amber-50" },
                  approved: { label: isZh ? "已接受" : "Accepted", color: "text-green-600 bg-green-50" },
                  rejected: { label: isZh ? "已拒绝" : "Rejected", color: "text-red-600 bg-red-50" },
                };
                const st = statusMap[w.teacherDecision] || statusMap.pending;
                return (
                  <div key={w.id || idx} className="flex items-center gap-2 text-sm">
                    <span className="text-gray-400 font-medium w-16 flex-shrink-0">
                      {isZh ? `第${w.priority}志愿` : `Wish #${w.priority}`}
                    </span>
                    <span className="truncate text-gray-700 flex-1">
                      {w.topic?.title || w.topic?.titleEn || `Topic #${w.topicId}`}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${st.color}`}>
                      {st.label}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        {progressStatus.action && (
          <Button
            size="sm"
            className="flex-shrink-0 mt-1"
            onClick={() => onNavigate(progressStatus.action!.path)}
          >
            {progressStatus.action.label}
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        )}
      </div>
    </div>
  );
}

// ── 进度步骤条 ──
function ProgressSteps({ currentStep, isZh }: { currentStep: number; isZh: boolean }) {
  const steps = [
    { label: isZh ? "志愿填报" : "Submit Wishes", labelShort: isZh ? "填报" : "Submit" },
    { label: isZh ? "导师确认" : "Supervisor Review", labelShort: isZh ? "确认" : "Review" },
    { label: isZh ? "课题匹配" : "Topic Matching", labelShort: isZh ? "匹配" : "Match" },
    { label: isZh ? "论文阶段" : "Thesis Phase", labelShort: isZh ? "论文" : "Thesis" },
  ];

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between relative">
        {/* 连接线 */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 z-0" />
        <div
          className="absolute top-5 left-0 h-0.5 bg-blue-500 z-0 transition-all duration-500"
          style={{ width: `${Math.max(0, ((currentStep - 1) / (steps.length - 1)) * 100)}%` }}
        />
        {steps.map((step, idx) => {
          const stepNum = idx + 1;
          const isActive = stepNum === currentStep;
          const isCompleted = stepNum < currentStep;
          return (
            <div key={idx} className="flex flex-col items-center z-10 relative">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                  isCompleted
                    ? "bg-blue-600 text-white"
                    : isActive
                    ? "bg-blue-600 text-white ring-4 ring-blue-100"
                    : "bg-white text-gray-400 border-2 border-gray-200"
                }`}
              >
                {isCompleted ? <CheckCircle className="w-5 h-5" /> : stepNum}
              </div>
              <span className={`mt-2 text-xs font-medium ${isActive ? "text-blue-700" : isCompleted ? "text-blue-600" : "text-gray-400"}`}>
                <span className="hidden sm:inline">{step.label}</span>
                <span className="sm:hidden">{step.labelShort}</span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function StudentDashboard() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  const { data: wishes } = trpc.wish.myWishes.useQuery(undefined, { enabled: isAuthenticated });
  const { data: match } = trpc.match.myMatch.useQuery(undefined, { enabled: isAuthenticated });
  const { data: wishStatus } = trpc.match.myWishStatus.useQuery(undefined, { enabled: isAuthenticated });
  const { data: phaseData } = trpc.admin.getCurrentPhase.useQuery(undefined, { enabled: isAuthenticated });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "student" && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const handleLogout = async () => { await logout(); setLocation("/"); };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  const isZh = language === "zh";
  const isTransfer = user?.studentType === "transfer";
  const phase = phaseData?.phase || "none";
  const extendedPhase = phaseData?.extendedPhase || phase;
  const currentReviewPriority = phaseData?.currentReviewPriority ?? 0;

  // 计算当前进度步骤
  const currentStep = (() => {
    if (match) return 4; // 已匹配，进入论文阶段
    if (wishStatus && wishStatus.some((w: any) => w.teacherDecision === "approved")) return 3; // 已被接受
    if (phase === "teacher_confirm") return 2; // 导师确认阶段
    if (wishes && wishes.length > 0) return 2; // 已提交志愿
    return 1; // 志愿填报
  })();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center"><GraduationCap className="w-6 h-6 text-white" /></div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.name} ({t.roles.student})</span>
            <Button variant="ghost" size="sm" onClick={() => setLanguage(isZh ? "en" : "zh")}><Globe className="w-4 h-4 mr-2" />{isZh ? "EN" : "中"}</Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}><LogOut className="w-4 h-4 mr-2" />{t.logout}</Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">{isZh ? "学生控制台" : "Student Dashboard"}</h1>

        {/* ══ 时间阶段提示横幅 ══ */}
        {phaseData && (
          <TimePhaseBar
            phase={phase}
            extendedPhase={extendedPhase}
            phaseData={phaseData}
            isZh={isZh}
          />
        )}

        {/* ══ 进度步骤条 ══ */}
        <ProgressSteps currentStep={currentStep} isZh={isZh} />

        {/* ══ 选题进度状态卡片 ══ */}
        <WishProgressCard
          wishes={wishStatus}
          match={match}
          currentReviewPriority={currentReviewPriority}
          phase={phase}
          isZh={isZh}
          onNavigate={setLocation}
        />

        {/* ── Summary cards ── */}
        <div className="grid md:grid-cols-3 gap-4 mb-10">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-600">{isZh ? "已填志愿数" : "Wishes"}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{wishes?.length || 0}</div></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-600">{isZh ? "最大志愿数" : "Max"}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">3</div></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-600">{isZh ? "匹配状态" : "Status"}</CardTitle></CardHeader><CardContent><div className={`text-lg font-bold ${match ? "text-green-600" : "text-yellow-600"}`}>{match ? (isZh ? "已匹配" : "Matched") : (isZh ? "待匹配" : "Pending")}</div></CardContent></Card>
        </div>

        {/* ═══ Section 1 — 选题相关 ═══ */}
        <Section title={isZh ? "选题相关" : "Topic Selection"}>
          <ModuleCard
            icon={FileCheck}
            iconBg="bg-purple-100"
            iconColor="text-purple-600"
            title={isZh ? "志愿填报" : "Submit Wishes"}
            description={isZh ? "填报您的选题志愿和英文声明" : "Submit preferences"}
            onClick={() => setLocation("/student/wishes")}
            actionButton={
              <Button variant="outline" className="w-full">{wishes?.length ? (isZh ? "修改志愿" : "Edit") : (isZh ? "开始填报" : "Start")}</Button>
            }
          />
        </Section>

        {/* ═══ Section 2 — 论文与指导 (仅分流学生且已匹配时显示) ═══ */}
        {isTransfer && match && (
          <Section title={isZh ? "论文与指导" : "Thesis & Guidance"}>
            <ModuleCard
              icon={Upload}
              iconBg="bg-green-100"
              iconColor="text-green-600"
              title={isZh ? "论文终稿" : "Final Thesis"}
              description={isZh ? "上传您的毕业论文终稿" : "Upload your final thesis"}
              onClick={() => setLocation("/student/thesis")}
              actionButton={
                <Button variant="outline" className="w-full"><Upload className="w-4 h-4 mr-2" />{isZh ? "上传论文" : "Upload"}</Button>
              }
            />
            <ModuleCard
              icon={FileEdit}
              iconBg="bg-orange-100"
              iconColor="text-orange-600"
              title={isZh ? "题目修改" : "Title Change"}
              description={isZh ? "申请修改您的毕业设计题目" : "Request to change your topic title"}
              onClick={() => setLocation("/student/title-change")}
              actionButton={
                <Button variant="outline" className="w-full"><FileEdit className="w-4 h-4 mr-2" />{isZh ? "申请修改" : "Request"}</Button>
              }
            />
            <ModuleCard
              icon={BookOpen}
              iconBg="bg-indigo-100"
              iconColor="text-indigo-600"
              title={isZh ? "指导记录" : "Guidance Logs"}
              description={isZh ? "记录和管理您的导师指导过程" : "Record and manage your supervision sessions"}
              onClick={() => setLocation("/student/guidance")}
              actionButton={
                <Button variant="outline" className="w-full"><BookOpen className="w-4 h-4 mr-2" />{isZh ? "查看记录" : "View Logs"}</Button>
              }
            />
          </Section>
        )}

        {/* ═══ Section 3 — 其他功能 ═══ */}
        <Section title={isZh ? "其他功能" : "Other Features"}>
          <ModuleCard
            icon={ShoppingCart}
            iconBg="bg-teal-100"
            iconColor="text-teal-600"
            title={isZh ? "毕设采购" : "Purchase Request"}
            description={
              match
                ? (isZh ? "申请毕业设计相关耗材采购" : "Request thesis-related material purchase")
                : (isZh ? "需要先确认导师才能申请" : "Need confirmed supervisor first")
            }
            onClick={() => match ? setLocation("/student/purchase") : undefined}
            disabled={!match}
            actionButton={
              <Button variant="outline" className="w-full" disabled={!match}>
                <ShoppingCart className="w-4 h-4 mr-2" />
                {match ? (isZh ? "提交申请" : "Submit") : (isZh ? "暂不可用" : "Unavailable")}
              </Button>
            }
          />
          <ModuleCard
            icon={Settings}
            iconBg="bg-gray-100"
            iconColor="text-gray-600"
            title={isZh ? "账户设置" : "Account Settings"}
            description={isZh ? "查看个人信息，修改密码" : "View profile, change password"}
            onClick={() => setLocation("/settings")}
            actionButton={
              <Button variant="outline" className="w-full"><Settings className="w-4 h-4 mr-2" />{isZh ? "进入设置" : "Settings"}</Button>
            }
          />
        </Section>
      </main>
    </div>
  );
}
