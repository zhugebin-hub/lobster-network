import { useAuth } from "@/_core/hooks/useAuth";
import { prefixFileUrl } from "@/lib/basePath";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, FileText, Download, Eye, Star, CheckCircle, Clock, AlertCircle, GraduationCap, Globe, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";

export default function SecondTeacherReview() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  // 状态管理
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [scoreDialogOpen, setScoreDialogOpen] = useState(false);
  const [scoreInput, setScoreInput] = useState("");
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  // 获取评审任务列表
  const { data: reviewTasks, isLoading: tasksLoading, refetch } = trpc.secondTeacher.getReviewTasks.useQuery(undefined, {
    enabled: isAuthenticated,
  });

  // 提交评分
  const submitScoreMutation = trpc.secondTeacher.submitScore.useMutation({
    onSuccess: (result) => {
      if (result.message && result.message.includes("评分一致")) {
        toast.success(language === "zh" ? "两位导师评分一致，最终成绩已自动确定" : "Scores match, final score confirmed automatically");
      } else {
        toast.success(language === "zh" ? "评分提交成功" : "Score submitted successfully");
      }
      setScoreDialogOpen(false);
      setConfirmDialogOpen(false);
      setScoreInput("");
      setSelectedTask(null);
      refetch();
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

  if (loading || tasksLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  // 分类任务
  const tasks = reviewTasks?.tasks || [];
  const pendingTasks = tasks.filter((task: any) => task.status === 'pending' && task.firstTeacherScore !== null) || [];
  const scoredTasks = tasks.filter((task: any) => task.status === 'scored') || [];
  const waitingTasks = tasks.filter((task: any) => task.status === 'pending' && task.firstTeacherScore === null) || [];

  // 打开评分对话框
  const handleOpenScoreDialog = (task: any) => {
    setSelectedTask(task);
    setScoreInput("");
    setScoreDialogOpen(true);
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
    submitScoreMutation.mutate({
      draftId: selectedTask.draftId,
      score: Math.round(score * 10) / 10, // 保留一位小数
    });
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

  // 渲染任务卡片
  const renderTaskCard = (task: any, showScoreButton: boolean = false) => (
    <Card key={task.matchId} className="mb-4">
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
              ? (language === "zh" ? "已评审" : "Scored")
              : (language === "zh" ? "待评审" : "Pending")}
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
          {task.firstTeacherScore !== null && task.secondTeacherScore !== null && (() => {
            const avg = Math.round((task.firstTeacherScore + task.secondTeacherScore) / 2 * 10) / 10;
            const penalty = task.latePenalty ?? 0;
            const finalScore = Math.max(0, Math.round((avg - penalty) * 10) / 10);
            return (
              <div className="bg-green-50 border border-green-200 p-3 rounded-lg">
                <p className="text-sm font-medium text-green-800">
                  {language === "zh" ? "最终成绩" : "Final Score"}: 
                  <span className="text-lg ml-2 font-bold">{finalScore}</span>
                  {penalty > 0 && (
                    <span className="text-xs text-orange-600 ml-2">
                      (平均分{avg} - 迟交扣分{penalty} = {finalScore})
                    </span>
                  )}
                </p>
              </div>
            );
          })()}

          {/* 评分按钮 */}
          {showScoreButton && task.draftId && (
            <Button
              className="w-full mt-3"
              onClick={() => handleOpenScoreDialog(task)}
            >
              <Star className="w-4 h-4 mr-2" />
              {language === "zh" ? "提交评分" : "Submit Score"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

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
          <h1 className="text-2xl font-bold">{language === "zh" ? "论文评审" : "Thesis Review"}</h1>
          <p className="text-gray-600 mt-1">
            {language === "zh" 
              ? "作为第二导师，审阅学生论文并提交评分" 
              : "Review student theses and submit scores as second supervisor"}
          </p>
        </div>

        {/* 统计卡片 */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-500" />
                {language === "zh" ? "待评审" : "Pending Review"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{pendingTasks.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                {language === "zh" ? "已评审" : "Scored"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{scoredTasks.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-gray-500" />
                {language === "zh" ? "等待第一导师评分" : "Waiting for First Score"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">{waitingTasks.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* 任务列表 */}
        {tasks && tasks.length > 0 ? (
          <Tabs defaultValue="pending" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6">
              <TabsTrigger value="pending">
                {language === "zh" ? "待评审" : "Pending"} ({pendingTasks.length})
              </TabsTrigger>
              <TabsTrigger value="scored">
                {language === "zh" ? "已评审" : "Scored"} ({scoredTasks.length})
              </TabsTrigger>
              <TabsTrigger value="waiting">
                {language === "zh" ? "等待中" : "Waiting"} ({waitingTasks.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="pending">
              {pendingTasks.length > 0 ? (
                pendingTasks.map(task => renderTaskCard(task, true))
              ) : (
                <Card>
                  <CardContent className="py-12 text-center text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                    <p>{language === "zh" ? "暂无待评审的论文" : "No pending reviews"}</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="scored">
              {scoredTasks.length > 0 ? (
                scoredTasks.map(task => renderTaskCard(task, false))
              ) : (
                <Card>
                  <CardContent className="py-12 text-center text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>{language === "zh" ? "暂无已评审的论文" : "No scored reviews"}</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="waiting">
              {waitingTasks.length > 0 ? (
                <>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                    <p className="text-sm text-yellow-800">
                      {language === "zh" 
                        ? "以下论文正在等待第一导师评分，第一导师评分后您才能进行评审。" 
                        : "The following theses are waiting for first supervisor scores. You can review after the first supervisor scores."}
                    </p>
                  </div>
                  {waitingTasks.map(task => renderTaskCard(task, false))}
                </>
              ) : (
                <Card>
                  <CardContent className="py-12 text-center text-gray-500">
                    <Clock className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>{language === "zh" ? "暂无等待中的论文" : "No waiting reviews"}</p>
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
      </main>

      {/* 评分对话框 */}
      <Dialog open={scoreDialogOpen} onOpenChange={setScoreDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "提交评分" : "Submit Score"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `为 ${selectedTask?.studentName} 的论文评分` 
                : `Score the thesis of ${selectedTask?.studentName}`}
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
                <span className="font-medium">{language === "zh" ? "第一导师评分" : "First Score"}:</span> {selectedTask?.firstTeacherScore}
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

            {/* 警告提示 */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                <AlertCircle className="w-4 h-4 inline mr-1" />
                {language === "zh" 
                  ? "评分提交后不可更改，如需修改请联系管理员。" 
                  : "Score cannot be changed after submission. Contact admin if modification is needed."}
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
              <p className="text-sm text-gray-600 mb-2">{language === "zh" ? "您的评分" : "Your Score"}</p>
              <p className="text-3xl font-bold text-blue-600">{scoreInput}</p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDialogOpen(false)}>
              {language === "zh" ? "返回修改" : "Go Back"}
            </Button>
            <Button 
              onClick={handleSubmitScore}
              disabled={submitScoreMutation.isPending}
            >
              {submitScoreMutation.isPending 
                ? (language === "zh" ? "提交中..." : "Submitting...") 
                : (language === "zh" ? "确认提交" : "Confirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
