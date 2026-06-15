import { useAuth } from "@/_core/hooks/useAuth";
import { prefixFileUrl } from "@/lib/basePath";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, FileText, Download, Eye, Star, CheckCircle, Clock, AlertCircle, GraduationCap, Globe, LogOut, Lock, Users, Search, X, AlertTriangle, Filter } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";

type ReviewRole = 'first' | 'second';

export default function ThesisReview() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  // 状态管理
  const [activeRole, setActiveRole] = useState<ReviewRole>('first');
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [scoreDialogOpen, setScoreDialogOpen] = useState(false);
  const [scoreInput, setScoreInput] = useState("");
  const [commentInput, setCommentInput] = useState("");
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [editScoreDialogOpen, setEditScoreDialogOpen] = useState(false);
  const [editScoreInput, setEditScoreInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [showOnlyNegotiation, setShowOnlyNegotiation] = useState(false);

  // 获取第一导师评审任务列表
  const { data: firstTeacherTasks, isLoading: firstTasksLoading, refetch: refetchFirst } = trpc.secondTeacher.getFirstTeacherReviewTasks.useQuery(undefined, {
    enabled: isAuthenticated,
  });

  // 获取第二导师评审任务列表
  const { data: secondTeacherTasks, isLoading: secondTasksLoading, refetch: refetchSecond } = trpc.secondTeacher.getReviewTasks.useQuery(undefined, {
    enabled: isAuthenticated,
  });

  // 第一导师提交评分
  const submitFirstScoreMutation = trpc.secondTeacher.submitFirstTeacherScore.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "评分提交成功" : "Score submitted successfully");
      setScoreDialogOpen(false);
      setConfirmDialogOpen(false);
      setScoreInput("");
      setCommentInput("");
      setSelectedTask(null);
      refetchFirst();
      refetchSecond();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  // 导师修改评分（用于分差>10分时协商后修改）
  const updateScoreMutation = trpc.secondTeacher.updateScore.useMutation({
    onSuccess: (result) => {
      if (result.message) {
        if (result.finalScore !== undefined && result.finalScore !== null) {
          toast.success(result.message, { duration: 5000 });
        } else {
          toast.info(result.message, { duration: 5000 });
        }
      } else {
        toast.success(language === "zh" ? "评分修改成功" : "Score updated successfully");
      }
      setEditScoreDialogOpen(false);
      setEditScoreInput("");
      setSelectedTask(null);
      refetchFirst();
      refetchSecond();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  // 第二导师提交评分
  const submitSecondScoreMutation = trpc.secondTeacher.submitScore.useMutation({
    onSuccess: (result) => {
      if (result.message) {
        // 根据返回的消息显示不同的提示
        if (result.message.includes("评分一致") || result.message.includes("≤10分")) {
          toast.success(result.message, { duration: 5000 });
        } else if (result.message.includes(">10分") || result.message.includes("协商")) {
          toast.warning(result.message, { duration: 8000 });
        } else {
          toast.success(result.message);
        }
      } else {
        toast.success(language === "zh" ? "评分提交成功" : "Score submitted successfully");
      }
      setScoreDialogOpen(false);
      setConfirmDialogOpen(false);
      setScoreInput("");
      setCommentInput("");
      setSelectedTask(null);
      refetchFirst();
      refetchSecond();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "teacher" && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  if (loading || firstTasksLoading || secondTasksLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  // 获取评分时间段状态
  const firstScoringPeriodStatus = firstTeacherTasks?.scoringPeriodStatus;
  const secondScoringPeriodStatus = secondTeacherTasks?.scoringPeriodStatus;
  
  // 使用任一个可用的评分时间段状态
  const scoringPeriodStatus = firstScoringPeriodStatus || secondScoringPeriodStatus;
  const isInScoringPeriod = scoringPeriodStatus?.isInScoringPeriod || false;

  // 搜索筛选函数
  const filterBySearch = (task: any) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.trim().toLowerCase();
    const studentName = (task.studentName || '').toLowerCase();
    const chineseId = (task.chineseStudentId || '').toLowerCase();
    const britishId = (task.britishStudentId || '').toLowerCase();
    const topicTitle = (task.topicTitle || '').toLowerCase();
    const topicTitleEn = (task.topicTitleEn || '').toLowerCase();
    return studentName.includes(query) || chineseId.includes(query) || britishId.includes(query) || topicTitle.includes(query) || topicTitleEn.includes(query);
  };

  // 第一导师任务分类
  const firstTasks = firstTeacherTasks?.tasks || [];
  const firstPendingTasks = firstTasks.filter(task => task.status === 'pending' && task.draftId).filter(filterBySearch) || [];
  const firstScoredTasks = firstTasks.filter(task => task.status === 'scored').filter(filterBySearch) || [];
  const firstScoredDisplayTasks = showOnlyNegotiation ? firstScoredTasks.filter(task => task.needsNegotiation) : firstScoredTasks;
  const firstNoDraftTasks = firstTasks.filter(task => !task.draftId).filter(filterBySearch) || [];
  const firstNegotiationCount = firstTasks.filter(task => task.status === 'scored' && task.needsNegotiation).length;

  // 第二导师任务分类
  const secondTasks = secondTeacherTasks?.tasks || [];
  const secondPendingTasks = secondTasks.filter(task => task.status === 'pending' && task.canScore).filter(filterBySearch) || [];
  const secondScoredTasks = secondTasks.filter(task => task.status === 'scored').filter(filterBySearch) || [];
  const secondScoredDisplayTasks = showOnlyNegotiation ? secondScoredTasks.filter(task => task.needsNegotiation) : secondScoredTasks;
  const secondNoDraftTasks = secondTasks.filter(task => !task.draftId).filter(filterBySearch) || [];
  const secondNegotiationCount = secondTasks.filter(task => task.status === 'scored' && task.needsNegotiation).length;

  // 总需协商数量（用于红点提示）
  const totalNegotiationCount = firstNegotiationCount + secondNegotiationCount;

  // 打开评分对话框
  const handleOpenScoreDialog = (task: any, role: ReviewRole) => {
    setSelectedTask({ ...task, role });
    setScoreInput("");
    setCommentInput("");
    setScoreDialogOpen(true);
  };

  // 打开修改评分对话框（用于分差>10分时协商后修改）
  const handleOpenEditScoreDialog = (task: any, role: ReviewRole) => {
    setSelectedTask({ ...task, role });
    setEditScoreInput(role === 'first' ? String(task.firstTeacherScore ?? '') : String(task.secondTeacherScore ?? ''));
    setEditScoreDialogOpen(true);
  };

  // 提交修改后的评分
  const handleSubmitEditScore = () => {
    if (!selectedTask || !selectedTask.draftId) return;
    const score = parseFloat(editScoreInput);
    if (isNaN(score) || score < 0 || score > 100) {
      toast.error(language === "zh" ? "请输入0-100之间的有效分数" : "Please enter a valid score between 0-100");
      return;
    }
    const roundedScore = Math.round(score * 10) / 10;
    updateScoreMutation.mutate({
      draftId: selectedTask.draftId,
      newScore: roundedScore,
      isFirstTeacher: selectedTask.role === 'first',
    });
  };

  // 提交评分前确认
  const handleScoreConfirm = () => {
    const score = parseFloat(scoreInput);
    if (isNaN(score) || score < 0 || score > 100) {
      toast.error(language === "zh" ? "请输入0-100之间的有效分数" : "Please enter a valid score between 0-100");
      return;
    }
    setConfirmDialogOpen(true);
  };

  // 确认提交评分
  const handleSubmitScore = () => {
    if (!selectedTask || !selectedTask.draftId) return;
    const score = parseFloat(scoreInput);
    const roundedScore = Math.round(score * 10) / 10;

    if (selectedTask.role === 'first') {
      submitFirstScoreMutation.mutate({
        draftId: selectedTask.draftId,
        score: roundedScore,
        comment: commentInput.trim() || undefined,
      });
    } else {
      submitSecondScoreMutation.mutate({
        draftId: selectedTask.draftId,
        score: roundedScore,
        comment: commentInput.trim() || undefined,
      });
    }
  };

  // 预览论文
  const handlePreviewDraft = (fileUrl: string) => {
    window.open(prefixFileUrl(fileUrl), '_blank');
  };

  // 下载论文
  const handleDownloadDraft = (fileUrl: string, fileName: string) => {
    const link = document.createElement('a');
    link.href = prefixFileUrl(fileUrl);
    link.download = fileName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 渲染第一导师任务卡片
  const renderFirstTeacherTaskCard = (task: any, showScoreButton: boolean = false) => (
    <Card key={task.matchId} className={`mb-4 ${task.needsNegotiation ? 'border-2 border-red-400 shadow-red-100 shadow-md ring-1 ring-red-200' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">
              {task.studentName || (language === "zh" ? "未知学生" : "Unknown Student")}
            </CardTitle>
            <CardDescription className="mt-1">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span>{language === "zh" ? "中方学号" : "Chinese ID"}: {task.chineseStudentId || "-"}</span>
                <span>{language === "zh" ? "英方学号" : "Sussex ID"}: {task.britishStudentId || "-"}</span>
              </div>
            </CardDescription>
          </div>
          <Badge variant={task.status === 'scored' ? 'default' : 'secondary'}>
            {task.status === 'scored' 
              ? (language === "zh" ? "已评分" : "Scored")
              : (language === "zh" ? "待评分" : "Pending")}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* 第二导师信息 */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="font-medium">{language === "zh" ? "第二导师" : "Second Supervisor"}:</span>
            <span>{task.secondTeacherName || (language === "zh" ? "未指派" : "Not assigned")}</span>
          </div>

          {/* 论文题目 */}
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">{language === "zh" ? "论文题目" : "Thesis Title"}</p>
            <p className="text-sm">{task.topicTitleEn || task.topicTitle}</p>
          </div>

          {/* 论文信息 */}
          {task.draftFileName && (
            <div className="flex items-center justify-between bg-blue-50 p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">{task.draftFileName}</p>
                  <p className="text-xs text-gray-500">
                    {language === "zh" ? "提交时间" : "Submitted"}: {task.draftSubmittedAt ? new Date(task.draftSubmittedAt).toLocaleString() : "-"}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePreviewDraft(task.draftFileUrl)}
                >
                  <Eye className="w-4 h-4 mr-1" />
                  {language === "zh" ? "预览" : "Preview"}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownloadDraft(task.draftFileUrl, task.draftFileName)}
                >
                  <Download className="w-4 h-4 mr-1" />
                  {language === "zh" ? "下载" : "Download"}
                </Button>
              </div>
            </div>
          )}

          {/* 评分信息 */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">{language === "zh" ? "我的评分（第一导师）" : "My Score (First)"}</p>
              <p className="text-lg font-bold text-blue-600">
                {task.firstTeacherScore !== null ? task.firstTeacherScore : "-"}
              </p>
              {task.firstTeacherScoredAt && (
                <p className="text-xs text-gray-400">
                  {new Date(task.firstTeacherScoredAt).toLocaleDateString()}
                </p>
              )}
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">{language === "zh" ? "第二导师评分" : "Second Supervisor Score"}</p>
              {task.bothScored ? (
                <>
                  <p className="text-lg font-bold text-green-600">
                    {task.secondTeacherScore !== null ? task.secondTeacherScore : "-"}
                  </p>
                  {task.secondTeacherScoredAt && (
                    <p className="text-xs text-gray-400">
                      {new Date(task.secondTeacherScoredAt).toLocaleDateString()}
                    </p>
                  )}
                </>
              ) : (
                <div className="flex items-center gap-1 text-gray-400">
                  <Lock className="w-4 h-4" />
                  <span className="text-sm">{language === "zh" ? "双方评分后可见" : "Visible after both score"}</span>
                </div>
              )}
            </div>
          </div>

          {/* 最终成绩显示 */}
          {task.bothScored && task.finalScore !== null && (
            <div className="bg-green-50 border border-green-200 p-3 rounded-lg mt-3">
              <p className="text-sm font-medium text-green-800">
                {language === "zh" ? "最终成绩" : "Final Score"}: 
                <span className="text-lg ml-2 font-bold">{task.finalScore}</span>
                {task.latePenalty > 0 && (
                  <span className="text-xs text-orange-600 ml-2">
                    (已扣除迟交罚分{task.latePenalty}分)
                  </span>
                )}
              </p>
            </div>
          )}

          {/* 两位导师都评分但未确定最终成绩时显示预估最终成绩 */}
          {task.bothScored && task.finalScore === null && !task.needsNegotiation && (
            <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg mt-3">
              <p className="text-sm font-medium text-blue-800">
                {language === "zh" ? "预估最终成绩" : "Estimated Final Score"}: 
                {(() => {
                  const avg = Math.round(((task.firstTeacherScore ?? 0) + (task.secondTeacherScore ?? 0)) / 2 * 10) / 10;
                  const penalty = task.latePenalty ?? 0;
                  const est = Math.max(0, Math.round((avg - penalty) * 10) / 10);
                  return (
                    <>
                      <span className="text-lg ml-2 font-bold">{est}</span>
                      {penalty > 0 && (
                        <span className="text-xs text-orange-600 ml-2">
                          (平均分{avg} - 迟交扣分{penalty})
                        </span>
                      )}
                    </>
                  );
                })()}
              </p>
            </div>
          )}

          {/* 分差>10分协商提示 - 醒目红色样式 */}
          {task.bothScored && task.finalScore === null && task.needsNegotiation && (
            <div className="bg-red-50 border-2 border-red-400 p-4 rounded-lg mt-3 animate-pulse-subtle">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-bold text-red-800 mb-1">
                    {language === "zh" ? "⚠ 需要协商修改评分" : "⚠ Score Negotiation Required"}
                  </p>
                  <p className="text-sm text-red-700 mb-3">
                    {language === "zh" 
                      ? `两位导师评分差异超过10分（差异: ${Math.abs((task.firstTeacherScore ?? 0) - (task.secondTeacherScore ?? 0))}分），请与第二导师协商后修改评分` 
                      : `Score difference exceeds 10 points (${Math.abs((task.firstTeacherScore ?? 0) - (task.secondTeacherScore ?? 0))} points). Please negotiate with the second supervisor.`}
                  </p>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="w-full"
                    onClick={() => handleOpenEditScoreDialog(task, 'first')}
                  >
                    {language === "zh" ? "修改我的评分" : "Edit My Score"}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* 评分按钮 */}
          {showScoreButton && task.draftId && task.status === 'pending' && (
            <Button
              className="w-full mt-3"
              onClick={() => handleOpenScoreDialog(task, 'first')}
              disabled={!isInScoringPeriod}
            >
              <Star className="w-4 h-4 mr-2" />
              {isInScoringPeriod 
                ? (language === "zh" ? "提交评分" : "Submit Score")
                : (language === "zh" ? "不在评分时间段" : "Not in Scoring Period")}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  // 渲染第二导师任务卡片
  const renderSecondTeacherTaskCard = (task: any, showScoreButton: boolean = false) => (
    <Card key={task.matchId} className={`mb-4 ${task.needsNegotiation ? 'border-2 border-red-400 shadow-red-100 shadow-md ring-1 ring-red-200' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">
              {task.studentName || (language === "zh" ? "未知学生" : "Unknown Student")}
            </CardTitle>
            <CardDescription className="mt-1">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span>{language === "zh" ? "中方学号" : "Chinese ID"}: {task.chineseStudentId || "-"}</span>
                <span>{language === "zh" ? "英方学号" : "Sussex ID"}: {task.britishStudentId || "-"}</span>
              </div>
            </CardDescription>
          </div>
          <Badge variant={task.status === 'scored' ? 'default' : 'secondary'}>
            {task.status === 'scored' 
              ? (language === "zh" ? "已评分" : "Scored")
              : (language === "zh" ? "待评分" : "Pending")}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* 第一导师信息 */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="font-medium">{language === "zh" ? "第一导师" : "First Supervisor"}:</span>
            <span>{task.firstTeacherName || "-"}</span>
          </div>

          {/* 论文题目 */}
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">{language === "zh" ? "论文题目" : "Thesis Title"}</p>
            <p className="text-sm">{task.topicTitleEn || task.topicTitle}</p>
          </div>

          {/* 论文信息 */}
          {task.draftFileName && (
            <div className="flex items-center justify-between bg-blue-50 p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">{task.draftFileName}</p>
                  <p className="text-xs text-gray-500">
                    {language === "zh" ? "提交时间" : "Submitted"}: {task.draftSubmittedAt ? new Date(task.draftSubmittedAt).toLocaleString() : "-"}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePreviewDraft(task.draftFileUrl)}
                >
                  <Eye className="w-4 h-4 mr-1" />
                  {language === "zh" ? "预览" : "Preview"}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownloadDraft(task.draftFileUrl, task.draftFileName)}
                >
                  <Download className="w-4 h-4 mr-1" />
                  {language === "zh" ? "下载" : "Download"}
                </Button>
              </div>
            </div>
          )}

          {/* 评分信息 */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">{language === "zh" ? "第一导师评分" : "First Supervisor Score"}</p>
              {task.bothScored ? (
                <>
                  <p className="text-lg font-bold text-blue-600">
                    {task.firstTeacherScore !== null ? task.firstTeacherScore : "-"}
                  </p>
                  {task.firstTeacherScoredAt && (
                    <p className="text-xs text-gray-400">
                      {new Date(task.firstTeacherScoredAt).toLocaleDateString()}
                    </p>
                  )}
                </>
              ) : (
                <div className="flex items-center gap-1 text-gray-400">
                  <Lock className="w-4 h-4" />
                  <span className="text-sm">{language === "zh" ? "双方评分后可见" : "Visible after both score"}</span>
                </div>
              )}
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">{language === "zh" ? "我的评分（第二导师）" : "My Score (Second)"}</p>
              <p className="text-lg font-bold text-green-600">
                {task.secondTeacherScore !== null ? task.secondTeacherScore : "-"}
              </p>
              {task.secondTeacherScoredAt && (
                <p className="text-xs text-gray-400">
                  {new Date(task.secondTeacherScoredAt).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>

          {/* 最终成绩显示 */}
          {task.bothScored && task.finalScore !== null && (
            <div className="bg-green-50 border border-green-200 p-3 rounded-lg mt-3">
              <p className="text-sm font-medium text-green-800">
                {language === "zh" ? "最终成绩" : "Final Score"}: 
                <span className="text-lg ml-2 font-bold">{task.finalScore}</span>
                {task.latePenalty > 0 && (
                  <span className="text-xs text-orange-600 ml-2">
                    (已扣除迟交罚分{task.latePenalty}分)
                  </span>
                )}
              </p>
            </div>
          )}

          {/* 两位导师都评分但未确定最终成绩时显示预估最终成绩 */}
          {task.bothScored && task.finalScore === null && !task.needsNegotiation && (
            <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg mt-3">
              <p className="text-sm font-medium text-blue-800">
                {language === "zh" ? "预估最终成绩" : "Estimated Final Score"}: 
                {(() => {
                  const avg = Math.round(((task.firstTeacherScore ?? 0) + (task.secondTeacherScore ?? 0)) / 2 * 10) / 10;
                  const penalty = task.latePenalty ?? 0;
                  const est = Math.max(0, Math.round((avg - penalty) * 10) / 10);
                  return (
                    <>
                      <span className="text-lg ml-2 font-bold">{est}</span>
                      {penalty > 0 && (
                        <span className="text-xs text-orange-600 ml-2">
                          (平均分{avg} - 迟交扣分{penalty})
                        </span>
                      )}
                    </>
                  );
                })()}
              </p>
            </div>
          )}

          {/* 分差>10分协商提示 - 醒目红色样式 */}
          {task.bothScored && task.finalScore === null && task.needsNegotiation && (
            <div className="bg-red-50 border-2 border-red-400 p-4 rounded-lg mt-3 animate-pulse-subtle">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-bold text-red-800 mb-1">
                    {language === "zh" ? "⚠ 需要协商修改评分" : "⚠ Score Negotiation Required"}
                  </p>
                  <p className="text-sm text-red-700 mb-3">
                    {language === "zh" 
                      ? `两位导师评分差异超过10分（差异: ${Math.abs((task.firstTeacherScore ?? 0) - (task.secondTeacherScore ?? 0))}分），请与第一导师协商后修改评分` 
                      : `Score difference exceeds 10 points (${Math.abs((task.firstTeacherScore ?? 0) - (task.secondTeacherScore ?? 0))} points). Please negotiate with the first supervisor.`}
                  </p>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="w-full"
                    onClick={() => handleOpenEditScoreDialog(task, 'second')}
                  >
                    {language === "zh" ? "修改我的评分" : "Edit My Score"}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* 评分按钮 */}
          {showScoreButton && task.draftId && task.canScore && (
            <Button
              className="w-full mt-3"
              onClick={() => handleOpenScoreDialog(task, 'second')}
              disabled={!isInScoringPeriod}
            >
              <Star className="w-4 h-4 mr-2" />
              {isInScoringPeriod 
                ? (language === "zh" ? "提交评分" : "Submit Score")
                : (language === "zh" ? "不在评分时间段" : "Not in Scoring Period")}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const hasFirstTeacherTasks = firstTasks && firstTasks.length > 0;
  const hasSecondTeacherTasks = secondTasks && secondTasks.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => setLocation("/teacher")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              {language === "zh" ? "返回" : "Back"}
            </Button>
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.name} ({t.roles.teacher})</span>
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}>
              <Globe className="w-4 h-4 mr-2" />
              {language === "zh" ? "EN" : "中"}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              {t.logout}
            </Button>
          </div>
        </div>
      </header>

      {/* 主内容 */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold relative inline-block">
            {language === "zh" ? "论文评审" : "Thesis Review"}
            {totalNegotiationCount > 0 && (
              <span className="absolute -top-2 -right-8 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center animate-pulse">{totalNegotiationCount}</span>
            )}
          </h1>
          <p className="text-gray-600 mt-1">
            {language === "zh" 
              ? "审阅学生论文并提交评分（双方评分完成后可见对方分数）" 
              : "Review student theses and submit scores (scores visible after both supervisors submit)"}
          </p>
        </div>

        {/* 搜索框 */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder={language === "zh" ? "搜索学生姓名、学号或论文题目..." : "Search by student name, ID or thesis title..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* 评分时间段状态卡片 */}
        {scoringPeriodStatus && (
          <Card className={`mb-6 ${isInScoringPeriod ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
            <CardContent className="py-4">
              <div className="flex items-center gap-3">
                {isInScoringPeriod ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <Clock className="w-5 h-5 text-gray-500" />
                )}
                <div>
                  <p className={`text-sm font-medium ${isInScoringPeriod ? 'text-green-800' : 'text-gray-700'}`}>
                    {language === "zh" ? "评分时间段状态" : "Scoring Period Status"}
                  </p>
                  <p className={`text-sm ${isInScoringPeriod ? 'text-green-600' : 'text-gray-500'}`}>
                    {scoringPeriodStatus.message}
                  </p>
                  {scoringPeriodStatus.scoringStart && scoringPeriodStatus.scoringEnd && (
                    <p className="text-xs text-gray-400 mt-1">
                      {language === "zh" ? "评分时间段" : "Scoring Period"}: {new Date(scoringPeriodStatus.scoringStart).toLocaleString()} - {new Date(scoringPeriodStatus.scoringEnd).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 角色切换 */}
        <Tabs value={activeRole} onValueChange={(v) => setActiveRole(v as ReviewRole)} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="first" className="flex items-center gap-2 relative">
              <Users className="w-4 h-4" />
              {language === "zh" ? "作为第一导师" : "As First Supervisor"}
              {hasFirstTeacherTasks && (
                <Badge variant="secondary" className="ml-1">{firstTasks.length}</Badge>
              )}
              {firstNegotiationCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center animate-pulse">{firstNegotiationCount}</span>
              )}
            </TabsTrigger>
            <TabsTrigger value="second" className="flex items-center gap-2 relative">
              <Users className="w-4 h-4" />
              {language === "zh" ? "作为第二导师" : "As Second Supervisor"}
              {hasSecondTeacherTasks && (
                <Badge variant="secondary" className="ml-1">{secondTasks.length}</Badge>
              )}
              {secondNegotiationCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center animate-pulse">{secondNegotiationCount}</span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* 第一导师视图 */}
          <TabsContent value="first">
            {/* 统计卡片 */}
            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-orange-500" />
                    {language === "zh" ? "待评分" : "Pending"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">{firstPendingTasks.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    {language === "zh" ? "已评分" : "Scored"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{firstScoredTasks.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-gray-500" />
                    {language === "zh" ? "未提交论文" : "No Thesis"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-600">{firstNoDraftTasks.length}</div>
                </CardContent>
              </Card>
            </div>

            {/* 任务列表 */}
            {hasFirstTeacherTasks ? (
              <Tabs defaultValue="pending" className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-6">
                  <TabsTrigger value="pending">
                    {language === "zh" ? "待评分" : "Pending"} ({firstPendingTasks.length})
                  </TabsTrigger>
                  <TabsTrigger value="scored">
                    {language === "zh" ? "已评分" : "Scored"} ({firstScoredTasks.length})
                  </TabsTrigger>
                  <TabsTrigger value="nodraft">
                    {language === "zh" ? "未提交" : "No Thesis"} ({firstNoDraftTasks.length})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="pending">
                  {firstPendingTasks.length > 0 ? (
                    firstPendingTasks.map(task => renderFirstTeacherTaskCard(task, true))
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center text-gray-500">
                        <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                        <p>{language === "zh" ? "暂无待评分的论文" : "No pending reviews"}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="scored">
                  {/* 协商筛选按钮 */}
                  {firstNegotiationCount > 0 && (
                    <div className="flex items-center gap-2 mb-4">
                      <Button
                        variant={showOnlyNegotiation ? "destructive" : "outline"}
                        size="sm"
                        onClick={() => setShowOnlyNegotiation(!showOnlyNegotiation)}
                        className="flex items-center gap-2"
                      >
                        <Filter className="w-4 h-4" />
                        {language === "zh" ? "需协商" : "Needs Negotiation"}
                        <Badge variant="secondary" className={`ml-1 ${showOnlyNegotiation ? 'bg-white/20 text-white' : 'bg-red-100 text-red-700'}`}>{firstNegotiationCount}</Badge>
                      </Button>
                      {showOnlyNegotiation && (
                        <Button variant="ghost" size="sm" onClick={() => setShowOnlyNegotiation(false)}>
                          <X className="w-4 h-4 mr-1" />
                          {language === "zh" ? "显示全部" : "Show All"}
                        </Button>
                      )}
                    </div>
                  )}
                  {firstScoredDisplayTasks.length > 0 ? (
                    firstScoredDisplayTasks.map(task => renderFirstTeacherTaskCard(task, false))
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>{language === "zh" ? (showOnlyNegotiation ? "暂无需要协商的论文" : "暂无已评分的论文") : (showOnlyNegotiation ? "No reviews need negotiation" : "No scored reviews")}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="nodraft">
                  {firstNoDraftTasks.length > 0 ? (
                    <>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                        <p className="text-sm text-gray-600">
                          {language === "zh" 
                            ? "以下学生尚未提交论文终稿。" 
                            : "The following students have not submitted their thesis."}
                        </p>
                      </div>
                      {firstNoDraftTasks.map(task => renderFirstTeacherTaskCard(task, false))}
                    </>
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>{language === "zh" ? "所有学生都已提交论文" : "All students have submitted"}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>
              </Tabs>
            ) : (
              <Card>
                <CardContent className="py-12 text-center text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium mb-2">
                    {language === "zh" ? "暂无评审任务" : "No Review Tasks"}
                  </p>
                  <p className="text-sm">
                    {language === "zh" 
                      ? "您作为第一导师暂无需要评分的分流学生论文" 
                      : "You have no Single-Degree student theses to review as first supervisor"}
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* 第二导师视图 */}
          <TabsContent value="second">
            {/* 统计卡片 */}
            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-orange-500" />
                    {language === "zh" ? "待评分" : "Pending"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">{secondPendingTasks.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    {language === "zh" ? "已评分" : "Scored"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{secondScoredTasks.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-gray-500" />
                    {language === "zh" ? "未提交论文" : "No Thesis"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-600">{secondNoDraftTasks.length}</div>
                </CardContent>
              </Card>
            </div>

            {/* 任务列表 */}
            {hasSecondTeacherTasks ? (
              <Tabs defaultValue="pending" className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-6">
                  <TabsTrigger value="pending">
                    {language === "zh" ? "待评分" : "Pending"} ({secondPendingTasks.length})
                  </TabsTrigger>
                  <TabsTrigger value="scored">
                    {language === "zh" ? "已评分" : "Scored"} ({secondScoredTasks.length})
                  </TabsTrigger>
                  <TabsTrigger value="nodraft">
                    {language === "zh" ? "未提交" : "No Thesis"} ({secondNoDraftTasks.length})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="pending">
                  {secondPendingTasks.length > 0 ? (
                    secondPendingTasks.map(task => renderSecondTeacherTaskCard(task, true))
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center text-gray-500">
                        <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                        <p>{language === "zh" ? "暂无待评分的论文" : "No pending reviews"}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="scored">
                  {/* 协商筛选按钮 */}
                  {secondNegotiationCount > 0 && (
                    <div className="flex items-center gap-2 mb-4">
                      <Button
                        variant={showOnlyNegotiation ? "destructive" : "outline"}
                        size="sm"
                        onClick={() => setShowOnlyNegotiation(!showOnlyNegotiation)}
                        className="flex items-center gap-2"
                      >
                        <Filter className="w-4 h-4" />
                        {language === "zh" ? "需协商" : "Needs Negotiation"}
                        <Badge variant="secondary" className={`ml-1 ${showOnlyNegotiation ? 'bg-white/20 text-white' : 'bg-red-100 text-red-700'}`}>{secondNegotiationCount}</Badge>
                      </Button>
                      {showOnlyNegotiation && (
                        <Button variant="ghost" size="sm" onClick={() => setShowOnlyNegotiation(false)}>
                          <X className="w-4 h-4 mr-1" />
                          {language === "zh" ? "显示全部" : "Show All"}
                        </Button>
                      )}
                    </div>
                  )}
                  {secondScoredDisplayTasks.length > 0 ? (
                    secondScoredDisplayTasks.map(task => renderSecondTeacherTaskCard(task, false))
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>{language === "zh" ? (showOnlyNegotiation ? "暂无需要协商的论文" : "暂无已评分的论文") : (showOnlyNegotiation ? "No reviews need negotiation" : "No scored reviews")}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="nodraft">
                  {secondNoDraftTasks.length > 0 ? (
                    <>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                        <p className="text-sm text-gray-600">
                          {language === "zh" 
                            ? "以下学生尚未提交论文终稿。" 
                            : "The following students have not submitted their thesis."}
                        </p>
                      </div>
                      {secondNoDraftTasks.map(task => renderSecondTeacherTaskCard(task, false))}
                    </>
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>{language === "zh" ? "所有学生都已提交论文" : "All students have submitted"}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>
              </Tabs>
            ) : (
              <Card>
                <CardContent className="py-12 text-center text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium mb-2">
                    {language === "zh" ? "暂无评审任务" : "No Review Tasks"}
                  </p>
                  <p className="text-sm">
                    {language === "zh" 
                      ? "您尚未被指派为任何学生的第二导师" 
                      : "You have not been assigned as a second supervisor for any student"}
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </main>

      {/* 评分对话框 */}
      <Dialog open={scoreDialogOpen} onOpenChange={setScoreDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "提交评分" : "Submit Score"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `为 ${selectedTask?.studentName} 的论文评分（作为${selectedTask?.role === 'first' ? '第一' : '第二'}导师）` 
                : `Score the thesis of ${selectedTask?.studentName} (as ${selectedTask?.role === 'first' ? 'first' : 'second'} supervisor)`}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {/* 学生和论文信息 */}
            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <p className="text-sm">
                <span className="font-medium">{language === "zh" ? "学生" : "Student"}:</span> {selectedTask?.studentName}
              </p>
              <p className="text-sm">
                <span className="font-medium">{language === "zh" ? "论文题目" : "Title"}:</span> {selectedTask?.topicTitleEn || selectedTask?.topicTitle}
              </p>
              <p className="text-sm">
                <span className="font-medium">{language === "zh" ? "评分身份" : "Role"}:</span> {selectedTask?.role === 'first' ? (language === "zh" ? "第一导师" : "First Supervisor") : (language === "zh" ? "第二导师" : "Second Supervisor")}
              </p>
            </div>

            {/* 分数输入 */}
            <div className="space-y-2">
              <Label htmlFor="score">{language === "zh" ? "评分（0-100分，支持一位小数）" : "Score (0-100, one decimal allowed)"}</Label>
              <Input
                id="score"
                type="number"
                min="0"
                max="100"
                step="0.1"
                placeholder={language === "zh" ? "请输入分数" : "Enter score"}
                value={scoreInput}
                onChange={(e) => setScoreInput(e.target.value)}
              />
            </div>

            {/* 评语输入 */}
            <div className="space-y-2">
              <Label htmlFor="comment">{language === "zh" ? "评审评语（可选）" : "Review Comment (Optional)"}</Label>
              <Textarea
                id="comment"
                placeholder={language === "zh" ? "请输入详细的评审意见..." : "Enter your detailed review comments..."}
                value={commentInput}
                onChange={(e) => setCommentInput(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <p className="text-xs text-gray-500">
                {language === "zh" 
                  ? "评语将与评分一起保存，管理员可以查看" 
                  : "Comments will be saved with the score and visible to administrators"}
              </p>
            </div>

            {/* 警告提示 */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                <AlertCircle className="w-4 h-4 inline mr-1" />
                {language === "zh" 
                  ? "评分提交后不可更改，如需修改请联系管理员。双方评分完成后才能看到对方的分数。" 
                  : "Score cannot be changed after submission. Contact admin if modification is needed. Scores are visible only after both supervisors submit."}
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setScoreDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleScoreConfirm}>
              {language === "zh" ? "提交" : "Submit"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 确认对话框 */}
      <Dialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "确认提交" : "Confirm Submission"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? "评分提交后将无法修改，确定要提交吗？" 
                : "Score cannot be modified after submission. Are you sure?"}
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <p className="text-sm text-gray-600 mb-2">
                {language === "zh" ? "您将为以下学生提交评分：" : "You are about to submit score for:"}
              </p>
              <p className="font-bold text-lg">{selectedTask?.studentName}</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{scoreInput} {language === "zh" ? "分" : ""}</p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              onClick={handleSubmitScore}
              disabled={submitFirstScoreMutation.isPending || submitSecondScoreMutation.isPending}
            >
              {(submitFirstScoreMutation.isPending || submitSecondScoreMutation.isPending)
                ? (language === "zh" ? "提交中..." : "Submitting...")
                : (language === "zh" ? "确认提交" : "Confirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 修改评分对话框（用于分差>10分时协商后修改） */}
      <Dialog open={editScoreDialogOpen} onOpenChange={setEditScoreDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "修改评分" : "Edit Score"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `两位导师评分差异超过10分，请与另一位导师协商后修改您的评分` 
                : `Score difference exceeds 10 points. Please negotiate with the other supervisor and update your score.`}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {/* 当前评分信息 */}
            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <p className="text-sm">
                <span className="font-medium">{language === "zh" ? "学生" : "Student"}:</span> {selectedTask?.studentName}
              </p>
              <p className="text-sm">
                <span className="font-medium">{language === "zh" ? "论文题目" : "Title"}:</span> {selectedTask?.topicTitleEn || selectedTask?.topicTitle}
              </p>
              <div className="grid grid-cols-2 gap-4 mt-3">
                <div className="bg-white p-2 rounded border">
                  <p className="text-xs text-gray-500">{language === "zh" ? "第一导师评分" : "First Supervisor"}</p>
                  <p className="text-lg font-bold text-blue-600">{selectedTask?.firstTeacherScore}</p>
                </div>
                <div className="bg-white p-2 rounded border">
                  <p className="text-xs text-gray-500">{language === "zh" ? "第二导师评分" : "Second Supervisor"}</p>
                  <p className="text-lg font-bold text-green-600">{selectedTask?.secondTeacherScore}</p>
                </div>
              </div>
              <div className="text-center mt-2">
                <p className="text-sm text-orange-600 font-medium">
                  {language === "zh" 
                    ? `当前分差: ${Math.abs((selectedTask?.firstTeacherScore ?? 0) - (selectedTask?.secondTeacherScore ?? 0))}分`
                    : `Current difference: ${Math.abs((selectedTask?.firstTeacherScore ?? 0) - (selectedTask?.secondTeacherScore ?? 0))} points`}
                </p>
              </div>
            </div>

            {/* 新分数输入 */}
            <div className="space-y-2">
              <Label htmlFor="editScore">
                {language === "zh" 
                  ? `您的新评分（作为${selectedTask?.role === 'first' ? '第一' : '第二'}导师）` 
                  : `Your new score (as ${selectedTask?.role === 'first' ? 'first' : 'second'} supervisor)`}
              </Label>
              <Input
                id="editScore"
                type="number"
                min="0"
                max="100"
                step="0.1"
                placeholder={language === "zh" ? "请输入新分数" : "Enter new score"}
                value={editScoreInput}
                onChange={(e) => setEditScoreInput(e.target.value)}
              />
            </div>

            {/* 提示信息 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                <AlertCircle className="w-4 h-4 inline mr-1" />
                {language === "zh" 
                  ? "修改后，如果两位导师的评分差异在10分以内，系统将自动取平均分作为最终成绩。" 
                  : "After modification, if the score difference is within 10 points, the system will automatically calculate the average as the final score."}
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditScoreDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              onClick={handleSubmitEditScore}
              disabled={updateScoreMutation.isPending}
            >
              {updateScoreMutation.isPending
                ? (language === "zh" ? "提交中..." : "Submitting...")
                : (language === "zh" ? "确认修改" : "Confirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
