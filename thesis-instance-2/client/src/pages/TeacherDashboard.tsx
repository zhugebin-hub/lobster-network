import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { BookOpen, Users, ClipboardCheck, LogOut, Globe, GraduationCap, Plus, FileText, Settings, FileSearch, FileEdit, NotebookPen, ShoppingCart, LucideIcon, Clock, Upload, FileCheck } from "lucide-react";
import { useEffect, ReactNode } from "react";

// ── 时间阶段提示横幅 ──
function TeacherTimePhaseBar({ phaseData, isZh }: {
  phaseData: {
    phase: string;
    extendedPhase: string;
    currentReviewPriority: number;
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

  const displayPhase = phaseData.extendedPhase || phaseData.phase;

  const configs: Record<string, {
    label: string; labelEn: string;
    sublabel?: string; sublabelEn?: string;
    bg: string; border: string; text: string;
    icon: typeof Clock;
    dateStart?: string | null; dateEnd?: string | null;
  }> = {
    topic_publish: {
      label: "当前处于 — 导师发布题目阶段",
      labelEn: "Current Phase — Topic Publishing",
      sublabel: "请在此期间创建并发布您的课题",
      sublabelEn: "Please create and publish your topics during this period.",
      bg: "bg-teal-50", border: "border-teal-300", text: "text-teal-800", icon: NotebookPen,
      dateStart: phaseData.topicPublishStart, dateEnd: phaseData.topicPublishEnd,
    },
    student_selection: {
      label: "当前处于 — 学生志愿填报阶段",
      labelEn: "Current Phase — Student Wish Submission",
      sublabel: "学生正在填报选题志愿，请确保您的课题已发布",
      sublabelEn: "Students are submitting wishes. Please ensure your topics are published.",
      bg: "bg-blue-50", border: "border-blue-300", text: "text-blue-800", icon: FileCheck,
      dateStart: phaseData.studentSelectionStart, dateEnd: phaseData.studentSelectionEnd,
    },
    teacher_confirm: {
      label: `当前处于 — 导师确认志愿阶段${phaseData.currentReviewPriority > 0 && phaseData.currentReviewPriority <= 6 ? `（第${phaseData.currentReviewPriority}轮审核）` : ""}`,
      labelEn: `Current Phase — Supervisor Confirmation${phaseData.currentReviewPriority > 0 && phaseData.currentReviewPriority <= 6 ? ` (Round ${phaseData.currentReviewPriority})` : ""}`,
      sublabel: "请及时审核学生的选题志愿申请",
      sublabelEn: "Please review student applications promptly.",
      bg: "bg-amber-50", border: "border-amber-300", text: "text-amber-800", icon: ClipboardCheck,
      dateStart: phaseData.teacherConfirmStart, dateEnd: phaseData.teacherConfirmEnd,
    },
    thesis_upload: {
      label: "当前处于 — 论文提交阶段",
      labelEn: "Current Phase — Thesis Submission",
      sublabel: "学生正在提交论文终稿",
      sublabelEn: "Students are submitting their final theses.",
      bg: "bg-green-50", border: "border-green-300", text: "text-green-800", icon: Upload,
      dateStart: phaseData.thesisUploadStart, dateEnd: phaseData.thesisUploadEnd,
    },
    scoring: {
      label: "当前处于 — 论文评分阶段",
      labelEn: "Current Phase — Thesis Scoring",
      sublabel: "请及时完成学生论文评分",
      sublabelEn: "Please complete thesis scoring promptly.",
      bg: "bg-purple-50", border: "border-purple-300", text: "text-purple-800", icon: FileSearch,
      dateStart: phaseData.scoringStart, dateEnd: phaseData.scoringEnd,
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

  const config = configs[displayPhase] || configs.none;
  const PhaseIcon = config.icon;
  const hasDateRange = config.dateStart && config.dateEnd;

  return (
    <div className={`${config.bg} ${config.border} border rounded-xl px-5 py-4 mb-6 flex items-start gap-4`}>
      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${config.bg} ${config.text}`}>
        <PhaseIcon className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className={`font-semibold text-base ${config.text}`}>
          {isZh ? config.label : config.labelEn}
        </p>
        {(config.sublabel || config.sublabelEn) && (
          <p className={`text-sm mt-0.5 ${config.text} opacity-80`}>
            {isZh ? config.sublabel : config.sublabelEn}
          </p>
        )}
        {hasDateRange && (
          <p className={`text-sm mt-1 ${config.text} opacity-70`}>
            {formatDate(config.dateStart)} ~ {formatDate(config.dateEnd)}
          </p>
        )}
      </div>
    </div>
  );
}

// ── Section wrapper (same style as AdminDashboard) ──
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
  icon: Icon,
  iconBg,
  iconColor,
  title,
  description,
  onClick,
  badge,
  actionButton,
}: {
  icon: LucideIcon;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  onClick: () => void;
  badge?: ReactNode;
  actionButton?: ReactNode;
}) {
  return (
    <Card
      className="hover:shadow-lg transition-shadow cursor-pointer relative group"
      onClick={onClick}
    >
      {badge}
      <CardHeader>
        <div
          className={`w-12 h-12 ${iconBg} rounded-lg flex items-center justify-center mb-4 transition-transform group-hover:scale-105`}
        >
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      {actionButton && <CardContent>{actionButton}</CardContent>}
    </Card>
  );
}

export default function TeacherDashboard() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  const { data: topics } = trpc.topic.myTopics.useQuery(undefined, { enabled: isAuthenticated });
  const { data: pendingWishes } = trpc.match.pendingWishes.useQuery(undefined, { enabled: isAuthenticated });
  const { data: students } = trpc.match.myStudents.useQuery(undefined, { enabled: isAuthenticated });
  const { data: firstTeacherTasks } = trpc.secondTeacher.getFirstTeacherReviewTasks.useQuery(undefined, { enabled: isAuthenticated });
  const { data: secondTeacherTasks } = trpc.secondTeacher.getReviewTasks.useQuery(undefined, { enabled: isAuthenticated });
  const { data: pendingTitleChangeCount } = trpc.titleChange.getPendingCount.useQuery(undefined, { enabled: isAuthenticated });
  const { data: pendingPurchaseRequests } = trpc.purchase.getPendingTeacherReview.useQuery(undefined, { enabled: isAuthenticated });
  const { data: isLabAdmin } = trpc.purchase.isLabAdmin.useQuery(undefined, { enabled: isAuthenticated });
  const { data: isAssetLeader } = trpc.purchase.isAssetLeader.useQuery(undefined, { enabled: isAuthenticated });
  const { data: pendingLabRequests } = trpc.purchase.getPendingLabReview.useQuery(undefined, { enabled: isAuthenticated && isLabAdmin });
  const { data: pendingAssetRequests } = trpc.purchase.getPendingAssetReview.useQuery(undefined, { enabled: isAuthenticated && isAssetLeader });
  const { data: phaseData } = trpc.admin.getCurrentPhase.useQuery(undefined, { enabled: isAuthenticated });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "teacher" && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  const isZh = language === "zh";
  const publishedTopics = topics?.filter(t => t.status === "published") || [];
  const draftTopics = topics?.filter(t => t.status === "draft") || [];
  const pendingCount = pendingWishes?.length || 0;
  const firstTasks = firstTeacherTasks?.tasks || [];
  const secondTasks = secondTeacherTasks?.tasks || [];
  const firstPendingCount = firstTasks.filter((t: any) => t.status === 'pending' && t.draftId).length || 0;
  const secondPendingCount = secondTasks.filter((t: any) => t.status === 'pending' && t.canScore).length || 0;
  const totalPendingReviewCount = firstPendingCount + secondPendingCount;
  const negotiationCount = firstTasks.filter((t: any) => t.status === 'scored' && t.needsNegotiation).length + secondTasks.filter((t: any) => t.status === 'scored' && t.needsNegotiation).length;
  const reviewBadgeCount = totalPendingReviewCount + negotiationCount;

  // 采购审核待办
  const teacherPending = pendingPurchaseRequests?.length || 0;
  const labPending = isLabAdmin ? (pendingLabRequests?.length || 0) : 0;
  const assetPending = isAssetLeader ? (pendingAssetRequests?.length || 0) : 0;
  const totalPurchasePending = teacherPending + labPending + assetPending;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.name} ({t.roles.teacher})</span>
            <Button variant="ghost" size="sm" onClick={() => setLanguage(isZh ? "en" : "zh")}>
              <Globe className="w-4 h-4 mr-2" />
              {isZh ? "EN" : "中"}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              {t.logout}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">{isZh ? "导师控制台" : "Supervisor Dashboard"}</h1>

        {/* ══ 时间阶段提示横幅 ══ */}
        {phaseData && <TeacherTimePhaseBar phaseData={phaseData} isZh={isZh} />}

        {/* ── Summary cards ── */}
        <div className="grid md:grid-cols-4 gap-4 mb-10">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{isZh ? "已发布课题" : "Published Topics"}</CardTitle>
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{publishedTopics.length}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{isZh ? "草稿课题" : "Draft Topics"}</CardTitle>
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{draftTopics.length}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{isZh ? "待审核申请" : "Pending Applications"}</CardTitle>
            </CardHeader>
            <CardContent><div className="text-2xl font-bold text-orange-600">{pendingCount}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{isZh ? "已录取学生" : "Accepted Students"}</CardTitle>
            </CardHeader>
            <CardContent><div className="text-2xl font-bold text-green-600">{students?.length || 0}</div></CardContent>
          </Card>
        </div>

        {/* ═══ Section 1 — 选题管理 ═══ */}
        <Section title={isZh ? "选题管理" : "Topic Selection"}>
          <ModuleCard
            icon={BookOpen}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            title={isZh ? "课题管理" : "Topic Management"}
            description={isZh ? "管理您的毕设题库，添加、编辑或发布课题" : "Manage your thesis topics"}
            onClick={() => setLocation("/teacher/topics")}
            actionButton={
              <Button className="w-full"><Plus className="w-4 h-4 mr-2" />{isZh ? "进入管理" : "Manage Topics"}</Button>
            }
          />
          <ModuleCard
            icon={ClipboardCheck}
            iconBg="bg-orange-100"
            iconColor="text-orange-600"
            title={isZh ? "志愿审核" : "Application Review"}
            description={isZh ? "审核学生的选题申请，同意或拒绝" : "Review student applications"}
            onClick={() => setLocation("/teacher/review")}
            badge={pendingCount > 0 ? (
              <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center z-10">
                {pendingCount}
              </div>
            ) : undefined}
            actionButton={
              <Button variant={pendingCount > 0 ? "destructive" : "outline"} className="w-full">
                {pendingCount > 0 ? `${pendingCount} ${isZh ? "个待审核" : " Pending"}` : (isZh ? "暂无申请" : "No Applications")}
              </Button>
            }
          />
          <ModuleCard
            icon={Users}
            iconBg="bg-green-100"
            iconColor="text-green-600"
            title={isZh ? "我的学生" : "My Students"}
            description={isZh ? "查看已录取的学生信息" : "View accepted students"}
            onClick={() => setLocation("/teacher/students")}
            actionButton={
              <Button variant="outline" className="w-full"><FileText className="w-4 h-4 mr-2" />{isZh ? "查看详情" : "View Details"}</Button>
            }
          />
        </Section>

        {/* ═══ Section 2 — 论文与指导 ═══ */}
        <Section title={isZh ? "论文与指导" : "Thesis & Guidance"}>
          <ModuleCard
            icon={FileSearch}
            iconBg="bg-purple-100"
            iconColor="text-purple-600"
            title={isZh ? "论文评审" : "Thesis Review"}
            description={isZh ? "审阅学生论文并评分（第一/第二导师）" : "Review and score student theses"}
            onClick={() => setLocation("/teacher/thesis-review")}
            badge={reviewBadgeCount > 0 ? (
              <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center z-10 animate-pulse">
                {reviewBadgeCount}
              </div>
            ) : undefined}
            actionButton={
              <div className="space-y-2 w-full">
                <Button variant={totalPendingReviewCount > 0 ? "destructive" : "outline"} className="w-full">
                  <FileSearch className="w-4 h-4 mr-2" />
                  {totalPendingReviewCount > 0 ? `${totalPendingReviewCount} ${isZh ? "个待评分" : " Pending"}` : (isZh ? "查看评审" : "View Reviews")}
                </Button>
                {negotiationCount > 0 && (
                  <div className="text-xs text-red-600 font-medium text-center bg-red-50 rounded py-1">
                    ⚠ {negotiationCount} {isZh ? "个需协商修改评分" : " need score negotiation"}
                  </div>
                )}
              </div>
            }
          />
          <ModuleCard
            icon={FileEdit}
            iconBg="bg-orange-100"
            iconColor="text-orange-600"
            title={isZh ? "题目修改审核" : "Title Change Review"}
            description={isZh ? "审核学生的题目修改申请" : "Review student title change requests"}
            onClick={() => setLocation("/teacher/title-change")}
            badge={pendingTitleChangeCount && pendingTitleChangeCount > 0 ? (
              <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center z-10">
                {pendingTitleChangeCount}
              </div>
            ) : undefined}
            actionButton={
              <Button variant={pendingTitleChangeCount && pendingTitleChangeCount > 0 ? "destructive" : "outline"} className="w-full">
                <FileEdit className="w-4 h-4 mr-2" />
                {pendingTitleChangeCount && pendingTitleChangeCount > 0 ? `${pendingTitleChangeCount} ${isZh ? "个待审核" : " Pending"}` : (isZh ? "查看申请" : "View Requests")}
              </Button>
            }
          />
          <ModuleCard
            icon={NotebookPen}
            iconBg="bg-teal-100"
            iconColor="text-teal-600"
            title={isZh ? "指导记录" : "Guidance Logs"}
            description={isZh ? "查看学生的指导记录，添加评论和反馈" : "View student guidance logs and add feedback"}
            onClick={() => setLocation("/teacher/guidance")}
            actionButton={
              <Button variant="outline" className="w-full"><NotebookPen className="w-4 h-4 mr-2" />{isZh ? "查看记录" : "View Logs"}</Button>
            }
          />
        </Section>

        {/* ═══ Section 3 — 其他功能 ═══ */}
        <Section title={isZh ? "其他功能" : "Other Features"}>
          <ModuleCard
            icon={ShoppingCart}
            iconBg="bg-emerald-100"
            iconColor="text-emerald-600"
            title={isZh ? "采购审核" : "Purchase Review"}
            description={
              totalPurchasePending > 0
                ? (isZh ? `${totalPurchasePending} 个待审核申请` : `${totalPurchasePending} pending requests`)
                : (isZh ? "审核学生的毕设耗材采购申请" : "Review student purchase requests")
            }
            onClick={() => setLocation("/teacher/purchase")}
            badge={totalPurchasePending > 0 ? (
              <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center z-10">
                {totalPurchasePending}
              </div>
            ) : undefined}
            actionButton={
              <Button variant={totalPurchasePending > 0 ? "destructive" : "outline"} className="w-full">
                <ShoppingCart className="w-4 h-4 mr-2" />
                {totalPurchasePending > 0
                  ? `${totalPurchasePending} ${isZh ? "个待审核" : " Pending"}`
                  : (isZh ? "查看审核" : "View Reviews")}
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
