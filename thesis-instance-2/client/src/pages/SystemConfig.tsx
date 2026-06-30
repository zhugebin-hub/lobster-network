import { useState, useEffect } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, Save, Info, Clock, AlertTriangle, Zap, Settings, Loader2, Users, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function SystemConfig() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  // 时间配置状态
  const [timeConfig, setTimeConfig] = useState({
    topicPublishStart: "",
    topicPublishEnd: "",
    studentSelectionStart: "",
    studentSelectionEnd: "",
    teacherConfirmStart: "",
    teacherConfirmEnd: "",
    thesisUploadStart: "",
    thesisUploadEnd: "",
    scoringStart: "",
    scoringEnd: "",
  });

  // 逾期时限配置（天数）
  const [overdueDays, setOverdueDays] = useState("1");

  // 名额配置状态
  const [quotaValue, setQuotaValue] = useState("");

  const utils = trpc.useUtils();
  const { data: existingTimeConfig } = trpc.admin.getTimeConfig.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: configs } = trpc.admin.getConfigs.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: currentReviewPriority } = trpc.admin.getCurrentReviewPriority.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: quotaStats, isLoading: quotaLoading } = trpc.admin.getChineseTeacherQuotaStats.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });

  const saveTimeMutation = trpc.admin.saveTimeConfig.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "时间配置已保存" : "Time config saved"); utils.admin.getTimeConfig.invalidate(); },
    onError: (e: any) => toast.error(e.message),
  });

  const setConfigMutation = trpc.admin.setConfig.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "配置已保存" : "Config saved"); utils.admin.getConfigs.invalidate(); },
    onError: (e: any) => toast.error(e.message),
  });

  const triggerQuotaFullMutation = trpc.admin.triggerQuotaFullHandling.useMutation({
    onSuccess: (data) => {
      toast.success(language === "zh" ? data.message : "Quota full handling completed");
      utils.admin.getChineseTeacherQuotaStats.invalidate();
      utils.admin.getConfigs.invalidate();
    },
    onError: (e: any) => toast.error(e.message),
  });

  const autoAssignMutation = trpc.admin.autoAssignOverdueWishes.useMutation({
    onSuccess: (data) => { 
      toast.success(language === "zh" 
        ? `逾期自动分配完成：处理${data.processed}个志愿，成功分配${data.assigned}个` 
        : `Auto-assign complete: processed ${data.processed}, assigned ${data.assigned}`); 
      utils.admin.getCurrentReviewPriority.invalidate();
    },
    onError: (e: any) => toast.error(e.message),
  });

  useEffect(() => {
    if (existingTimeConfig) {
      setTimeConfig({
        topicPublishStart: existingTimeConfig.topicPublishStart ? existingTimeConfig.topicPublishStart.slice(0, 16) : "",
        topicPublishEnd: existingTimeConfig.topicPublishEnd ? existingTimeConfig.topicPublishEnd.slice(0, 16) : "",
        studentSelectionStart: existingTimeConfig.studentSelectionStart ? existingTimeConfig.studentSelectionStart.slice(0, 16) : "",
        studentSelectionEnd: existingTimeConfig.studentSelectionEnd ? existingTimeConfig.studentSelectionEnd.slice(0, 16) : "",
        teacherConfirmStart: existingTimeConfig.teacherConfirmStart ? existingTimeConfig.teacherConfirmStart.slice(0, 16) : "",
        teacherConfirmEnd: existingTimeConfig.teacherConfirmEnd ? existingTimeConfig.teacherConfirmEnd.slice(0, 16) : "",
        thesisUploadStart: existingTimeConfig.thesisUploadStart ? existingTimeConfig.thesisUploadStart.slice(0, 16) : "",
        thesisUploadEnd: existingTimeConfig.thesisUploadEnd ? existingTimeConfig.thesisUploadEnd.slice(0, 16) : "",
        scoringStart: existingTimeConfig.scoringStart ? existingTimeConfig.scoringStart.slice(0, 16) : "",
        scoringEnd: existingTimeConfig.scoringEnd ? existingTimeConfig.scoringEnd.slice(0, 16) : "",
      });
    }
  }, [existingTimeConfig]);

  useEffect(() => {
    if (configs) {
      const overdueConfig = configs.find(c => c.configKey === "overdueDays");
      if (overdueConfig) {
        setOverdueDays(overdueConfig.configValue);
      }
      const quotaConfig = configs.find(c => c.configKey === "chineseTeacherTotalQuota");
      if (quotaConfig) {
        setQuotaValue(quotaConfig.configValue);
      }
    }
  }, [configs]);

  const handleLogout = async () => { await logout(); setLocation("/"); };
  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  const getPhaseLabel = (phase: string) => {
    const labels: Record<string, { zh: string; en: string; color: string }> = {
      none: { zh: "未配置", en: "Not Configured", color: "bg-gray-500" },
      topic_publish: { zh: "导师发布题目阶段", en: "Topic Publishing Phase", color: "bg-teal-500" },
      student_selection: { zh: "学生选题阶段", en: "Student Selection Phase", color: "bg-green-500" },
      teacher_confirm: { zh: "导师确认阶段", en: "Teacher Confirmation Phase", color: "bg-blue-500" },
      closed: { zh: "已结束", en: "Ended", color: "bg-gray-500" },
    };
    return labels[phase] || labels.none;
  };

  const getPriorityLabel = (priority: number) => {
    if (priority === -1) return language === "zh" ? "所有轮次已完成" : "All rounds complete";
    const labels = language === "zh" 
      ? ["第一志愿", "第二志愿", "第三志愿", "第四志愿", "第五志愿", "第六志愿"]
      : ["1st Choice", "2nd Choice", "3rd Choice", "4th Choice", "5th Choice", "6th Choice"];
    return labels[priority - 1] || `#${priority}`;
  };

  const currentPhase = existingTimeConfig?.phase || "none";
  const phaseInfo = getPhaseLabel(currentPhase);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center"><GraduationCap className="w-6 h-6 text-white" /></div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}><Globe className="w-4 h-4 mr-2" />{language === "zh" ? "EN" : "中"}</Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}><LogOut className="w-4 h-4 mr-2" />{t.logout}</Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => setLocation("/admin")}><ArrowLeft className="w-4 h-4 mr-2" />{t.back}</Button>
          <h1 className="text-2xl font-bold">{language === "zh" ? "系统配置" : "System Configuration"}</h1>
          <Badge className={`${phaseInfo.color} text-white`}>
            {language === "zh" ? phaseInfo.zh : phaseInfo.en}
          </Badge>
        </div>

        <Tabs defaultValue="time" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="time"><Clock className="w-4 h-4 mr-2" />{language === "zh" ? "时间配置" : "Time Config"}</TabsTrigger>
            <TabsTrigger value="quota"><Users className="w-4 h-4 mr-2" />{language === "zh" ? "名额配置" : "Quota Config"}</TabsTrigger>
            <TabsTrigger value="overdue"><Settings className="w-4 h-4 mr-2" />{language === "zh" ? "逾期配置" : "Overdue Config"}</TabsTrigger>
            <TabsTrigger value="mechanism"><Info className="w-4 h-4 mr-2" />{language === "zh" ? "机制说明" : "Mechanism"}</TabsTrigger>
          </TabsList>

          {/* 时间配置 */}
          <TabsContent value="time">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="border-teal-200">
                <CardHeader className="bg-teal-50">
                  <CardTitle className="flex items-center gap-2 text-teal-800">
                    <Clock className="w-5 h-5" />
                    {language === "zh" ? "导师发布题目时间段" : "Topic Publishing Period"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "在此期间导师可以创建和发布课题，该时间段不可与学生选题时间段重叠"
                      : "During this period, supervisors can create and publish topics. Must not overlap with student selection period."}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div>
                    <Label>{language === "zh" ? "开始时间" : "Start Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.topicPublishStart} 
                      onChange={(e) => setTimeConfig({...timeConfig, topicPublishStart: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label>{language === "zh" ? "截止时间" : "End Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.topicPublishEnd} 
                      onChange={(e) => setTimeConfig({...timeConfig, topicPublishEnd: e.target.value})} 
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-green-200">
                <CardHeader className="bg-green-50">
                  <CardTitle className="flex items-center gap-2 text-green-800">
                    <Clock className="w-5 h-5" />
                    {language === "zh" ? "学生选题时间段" : "Student Selection Period"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "分流与非分流学生共同选题，导师不可以确认学生"
                      : "All students (Single-Degree and Dual-Degree) select topics together, teachers cannot confirm"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div>
                    <Label>{language === "zh" ? "开始时间" : "Start Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.studentSelectionStart} 
                      onChange={(e) => setTimeConfig({...timeConfig, studentSelectionStart: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label>{language === "zh" ? "截止时间" : "End Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.studentSelectionEnd} 
                      onChange={(e) => setTimeConfig({...timeConfig, studentSelectionEnd: e.target.value})} 
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-blue-200">
                <CardHeader className="bg-blue-50">
                  <CardTitle className="flex items-center gap-2 text-blue-800">
                    <Clock className="w-5 h-5" />
                    {language === "zh" ? "导师确认时间段" : "Teacher Confirmation Period"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "在此期间学生不可以选择课题，导师可以确认学生"
                      : "During this period, students cannot select topics, teachers can confirm"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div>
                    <Label>{language === "zh" ? "开始时间" : "Start Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.teacherConfirmStart} 
                      onChange={(e) => setTimeConfig({...timeConfig, teacherConfirmStart: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label>{language === "zh" ? "截止时间" : "End Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.teacherConfirmEnd} 
                      onChange={(e) => setTimeConfig({...timeConfig, teacherConfirmEnd: e.target.value})} 
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-purple-200">
                <CardHeader className="bg-purple-50">
                  <CardTitle className="flex items-center gap-2 text-purple-800">
                    <Clock className="w-5 h-5" />
                    {language === "zh" ? "学生上传论文时间段" : "Thesis Upload Period"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "在此期间分流学生可以上传和更新论文终稿"
                      : "During this period, Single-Degree students can upload and update thesis"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div>
                    <Label>{language === "zh" ? "开始时间" : "Start Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.thesisUploadStart} 
                      onChange={(e) => setTimeConfig({...timeConfig, thesisUploadStart: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label>{language === "zh" ? "截止时间" : "End Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.thesisUploadEnd} 
                      onChange={(e) => setTimeConfig({...timeConfig, thesisUploadEnd: e.target.value})} 
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-orange-200">
                <CardHeader className="bg-orange-50">
                  <CardTitle className="flex items-center gap-2 text-orange-800">
                    <Clock className="w-5 h-5" />
                    {language === "zh" ? "导师评分时间段" : "Teacher Scoring Period"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "在此期间导师可以对学生的论文终稿进行打分"
                      : "During this period, teachers can score student thesis"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div>
                    <Label>{language === "zh" ? "开始时间" : "Start Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.scoringStart} 
                      onChange={(e) => setTimeConfig({...timeConfig, scoringStart: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label>{language === "zh" ? "截止时间" : "End Time"}</Label>
                    <Input 
                      type="datetime-local" 
                      value={timeConfig.scoringEnd} 
                      onChange={(e) => setTimeConfig({...timeConfig, scoringEnd: e.target.value})} 
                    />
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="mt-4 border-yellow-200 bg-yellow-50">
              <CardContent className="pt-4">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                  <div className="text-sm text-yellow-800">
                    <p className="font-medium">{language === "zh" ? "注意事项：" : "Important Notes:"}</p>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      <li>{language === "zh" ? "导师发布题目时间段必须在学生选题时间段之前，且不可重叠" : "Topic publishing period must be before student selection and cannot overlap"}</li>
                      <li>{language === "zh" ? "学生选题时间段和导师确认时间段不可重叠" : "Student selection and teacher confirmation periods cannot overlap"}</li>
                      <li>{language === "zh" ? "建议学生选题时间段在前，导师确认时间段在后" : "Recommended: student selection before teacher confirmation"}</li>
                      <li>{language === "zh" ? "学生上传论文时间段必须在导师确认时间段之后" : "Thesis upload period must be after teacher confirmation period"}</li>
                      <li>{language === "zh" ? "导师评分时间段必须在学生上传论文时间段之后" : "Teacher scoring period must be after thesis upload period"}</li>
                      <li>{language === "zh" ? "时间段外，相应操作将被禁止" : "Operations will be disabled outside configured periods"}</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-4 mt-6">
              <Button onClick={() => saveTimeMutation.mutate(timeConfig)} disabled={saveTimeMutation.isPending}>
                {saveTimeMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                <Save className="w-4 h-4 mr-2" />
                {language === "zh" ? "保存时间配置" : "Save Time Config"}
              </Button>
            </div>
          </TabsContent>


          {/* 名额配置 */}
          <TabsContent value="quota">
            <div className="space-y-6">
              {/* 名额设置卡片 */}
              <Card className="border-purple-200">
                <CardHeader className="bg-purple-50">
                  <CardTitle className="flex items-center gap-2 text-purple-800">
                    <Users className="w-5 h-5" />
                    {language === "zh" ? "中方导师确认名额限制" : "Chinese Teacher Confirmation Quota"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "设置所有中方导师合计可以确认匹配学生的总数量。设为 0 或留空表示不启用名额限制。"
                      : "Set the total number of students all Chinese teachers can confirm combined. Set to 0 or leave empty to disable."}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div className="flex items-end gap-4">
                    <div className="flex-1">
                      <Label>{language === "zh" ? "确认名额总数" : "Total Quota"}</Label>
                      <Input
                        type="number"
                        min="0"
                        value={quotaValue}
                        onChange={(e) => setQuotaValue(e.target.value)}
                        placeholder={language === "zh" ? "例如：15" : "e.g., 15"}
                        className="mt-1"
                      />
                    </div>
                    <Button 
                      onClick={() => setConfigMutation.mutate({ 
                        key: "chineseTeacherTotalQuota", 
                        value: quotaValue || "0",
                        description: "中方导师可确认学生总名额"
                      })}
                      disabled={setConfigMutation.isPending}
                    >
                      <Save className="w-4 h-4 mr-2" />
                      {setConfigMutation.isPending 
                        ? (language === "zh" ? "保存中..." : "Saving...") 
                        : (language === "zh" ? "保存" : "Save")}
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500">
                    {language === "zh" 
                      ? "提示：修改名额后立即生效。如果新名额小于等于当前已确认数，系统将自动触发满额处理。"
                      : "Note: Changes take effect immediately. If new quota ≤ current confirmed count, quota-full handling will trigger automatically."}
                  </p>
                </CardContent>
              </Card>

              {/* 名额统计卡片 */}
              <Card className="border-blue-200">
                <CardHeader className="bg-blue-50">
                  <CardTitle className="flex items-center gap-2 text-blue-800">
                    <ShieldCheck className="w-5 h-5" />
                    {language === "zh" ? "名额使用统计" : "Quota Usage Statistics"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-4">
                  {quotaLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                    </div>
                  ) : quotaStats ? (
                    <div className="space-y-4">
                      {/* 进度条 */}
                      {quotaStats.quotaEnabled && (
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>{language === "zh" ? "已确认 / 总名额" : "Confirmed / Total"}</span>
                            <span className="font-bold">{quotaStats.confirmedCount} / {quotaStats.totalQuota}</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-4">
                            <div 
                              className={`h-4 rounded-full transition-all ${quotaStats.isQuotaFull ? 'bg-red-500' : quotaStats.shouldEnableTransferPriority ? 'bg-amber-500' : 'bg-green-500'}`}
                              style={{ width: `${Math.min(100, (quotaStats.confirmedCount / quotaStats.totalQuota) * 100)}%` }}
                            />
                          </div>
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>{language === "zh" ? `剩余名额：${quotaStats.remainingQuota}` : `Remaining: ${quotaStats.remainingQuota}`}</span>
                            <span>{language === "zh" ? `使用率：${Math.round((quotaStats.confirmedCount / quotaStats.totalQuota) * 100)}%` : `Usage: ${Math.round((quotaStats.confirmedCount / quotaStats.totalQuota) * 100)}%`}</span>
                          </div>
                        </div>
                      )}

                      {/* 统计数据网格 */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div className="bg-gray-50 rounded-lg p-3 text-center">
                          <div className="text-2xl font-bold text-blue-600">{quotaStats.confirmedCount}</div>
                          <div className="text-xs text-gray-500">{language === "zh" ? "已确认匹配" : "Confirmed"}</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-3 text-center">
                          <div className="text-2xl font-bold text-purple-600">{quotaStats.totalQuota || "-"}</div>
                          <div className="text-xs text-gray-500">{language === "zh" ? "总名额" : "Total Quota"}</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-3 text-center">
                          <div className="text-2xl font-bold text-green-600">{quotaStats.confirmedTransferStudents}</div>
                          <div className="text-xs text-gray-500">{language === "zh" ? "已确认分流学生" : "Confirmed Transfer"}</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-3 text-center">
                          <div className="text-2xl font-bold text-amber-600">{quotaStats.pendingTransferStudents}</div>
                          <div className="text-xs text-gray-500">{language === "zh" ? "待确认分流学生" : "Pending Transfer"}</div>
                        </div>
                      </div>

                      {/* 状态提示 */}
                      {!quotaStats.quotaEnabled && (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-600">
                          <Info className="w-4 h-4 inline mr-2" />
                          {language === "zh" ? "名额限制功能未启用。请在上方设置确认名额总数以启用。" : "Quota limit is not enabled. Set a total quota above to enable."}
                        </div>
                      )}
                      {quotaStats.quotaEnabled && quotaStats.isQuotaFull && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
                          <AlertTriangle className="w-4 h-4 inline mr-2" />
                          {language === "zh" ? "名额已满！中方导师将无法再确认新的学生志愿。未匹配的课题已退回草稿状态。" : "Quota is full! Chinese teachers can no longer confirm new student applications."}
                        </div>
                      )}
                      {quotaStats.quotaEnabled && !quotaStats.isQuotaFull && quotaStats.shouldEnableTransferPriority && (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-700">
                          <AlertTriangle className="w-4 h-4 inline mr-2" />
                          {language === "zh" 
                            ? `分流学生优先模式已自动启动！剩余名额（${quotaStats.remainingQuota}）不超过待确认分流学生数（${quotaStats.pendingTransferStudents}），中方导师仅可确认分流学生的志愿。`
                            : `Transfer student priority mode is active! Remaining quota (${quotaStats.remainingQuota}) ≤ pending transfer students (${quotaStats.pendingTransferStudents}).`}
                        </div>
                      )}

                      {/* 手动触发满额处理按钮 */}
                      {quotaStats.quotaEnabled && quotaStats.isQuotaFull && (
                        <div className="pt-2">
                          <Button 
                            variant="destructive" 
                            onClick={() => {
                              if (confirm(language === "zh" 
                                ? "确定要手动触发满额处理吗？这将拒绝所有中方导师的待审核志愿，并将未匹配课题退回草稿状态。" 
                                : "Are you sure? This will reject all pending wishes and retract unmatched topics.")) {
                                triggerQuotaFullMutation.mutate();
                              }
                            }}
                            disabled={triggerQuotaFullMutation.isPending}
                          >
                            {triggerQuotaFullMutation.isPending 
                              ? (language === "zh" ? "处理中..." : "Processing...") 
                              : (language === "zh" ? "手动触发满额处理" : "Trigger Quota Full Handling")}
                          </Button>
                          <p className="text-xs text-gray-500 mt-2">
                            {language === "zh" 
                              ? "如果自动处理未完全执行（例如服务重启），可手动触发。此操作将拒绝所有中方导师待审核志愿并退回未匹配课题。"
                              : "Use this if automatic handling was incomplete. This will reject all pending wishes and retract unmatched topics."}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : null}
                </CardContent>
              </Card>

              {/* 机制说明卡片 */}
              <Card className="border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-800">
                    <Info className="w-5 h-5" />
                    {language === "zh" ? "名额限制机制说明" : "Quota Mechanism Description"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-gray-600 space-y-3">
                  <div>
                    <p className="font-medium text-gray-800 mb-1">{language === "zh" ? "1. 名额控制" : "1. Quota Control"}</p>
                    <p>{language === "zh" 
                      ? "管理员设定中方导师合计可确认的学生总数。当已确认数达到上限时，系统自动禁止中方导师继续确认。"
                      : "Admin sets the total number of students all Chinese teachers can confirm. When the limit is reached, confirmations are blocked."}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-800 mb-1">{language === "zh" ? "2. 分流学生优先模式" : "2. Transfer Student Priority"}</p>
                    <p>{language === "zh" 
                      ? "当剩余名额 ≤ 待确认分流学生数时，自动启动分流优先模式。此时中方导师只能确认分流学生的志愿，确保分流学生的名额不被占用。"
                      : "When remaining quota ≤ pending transfer students, priority mode activates. Chinese teachers can only confirm transfer students."}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-800 mb-1">{language === "zh" ? "3. 满额自动处理" : "3. Auto Handling on Full"}</p>
                    <p>{language === "zh" 
                      ? "名额满后，系统自动执行：(1) 拒绝所有中方导师名下的待审核志愿（学生自动转入下一志愿）；(2) 将中方导师未匹配的课题退回草稿状态；(3) 清理题库中对应的课题记录，确保下一轮选题时学生无法看到这些课题。"
                      : "When full: (1) Reject all pending wishes under Chinese teachers; (2) Retract unmatched topics to draft; (3) Remove from topic library."}</p>
                  </div>
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mt-2">
                    <p className="font-medium text-amber-800 mb-1">{language === "zh" ? "举例说明" : "Example"}</p>
                    <p className="text-amber-700">{language === "zh" 
                      ? "假设总名额15人，分流学生5人。当已确认10个非分流学生后，剩余名额=5=待确认分流学生数，系统自动启动分流优先模式。此后中方导师只能确认分流学生的志愿，直到5个分流学生全部确认完毕，总名额15人满额。"
                      : "Example: Total quota 15, transfer students 5. After 10 non-transfer confirmed, remaining=5=pending transfer, priority mode activates. Only transfer students can be confirmed until all 5 are matched."}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 逾期配置 */}
          <TabsContent value="overdue">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    {language === "zh" ? "逾期时限设置" : "Overdue Threshold Setting"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "导师超过规定时限未审核确定学生，系统将优先分配给申请该课题的分流学生，若无分流学生则随机分配给其他申请学生"
                      : "If teacher doesn't review within threshold, system prioritizes Single-Degree applicants, then randomly assigns to other applicants"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>{language === "zh" ? "逾期时限" : "Overdue Threshold"}</Label>
                    <Select value={overdueDays} onValueChange={setOverdueDays}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0.0007">1 {language === "zh" ? "分钟（测试）" : "minute (test)"}</SelectItem>
                        <SelectItem value="1">1 {language === "zh" ? "天" : "day"}</SelectItem>
                        <SelectItem value="2">2 {language === "zh" ? "天" : "days"}</SelectItem>
                        <SelectItem value="3">3 {language === "zh" ? "天" : "days"}</SelectItem>
                        <SelectItem value="5">5 {language === "zh" ? "天" : "days"}</SelectItem>
                        <SelectItem value="7">7 {language === "zh" ? "天" : "days"}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button 
                    onClick={() => setConfigMutation.mutate({ key: "overdueDays", value: overdueDays, description: "导师审核逾期时限（天）" })}
                    disabled={setConfigMutation.isPending}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {language === "zh" ? "保存逾期配置" : "Save Overdue Config"}
                  </Button>
                  {overdueDays && overdueDays !== "0" && (
                    <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                      <p className="text-sm font-medium text-amber-800">
                        {language === "zh"
                          ? `✅ 已启用逾期分配：${overdueDays}天`
                          : `✅ Overdue allocation enabled: ${overdueDays} day(s)`}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-green-200">
                <CardHeader className="bg-green-50">
                  <CardTitle className="flex items-center gap-2 text-green-800">
                    <Zap className="w-5 h-5" />
                    {language === "zh" ? "自动触发逾期分配" : "Automatic Overdue Assignment"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" 
                      ? "服务器按照已设置的逾期时限自动检查，在导师确认时间段内自动分配逾期志愿"
                      : "Server automatically checks based on threshold and assigns overdue wishes during confirmation period"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {currentReviewPriority && (
                    <div className="p-3 bg-white rounded-lg border">
                      <p className="text-sm text-gray-600 mb-1">{language === "zh" ? "当前审核轮次：" : "Current Review Round:"}</p>
                      <p className="font-semibold text-lg">
                        {getPriorityLabel(currentReviewPriority.priority)}
                      </p>
                    </div>
                  )}
                  <div className="p-4 bg-green-100 rounded-lg border border-green-300">
                    <div className="flex items-center gap-2 text-green-800 font-medium mb-2">
                      <Zap className="w-4 h-4" />
                      {language === "zh" ? "自动分配已启用" : "Auto-Assignment Enabled"}
                    </div>
                    <p className="text-sm text-green-700">
                      {language === "zh" 
                        ? "系统每分钟自动检查逾期志愿，优先分配给分流学生，若无分流学生则随机分配给其他申请学生"
                        : "System checks every minute, prioritizes Single-Degree applicants, then randomly assigns to other applicants"}
                    </p>
                  </div>
                  <Button 
                    variant="outline"
                    className="border-green-300 text-green-700 hover:bg-green-50"
                    onClick={() => autoAssignMutation.mutate({ overdueDays: parseFloat(overdueDays) })}
                    disabled={autoAssignMutation.isPending || currentReviewPriority?.priority === -1}
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    {autoAssignMutation.isPending 
                      ? (language === "zh" ? "处理中..." : "Processing...")
                      : (language === "zh" ? "立即执行一次" : "Execute Now")}
                  </Button>
                  <p className="text-xs text-gray-500">
                    {language === "zh" 
                      ? "提示：点击此按钮可立即执行一次逾期分配，不影响自动分配机制"
                      : "Tip: Click to execute once immediately, does not affect automatic assignment"}
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card className="mt-6 border-blue-200 bg-blue-50">
              <CardContent className="pt-4">
                <div className="flex items-start gap-2">
                  <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium">{language === "zh" ? "志愿轮次匹配说明：" : "Wish Round Matching:"}</p>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      <li>{language === "zh" ? "系统先核对所有学生的第一志愿" : "System first reviews all students' first choices"}</li>
                      <li>{language === "zh" ? "第一志愿匹配完成后，才开始匹配未被分配学生的第二志愿" : "After first round, system processes second choices for unmatched students"}</li>
                      <li>{language === "zh" ? "导师超过逾期时限未审核，系统优先分配给申请该课题的分流学生，若无分流学生则随机分配" : "If teacher exceeds threshold, system prioritizes Single-Degree applicants, then randomly assigns"}</li>
                      <li>{language === "zh" ? "所有学生都有3个志愿" : "All students have 3 wishes"}</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 匹配机制说明 */}
          <TabsContent value="mechanism">
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-800">
                  <Info className="w-5 h-5" />
                  {language === "zh" ? "匹配机制说明" : "Matching Mechanism"}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-blue-700">
                <p className="mb-4">
                  {language === "zh" 
                    ? "本系统采用「志愿优先，教师确认制」匹配机制："
                    : "This system uses 'Preference-First, Teacher-Confirmation' matching mechanism:"}
                </p>
                <ol className="list-decimal list-inside space-y-2">
                  <li>{language === "zh" ? "学生提交选题志愿（所有学生3个志愿）" : "Students submit topic preferences (3 wishes for all students)"}</li>
                  <li>{language === "zh" ? "分流学生只能选择中方导师发布的题目" : "Single-Degree students can only select topics from ZJSU supervisors"}</li>
                  <li>{language === "zh" ? "所有学生必须填报3个志愿并填写选题声明才能提交" : "All students must submit 3 wishes with statements to submit"}</li>
                  <li>{language === "zh" ? "系统先核对所有学生的第一志愿，第一志愿全部匹配后才开始第二志愿" : "System processes first choices first, then second choices after completion"}</li>
                  <li>{language === "zh" ? "导师超过逾期时限未审核，系统优先分配给申请该课题的分流学生，若无分流学生则随机分配" : "If teacher exceeds threshold, system prioritizes Single-Degree applicants, then randomly assigns"}</li>
                </ol>

                <div className="mt-6 p-4 bg-white rounded-lg">
                  <h4 className="font-semibold mb-2">{language === "zh" ? "时间阶段说明" : "Time Phase Description"}</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <Badge className="bg-green-500">学生选题</Badge>
                      <span>{language === "zh" ? "学生可以浏览课题并提交志愿，导师无法确认学生" : "Students can browse topics and submit wishes, teachers cannot confirm"}</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge className="bg-blue-500">导师确认</Badge>
                      <span>{language === "zh" ? "导师可以审核并确认/拒绝学生申请，学生无法修改志愿" : "Teachers can review and approve/reject applications, students cannot modify wishes"}</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge className="bg-gray-500">已结束</Badge>
                      <span>{language === "zh" ? "导师确认时间结束后，选题流程关闭" : "Selection process closed after teacher confirmation period ends"}</span>
                    </li>
                  </ul>
                </div>

                <div className="mt-6 p-4 bg-white rounded-lg">
                  <h4 className="font-semibold mb-2">{language === "zh" ? "志愿填报规则" : "Wish Submission Rules"}</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <Badge variant="outline">所有学生</Badge>
                      <span>{language === "zh" ? "可填报3个志愿（第一、第二、第三志愿），必须填报3个" : "Can submit 3 wishes (1st, 2nd, 3rd choice), must submit all 3"}</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Badge variant="outline">分流学生</Badge>
                      <span>{language === "zh" ? "仅能选择中方导师发布的题目" : "Can only select topics from ZJSU supervisors"}</span>
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
