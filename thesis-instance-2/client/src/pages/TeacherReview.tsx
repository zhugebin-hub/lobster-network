import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, Check, X, User, FileText, Info, AlertTriangle } from "lucide-react";

export default function TeacherReview() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [selectedWish, setSelectedWish] = useState<any>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState<"approved" | "rejected">("approved");

  const utils = trpc.useUtils();
  const { data: pendingWishes, isLoading: wishesLoading } = trpc.match.pendingWishes.useQuery(undefined, { enabled: isAuthenticated });
  
  // 检查是否处于分流学生优先模式（但不向导师显示学生身份）
  const { data: priorityModeData } = trpc.match.checkTransferPriorityMode.useQuery(undefined, { enabled: isAuthenticated });
  // 查询名额状态
  const { data: quotaStatus } = trpc.match.getQuotaStatus.useQuery(undefined, { enabled: isAuthenticated });
  const isTransferPriorityMode = priorityModeData?.isActive || false;
  const isQuotaFull = priorityModeData?.quotaFull || false;
  
  // 判断当前用户是否为中方导师
  const isChineseTeacher = (user as any)?.teacherType === "chinese";

  const reviewMutation = trpc.match.reviewWish.useMutation({
    onSuccess: (data) => {
      toast.success(data.message);
      utils.match.pendingWishes.invalidate();
      utils.match.myStudents.invalidate();
      utils.match.checkTransferPriorityMode.invalidate();
      utils.match.getQuotaStatus.invalidate();
      setShowConfirmDialog(false);
      setSelectedWish(null);
    },
    onError: (e) => toast.error(e.message),
  });

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  const handleReview = (wish: any, action: "approved" | "rejected") => {
    setSelectedWish(wish);
    setConfirmAction(action);
    setShowConfirmDialog(true);
  };

  const confirmReview = () => {
    if (selectedWish) {
      reviewMutation.mutate({ wishId: selectedWish.id, decision: confirmAction });
    }
  };

  if (loading || wishesLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  // 按课题分组
  const wishesByTopic = pendingWishes?.reduce((acc: any, wish: any) => {
    const topicId = wish.topic?.id || 0;
    if (!acc[topicId]) {
      acc[topicId] = { topic: wish.topic, wishes: [] };
    }
    acc[topicId].wishes.push(wish);
    return acc;
  }, {}) || {};

  // 判断学生是否为分流学生（用于分流优先模式逻辑，但不向导师显示）
  const isTransferStudent = (wish: any) => wish.student?.studentType === "transfer";

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
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}>
              <Globe className="w-4 h-4 mr-2" />{language === "zh" ? "EN" : "中"}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />{t.logout}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => setLocation("/teacher")}>
            <ArrowLeft className="w-4 h-4 mr-2" />{t.back}
          </Button>
          <h1 className="text-2xl font-bold">{language === "zh" ? "志愿审核" : "Application Review"}</h1>
        </div>

        {/* 名额已满预警横幅 - 仅对中方导师显示 */}
        {isQuotaFull && isChineseTeacher && (
          <Card className="mb-6 border-red-400 bg-red-50">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-red-800">
                  <p className="font-bold mb-2 text-base">
                    {language === "zh" ? "系统提示：中方导师确认名额已满" : "System Notice: Chinese Teacher Quota Full"}
                  </p>
                  <p>
                    {language === "zh" 
                      ? `当前中方导师可确认学生总名额已满（${quotaStatus?.confirmedCount || 0}/${quotaStatus?.totalQuota || 0}），您将无法再确认新的学生志愿。如有疑问请联系管理员。`
                      : `The total confirmation quota for Chinese teachers is full (${quotaStatus?.confirmedCount || 0}/${quotaStatus?.totalQuota || 0}). You cannot confirm new applications. Please contact admin if needed.`}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 分流学生优先模式预警横幅 - 仅对中方导师显示 */}
        {isTransferPriorityMode && isChineseTeacher && (
          <Card className="mb-6 border-amber-400 bg-amber-50">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-amber-800">
                  <p className="font-bold mb-2 text-base">
                    {language === "zh" ? "系统提示：分流优先模式已启动" : "System Notice: Single-Degree Priority Mode Active"}
                  </p>
                  <p>
                    {language === "zh" 
                      ? "当前可接收非分流学生的总课题额度已用尽。此后志愿审核仅可对分流学生进行操作，请拒绝来自非分流学生的新志愿。请优先考虑分流学生。"
                      : "The quota for Dual-Degree students has been exhausted. Only Single-Degree student applications can be approved. Please reject applications from Dual-Degree students. Please prioritize Single-Degree students."}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 说明卡片 */}
        <Card className="mb-6 border-blue-200 bg-blue-50">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">{language === "zh" ? "志愿优先，教师确认制" : "Preference-First, Teacher-Confirmation"}</p>
                <p>{language === "zh" 
                  ? "以下是将您的课题作为当前志愿的学生申请。每个课题必须选择一个学生，请点击「同意」录取您认为合适的学生。"
                  : "Below are student applications for your topics. Each topic must select one student. Please click 'Approve' to accept the student you find suitable."}</p>
                {pendingWishes && pendingWishes.length > 0 && (pendingWishes[0] as any).currentReviewPriority > 0 && (
                  <p className="mt-2 font-medium text-blue-800">
                    {language === "zh" 
                      ? `当前审核轮次：第${(pendingWishes[0] as any).currentReviewPriority}志愿`
                      : `Current Review Round: Choice #${(pendingWishes[0] as any).currentReviewPriority}`}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {Object.keys(wishesByTopic).length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>{language === "zh" ? "暂无待审核的学生申请" : "No pending applications"}</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {Object.values(wishesByTopic).map((group: any) => (
              <Card key={group.topic?.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{group.topic?.titleEn || group.topic?.title || "Unknown Topic"}</CardTitle>
                  <CardDescription>
                    {language === "zh" ? `${group.wishes.length} 位学生申请` : `${group.wishes.length} student(s) applied`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {group.wishes.map((wish: any) => {
                      const isTransfer = isTransferStudent(wish);
                      // 在分流学生优先模式下或名额已满时，中方导师受限制，英方导师不受影响
                      const canApprove = !isChineseTeacher || (!isQuotaFull && (!isTransferPriorityMode || isTransfer));
                      // 不同意按钮逻辑：
                      // - 正常情况下禁用（每个课题必须选择一个学生）
                      // - 分流优先模式下，中方导师可以对非分流学生使用不同意
                      // - 英方导师不受分流优先模式影响
                      const canReject = (isTransferPriorityMode || isQuotaFull) && isChineseTeacher && !isTransfer;
                      
                      return (
                        <div key={wish.id} className="border rounded-lg p-4 bg-white">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-4">
                              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                                <User className="w-5 h-5 text-gray-600" />
                              </div>
                              <div>
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className="font-medium">{wish.student?.name || "Unknown"}</span>
                                  {wish.student?.namePinyin && (
                                    <span className="text-gray-500 font-normal">({wish.student.namePinyin})</span>
                                  )}
                                  <Badge variant="outline">
                                    {language === "zh" ? `第${wish.priority}志愿` : `Choice #${wish.priority}`}
                                  </Badge>
                                  {/* 学生分流/非分流身份对导师隐藏，不显示相关标签 */}
                                </div>
                                <p className="text-sm text-gray-500 mt-1">
                                  {wish.student?.email}
                                  {wish.student?.studentId && ` | ${language === "zh" ? "学号" : "ID"}: ${wish.student.studentId}`}
                                </p>
                                <p className="text-sm text-gray-500">
                                  {wish.student?.studentMajor === "electronic_info" 
                                    ? (language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering")
                                    : (language === "zh" ? "通信工程" : "Communications Engineering")}
                                  {wish.student?.studentClass && ` | ${wish.student.studentClass}`}
                                </p>
                                {wish.statement && (
                                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                    <p className="text-xs text-gray-500 mb-1">{language === "zh" ? "选题声明" : "Statement"}</p>
                                    <p className="text-sm text-gray-700">{wish.statement}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              {canReject ? (
                                <Button 
                                  size="sm" 
                                  variant="outline" 
                                  className="text-red-600 hover:bg-red-50"
                                  onClick={() => handleReview(wish, "rejected")}
                                >
                                  <X className="w-4 h-4 mr-1" />
                                  {language === "zh" ? "不同意" : "Reject"}
                                </Button>
                              ) : (
                                <Button 
                                  size="sm" 
                                  variant="outline" 
                                  className="text-gray-400 cursor-not-allowed"
                                  disabled
                                  title={language === "zh" ? "每个课题必须选择一个学生" : "Each topic must select one student"}
                                >
                                  <X className="w-4 h-4 mr-1" />
                                  {language === "zh" ? "不同意" : "Reject"}
                                </Button>
                              )}
                              {canApprove ? (
                                <Button 
                                  size="sm"
                                  onClick={() => handleReview(wish, "approved")}
                                >
                                  <Check className="w-4 h-4 mr-1" />
                                  {language === "zh" ? "同意" : "Approve"}
                                </Button>
                              ) : (
                                <Button 
                                  size="sm"
                                  variant="secondary"
                                  disabled
                                  className="cursor-not-allowed"
                                  title={language === "zh" ? (isQuotaFull ? "中方导师确认名额已满" : "分流优先模式下，该学生无法被录取") : (isQuotaFull ? "Chinese teacher quota is full" : "This student cannot be approved in Single-Degree priority mode")}
                                >
                                  <Check className="w-4 h-4 mr-1" />
                                  {language === "zh" ? "同意" : "Approve"}
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* 确认对话框 */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {confirmAction === "approved" 
                ? (language === "zh" ? "确认录取学生" : "Confirm Acceptance")
                : (language === "zh" ? "确认拒绝申请" : "Confirm Rejection")}
            </DialogTitle>
            <DialogDescription>
              {confirmAction === "approved" 
                ? (language === "zh" 
                    ? `确定要录取学生「${selectedWish?.student?.name}」吗？录取后该学生将与您的课题匹配成功。`
                    : `Are you sure you want to accept "${selectedWish?.student?.name}"? The student will be matched with your topic.`)
                : (language === "zh" 
                    ? `确定要拒绝学生「${selectedWish?.student?.name}」的申请吗？该学生将进入其下一志愿的审核队列。`
                    : `Are you sure you want to reject "${selectedWish?.student?.name}"? The student will move to their next preference.`)}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              variant={confirmAction === "approved" ? "default" : "destructive"}
              onClick={confirmReview}
              disabled={reviewMutation.isPending}
            >
              {reviewMutation.isPending 
                ? (language === "zh" ? "处理中..." : "Processing...")
                : (confirmAction === "approved" 
                    ? (language === "zh" ? "确认录取" : "Confirm Accept")
                    : (language === "zh" ? "确认拒绝" : "Confirm Reject"))}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
