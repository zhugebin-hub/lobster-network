import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import {
  Users, Settings, FileText, BarChart3, LogOut, Globe, GraduationCap,
  Calendar, ClipboardCheck, UserPlus, Star, BookOpen, Monitor,
  ShoppingCart, History, Upload, LucideIcon, Clock, FileCheck,
  FileSearch, CheckCircle2, Circle, AlertCircle, Activity, NotebookPen
} from "lucide-react";
import { useEffect, ReactNode, useMemo } from "react";

// ── 时间阶段概览面板 ──────────────────────────────────────────────────
interface PhaseInfo {
  key: string;
  label: string;
  labelEn: string;
  icon: typeof Clock;
  colorDot: string;
  colorBg: string;
  colorBorder: string;
  colorText: string;
  dateStart?: string | null;
  dateEnd?: string | null;
}

function TimePhaseOverview({ phaseData, isZh, onNavigate }: {
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
  onNavigate: (path: string) => void;
}) {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return isZh ? "未设置" : "Not set";
    const d = new Date(dateStr);
    return d.toLocaleDateString(isZh ? "zh-CN" : "en-US", {
      month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit",
    });
  };

  const now = useMemo(() => new Date(), []);
  const displayPhase = phaseData.extendedPhase || phaseData.phase;

  const getStatus = (start?: string | null, end?: string | null): "active" | "upcoming" | "completed" | "not_set" => {
    if (!start || !end) return "not_set";
    const s = new Date(start);
    const e = new Date(end);
    if (now < s) return "upcoming";
    if (now > e) return "completed";
    return "active";
  };

  const phases: PhaseInfo[] = [
    {
      key: "topic_publish",
      label: "导师发布题目",
      labelEn: "Topic Publishing",
      icon: NotebookPen,
      colorDot: "bg-teal-500",
      colorBg: "bg-teal-50",
      colorBorder: "border-teal-200",
      colorText: "text-teal-700",
      dateStart: phaseData.topicPublishStart,
      dateEnd: phaseData.topicPublishEnd,
    },
    {
      key: "student_selection",
      label: "学生志愿填报",
      labelEn: "Student Wish Submission",
      icon: FileCheck,
      colorDot: "bg-blue-500",
      colorBg: "bg-blue-50",
      colorBorder: "border-blue-200",
      colorText: "text-blue-700",
      dateStart: phaseData.studentSelectionStart,
      dateEnd: phaseData.studentSelectionEnd,
    },
    {
      key: "teacher_confirm",
      label: "导师确认志愿",
      labelEn: "Supervisor Confirmation",
      icon: ClipboardCheck,
      colorDot: "bg-amber-500",
      colorBg: "bg-amber-50",
      colorBorder: "border-amber-200",
      colorText: "text-amber-700",
      dateStart: phaseData.teacherConfirmStart,
      dateEnd: phaseData.teacherConfirmEnd,
    },
    {
      key: "thesis_upload",
      label: "论文提交",
      labelEn: "Thesis Submission",
      icon: Upload,
      colorDot: "bg-green-500",
      colorBg: "bg-green-50",
      colorBorder: "border-green-200",
      colorText: "text-green-700",
      dateStart: phaseData.thesisUploadStart,
      dateEnd: phaseData.thesisUploadEnd,
    },
    {
      key: "scoring",
      label: "论文评分",
      labelEn: "Thesis Scoring",
      icon: FileSearch,
      colorDot: "bg-purple-500",
      colorBg: "bg-purple-50",
      colorBorder: "border-purple-200",
      colorText: "text-purple-700",
      dateStart: phaseData.scoringStart,
      dateEnd: phaseData.scoringEnd,
    },
  ];

  const StatusIcon = ({ status }: { status: "active" | "upcoming" | "completed" | "not_set" }) => {
    switch (status) {
      case "active":
        return <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />;
      case "completed":
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case "upcoming":
        return <Circle className="w-4 h-4 text-gray-400" />;
      case "not_set":
        return <AlertCircle className="w-4 h-4 text-gray-300" />;
    }
  };

  const statusLabel = (status: "active" | "upcoming" | "completed" | "not_set") => {
    const map = {
      active: isZh ? "进行中" : "Active",
      upcoming: isZh ? "未开始" : "Upcoming",
      completed: isZh ? "已结束" : "Completed",
      not_set: isZh ? "未配置" : "Not Set",
    };
    return map[status];
  };

  const statusBadgeClass = (status: "active" | "upcoming" | "completed" | "not_set") => {
    const map = {
      active: "bg-green-100 text-green-700",
      upcoming: "bg-gray-100 text-gray-600",
      completed: "bg-green-50 text-green-600",
      not_set: "bg-gray-50 text-gray-400",
    };
    return map[status];
  };

  return (
    <div className="mb-8">
      {/* 标题栏 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-800">
            {isZh ? "系统时间阶段概览" : "System Phase Overview"}
          </h2>
          {phaseData.currentReviewPriority > 0 && phaseData.currentReviewPriority <= 6 && displayPhase === "teacher_confirm" && (
            <span className="ml-2 px-2.5 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
              {isZh ? `第${phaseData.currentReviewPriority}轮审核` : `Round ${phaseData.currentReviewPriority}`}
            </span>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={() => onNavigate("/admin/config")}>
          <Settings className="w-4 h-4 mr-1.5" />
          {isZh ? "配置时间" : "Configure"}
        </Button>
      </div>

      {/* 阶段卡片网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {phases.map((p) => {
          const status = getStatus(p.dateStart, p.dateEnd);
          const isActive = displayPhase === p.key;
          const PhaseIcon = p.icon;

          return (
            <div
              key={p.key}
              className={`relative rounded-xl border-2 p-4 transition-all ${
                isActive
                  ? `${p.colorBorder} ${p.colorBg} shadow-md ring-2 ring-offset-1 ring-${p.colorDot.replace("bg-", "").replace("-500", "-300")}`
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              {/* 活跃指示器 */}
              {isActive && (
                <div className="absolute -top-2.5 left-4">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${p.colorBg} ${p.colorText} border ${p.colorBorder}`}>
                    <div className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                    {isZh ? "当前阶段" : "Current"}
                  </span>
                </div>
              )}

              <div className="flex items-center justify-between mb-3 mt-1">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isActive ? p.colorBg : "bg-gray-100"}`}>
                    <PhaseIcon className={`w-4 h-4 ${isActive ? p.colorText : "text-gray-500"}`} />
                  </div>
                  <span className={`font-semibold text-sm ${isActive ? p.colorText : "text-gray-700"}`}>
                    {isZh ? p.label : p.labelEn}
                  </span>
                </div>
              </div>

              {/* 状态徽章 */}
              <div className="flex items-center gap-1.5 mb-2">
                <StatusIcon status={status} />
                <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${statusBadgeClass(status)}`}>
                  {statusLabel(status)}
                </span>
              </div>

              {/* 时间范围 */}
              <div className="text-xs text-gray-500 space-y-0.5">
                <div className="flex justify-between">
                  <span>{isZh ? "开始" : "Start"}:</span>
                  <span className={status === "not_set" ? "text-gray-300" : "text-gray-600 font-medium"}>
                    {formatDate(p.dateStart)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>{isZh ? "结束" : "End"}:</span>
                  <span className={status === "not_set" ? "text-gray-300" : "text-gray-600 font-medium"}>
                    {formatDate(p.dateEnd)}
                  </span>
                </div>
              </div>

              {/* 进度条（仅当活跃时显示） */}
              {isActive && p.dateStart && p.dateEnd && (() => {
                const s = new Date(p.dateStart!).getTime();
                const e = new Date(p.dateEnd!).getTime();
                const n = now.getTime();
                const pct = Math.min(100, Math.max(0, ((n - s) / (e - s)) * 100));
                return (
                  <div className="mt-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span className={p.colorText}>{Math.round(pct)}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${p.colorDot} transition-all`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })()}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Section wrapper ──────────────────────────────────────────────────────
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

// ── Module card ──────────────────────────────────────────────────
function ModuleCard({
  icon: Icon,
  iconBg,
  iconColor,
  title,
  description,
  onClick,
  badge,
}: {
  icon: LucideIcon;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  onClick: () => void;
  badge?: ReactNode;
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
    </Card>
  );
}

// ── Main component ───────────────────────────────────────────────
export default function AdminDashboard() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  const { data: users } = trpc.admin.getUsers.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });
  const { data: matches } = trpc.admin.getAllMatches.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });
  const { data: currentYear } = trpc.admin.getCurrentYear.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });

  // 采购审核待办数量
  const { data: pendingLabRequests } = trpc.purchase.getPendingLabReview.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });
  const { data: pendingAssetRequests } = trpc.purchase.getPendingAssetReview.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });
  const pendingPurchaseCount = (pendingLabRequests?.length || 0) + (pendingAssetRequests?.length || 0);

  // 时间阶段数据
  const { data: phaseData } = trpc.admin.getCurrentPhase.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });

  // 系统配置（用于获取逾期天数）
  const { data: configs } = trpc.admin.getConfigs.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin",
  });
  const overdueDaysConfig = configs?.find((c: any) => c.configKey === "overdueDays");
  const overdueDaysValue = overdueDaysConfig?.configValue;

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );

  const isZh = language === "zh";
  const teachers = users?.filter((u) => u.role === "teacher") || [];
  const students = users?.filter((u) => u.role === "student") || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ── Header ── */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user?.name} ({t.roles.admin})
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLanguage(isZh ? "en" : "zh")}
            >
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

      {/* ── Content ── */}
      <main className="container mx-auto px-4 py-8">
        {/* Title row */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">
            {isZh ? "管理员控制台" : "Admin Dashboard"}
          </h1>
          <div className="flex items-center gap-3">
            {currentYear && (
              <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium">
                {isZh ? "当前学年" : "Current Year"}:{" "}
                {isZh
                  ? (currentYear.displayName || currentYear.yearName)
                  : (() => {
                      // 英文模式下格式化为 "2026-2027 (2027 graduates)"
                      const yn = currentYear.yearName || "";
                      const m = yn.match(/(\d{4})-(\d{4})/);
                      if (m) return `${m[1]}-${m[2]} (${m[2]} graduates)`;
                      return currentYear.displayName || yn;
                    })()}
              </div>
            )}
            {overdueDaysValue && (
              <div className="bg-amber-50 text-amber-700 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-1">
                {isZh
                  ? `✅ 已启用逾期分配：${overdueDaysValue}天`
                  : `✅ Overdue allocation enabled: ${overdueDaysValue} day(s)`}
              </div>
            )}
          </div>
        </div>

        {/* ══ 全局时间阶段概览面板 ══ */}
        {phaseData && <TimePhaseOverview phaseData={phaseData} isZh={isZh} onNavigate={setLocation} />}

        {/* ── Summary cards ── */}
        <div className="grid md:grid-cols-4 gap-4 mb-10">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {isZh ? "导师数量" : "Teachers"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{teachers.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {isZh ? "学生数量" : "Students"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{students.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {isZh ? "已匹配" : "Matched"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {matches?.length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {isZh ? "待匹配" : "Pending"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {students.length - (matches?.length || 0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ═══════════════════════════════════════════════════════════
            Section 1 — 选题与课题管理
            ═══════════════════════════════════════════════════════════ */}
        <Section title={isZh ? "选题与课题管理" : "Topics & Thesis Management"}>
          <ModuleCard
            icon={BookOpen}
            iconBg="bg-teal-100"
            iconColor="text-teal-600"
            title={isZh ? "题库管理" : "Topic Library"}
            description={
              isZh
                ? "管理已发布课题的题库，支持查重和清理"
                : "Manage topic library with deduplication"
            }
            onClick={() => setLocation("/admin/topic-library")}
          />
          <ModuleCard
            icon={Upload}
            iconBg="bg-amber-100"
            iconColor="text-amber-600"
            title={isZh ? "代理导入课题" : "Proxy Import Topics"}
            description={
              isZh
                ? "代替导师批量创建和发布课题"
                : "Bulk create and publish topics for teachers"
            }
            onClick={() => setLocation("/admin/proxy-import")}
          />
          <ModuleCard
            icon={Monitor}
            iconBg="bg-rose-100"
            iconColor="text-rose-600"
            title={isZh ? "中方导师监控" : "ZJSU Teacher Monitor"}
            description={
              isZh
                ? "监控中方导师课题容量与分流学生匹配情况"
                : "Monitor ZJSU teacher topics and Single-Degree students"
            }
            onClick={() => setLocation("/admin/chinese-teacher-monitoring")}
          />
        </Section>

        {/* ═══════════════════════════════════════════════════════════
            Section 2 — 匹配与分配
            ═══════════════════════════════════════════════════════════ */}
        <Section title={isZh ? "匹配与分配" : "Matching & Assignment"}>
          <ModuleCard
            icon={FileText}
            iconBg="bg-green-100"
            iconColor="text-green-600"
            title={isZh ? "匹配结果" : "Matches"}
            description={isZh ? "查看和导出匹配结果" : "View results"}
            onClick={() => setLocation("/admin/matches")}
          />
          <ModuleCard
            icon={UserPlus}
            iconBg="bg-cyan-100"
            iconColor="text-cyan-600"
            title={isZh ? "第二导师管理" : "Second Teacher"}
            description={
              isZh ? "为学生指派第二导师" : "Assign second teachers"
            }
            onClick={() => setLocation("/admin/second-teacher")}
          />
          <ModuleCard
            icon={ClipboardCheck}
            iconBg="bg-red-100"
            iconColor="text-red-600"
            title={isZh ? "审核监控" : "Review Monitor"}
            description={
              isZh ? "监控导师审核进度" : "Monitor review progress"
            }
            onClick={() => setLocation("/admin/review-status")}
          />
        </Section>

        {/* ═══════════════════════════════════════════════════════════
            Section 3 — 数据与评估
            ═══════════════════════════════════════════════════════════ */}
        <Section title={isZh ? "数据与评估" : "Data & Evaluation"}>
          <ModuleCard
            icon={BarChart3}
            iconBg="bg-orange-100"
            iconColor="text-orange-600"
            title={isZh ? "数据统计" : "Statistics"}
            description={isZh ? "查看选题统计数据" : "View statistics"}
            onClick={() => setLocation("/admin/stats")}
          />
          <ModuleCard
            icon={Star}
            iconBg="bg-yellow-100"
            iconColor="text-yellow-600"
            title={isZh ? "评分统计" : "Score Statistics"}
            description={
              isZh
                ? "查看双导师评分情况和分数差异"
                : "View dual-supervisor scores"
            }
            onClick={() => setLocation("/admin/score-statistics")}
          />
        </Section>

        {/* ═══════════════════════════════════════════════════════════
            Section 4 — 系统管理
            ═══════════════════════════════════════════════════════════ */}
        <Section title={isZh ? "系统管理" : "System Administration"}>
          <ModuleCard
            icon={Calendar}
            iconBg="bg-indigo-100"
            iconColor="text-indigo-600"
            title={isZh ? "年度管理" : "Year Management"}
            description={isZh ? "管理学年和流程配置" : "Manage academic years"}
            onClick={() => setLocation("/admin/years")}
          />
          <ModuleCard
            icon={Users}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            title={isZh ? "用户管理" : "Users"}
            description={isZh ? "管理导师和学生账号" : "Manage accounts"}
            onClick={() => setLocation("/admin/users")}
          />
          <ModuleCard
            icon={Settings}
            iconBg="bg-purple-100"
            iconColor="text-purple-600"
            title={isZh ? "系统配置" : "Settings"}
            description={isZh ? "配置时间节点和参数" : "Configure system"}
            onClick={() => setLocation("/admin/config")}
          />
          <ModuleCard
            icon={ShoppingCart}
            iconBg="bg-emerald-100"
            iconColor="text-emerald-600"
            title={isZh ? "采购审核管理" : "Purchase Management"}
            description={
              pendingPurchaseCount > 0
                ? isZh
                  ? `${pendingPurchaseCount} 个待审核申请`
                  : `${pendingPurchaseCount} pending requests`
                : isZh
                  ? "管理毕设采购申请审核流程和角色任命"
                  : "Manage purchase requests and role assignments"
            }
            onClick={() => setLocation("/admin/purchase")}
            badge={
              pendingPurchaseCount > 0 ? (
                <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center z-10">
                  {pendingPurchaseCount}
                </div>
              ) : undefined
            }
          />
          <ModuleCard
            icon={Activity}
            iconBg="bg-indigo-100"
            iconColor="text-indigo-600"
            title={isZh ? "用户活动日志" : "User Activity Logs"}
            description={
              isZh
                ? "追踪所有用户的关键操作记录"
                : "Track key operations of all users"
            }
            onClick={() => setLocation("/admin/activity-logs")}
          />
        </Section>
      </main>
    </div>
  );
}
