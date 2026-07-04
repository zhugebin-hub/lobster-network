import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ArrowLeft, Download, Search, AlertTriangle, CheckCircle, Clock, FileText, MessageSquare, Trash2 } from "lucide-react";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import { Link } from "wouter";

export default function AdminScoreStatistics() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [selectedComment, setSelectedComment] = useState<{
    studentName: string;
    firstComment: string | null;
    secondComment: string | null;
  } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<{
    id: number;
    studentName: string;
    topicTitle: string;
  } | null>(null);
  const [deleteConfirmStep, setDeleteConfirmStep] = useState(0);

  const { data: academicYearsData } = trpc.admin.getAllYears.useQuery();
  const academicYears = academicYearsData || [];
  const [selectedYear, setSelectedYear] = useState<string>("__current__");
  
  const utils = trpc.useUtils();
  const { data, isLoading } = trpc.secondTeacher.getScoreStatistics.useQuery(
    selectedYear && selectedYear !== "__current__" ? { academicYear: selectedYear } : undefined
  );

  const deleteRecordMutation = trpc.secondTeacher.deleteScoreRecord.useMutation({
    onSuccess: () => {
      toast.success("记录已删除");
      utils.secondTeacher.getScoreStatistics.invalidate();
      setDeleteTarget(null);
      setDeleteConfirmStep(0);
    },
    onError: (error: { message?: string }) => {
      toast.error(error.message || "删除失败");
    },
  });

  const handleDeleteClick = (item: { id: number; studentName: string; topicTitle: string }) => {
    setDeleteTarget(item);
    setDeleteConfirmStep(1);
  };

  const handleDeleteConfirm = () => {
    if (deleteConfirmStep === 1) {
      setDeleteConfirmStep(2);
    } else if (deleteConfirmStep === 2 && deleteTarget) {
      deleteRecordMutation.mutate({
        draftId: deleteTarget.id,
        confirmDelete: true,
      });
    }
  };

  const handleDeleteCancel = () => {
    setDeleteTarget(null);
    setDeleteConfirmStep(0);
  };

  const statistics = data?.statistics || [];
  const overview = data?.overview || {
    totalDrafts: 0,
    scoredByFirst: 0,
    scoredBySecond: 0,
    bothScored: 0,
    finalScoreConfirmed: 0,
    avgFirstScore: null,
    avgSecondScore: null,
    avgFinalScore: null,
    avgScoreDifference: null,
    largeDifferenceCount: 0,
  };

  // 筛选数据
  const filteredStatistics = statistics.filter(item => {
    const matchesSearch = 
      item.studentName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.chineseStudentId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.englishStudentId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.topicTitle?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.teacherName?.toLowerCase().includes(searchTerm.toLowerCase());

    let matchesFilter = true;
    if (filterStatus === "both_scored") {
      matchesFilter = item.firstScore !== null && item.secondScore !== null;
    } else if (filterStatus === "first_only") {
      matchesFilter = item.firstScore !== null && item.secondScore === null;
    } else if (filterStatus === "second_only") {
      matchesFilter = item.firstScore === null && item.secondScore !== null;
    } else if (filterStatus === "not_scored") {
      matchesFilter = item.firstScore === null && item.secondScore === null;
    } else if (filterStatus === "large_diff") {
      matchesFilter = item.scoreDifference !== null && item.scoreDifference > 10;
    } else if (filterStatus === "final_confirmed") {
      matchesFilter = item.finalScore !== null;
    } else if (filterStatus === "final_pending") {
      matchesFilter = item.firstScore !== null && item.secondScore !== null && item.finalScore === null;
    }

    return matchesSearch && matchesFilter;
  });

  // 导出CSV
  const handleExport = () => {
    const headers = ["学生姓名", "中方学号", "英方学号", "论文题目", "第一导师", "第二导师", "第一导师评分", "第二导师评分", "最终成绩", "分数差异", "第一导师评语", "第二导师评语", "提交时间"];
    const rows = filteredStatistics.map(item => [
      item.studentName,
      item.chineseStudentId,
      item.englishStudentId,
      item.topicTitle,
      item.teacherName,
      item.secondTeacherName || "-",
      item.firstScore?.toString() ?? "-",
      item.secondScore?.toString() ?? "-",
      item.finalScore?.toString() ?? "-",
      item.scoreDifference?.toString() ?? "-",
      item.firstTeacherComment || "-",
      item.secondTeacherComment || "-",
      item.submittedAt ? new Date(item.submittedAt).toLocaleString("zh-CN") : "-",
    ]);

    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(","))
      .join("\n");

    const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `评分统计_${selectedYear || "全部"}_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getScoreStatusBadge = (firstScore: number | null, secondScore: number | null, finalScore: number | null) => {
    if (finalScore !== null) {
      return <Badge className="bg-indigo-100 text-indigo-800">已确定</Badge>;
    } else if (firstScore !== null && secondScore !== null) {
      return <Badge className="bg-green-100 text-green-800">双方已评</Badge>;
    } else if (firstScore !== null) {
      return <Badge className="bg-blue-100 text-blue-800">仅第一导师</Badge>;
    } else if (secondScore !== null) {
      return <Badge className="bg-purple-100 text-purple-800">仅第二导师</Badge>;
    } else {
      return <Badge variant="secondary">未评分</Badge>;
    }
  };

  const getDifferenceColor = (diff: number | null) => {
    if (diff === null) return "text-gray-400";
    if (diff <= 5) return "text-green-600";
    if (diff <= 10) return "text-yellow-600";
    return "text-red-600 font-semibold";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container py-8">
        {/* 返回按钮 */}
        <Link href="/admin">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回管理控制台
          </Button>
        </Link>

        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">评分统计</h1>
          <p className="text-gray-600 mt-2">查看所有论文的双导师评分情况和分数差异</p>
        </div>

        {/* 统计概览 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>论文总数</CardDescription>
              <CardTitle className="text-2xl">{overview.totalDrafts}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>第一导师已评</CardDescription>
              <CardTitle className="text-2xl text-blue-600">{overview.scoredByFirst}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>第二导师已评</CardDescription>
              <CardTitle className="text-2xl text-purple-600">{overview.scoredBySecond}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>双方都已评</CardDescription>
              <CardTitle className="text-2xl text-green-600">{overview.bothScored}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-indigo-200 bg-indigo-50">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-indigo-500" />
                最终成绩已确定
              </CardDescription>
              <CardTitle className="text-2xl text-indigo-700">{overview.finalScoreConfirmed}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* 评分统计 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>第一导师平均分</CardDescription>
              <CardTitle className="text-xl">
                {overview.avgFirstScore !== null ? overview.avgFirstScore.toFixed(1) : "-"}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>第二导师平均分</CardDescription>
              <CardTitle className="text-xl">
                {overview.avgSecondScore !== null ? overview.avgSecondScore.toFixed(1) : "-"}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-indigo-200 bg-indigo-50">
            <CardHeader className="pb-2">
              <CardDescription>最终成绩平均分</CardDescription>
              <CardTitle className="text-xl text-indigo-700">
                {overview.avgFinalScore !== null ? overview.avgFinalScore.toFixed(1) : "-"}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>平均分数差异</CardDescription>
              <CardTitle className="text-xl">
                {overview.avgScoreDifference !== null ? overview.avgScoreDifference.toFixed(1) : "-"}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card className={overview.largeDifferenceCount > 0 ? "border-red-200 bg-red-50" : ""}>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                {overview.largeDifferenceCount > 0 && <AlertTriangle className="h-4 w-4 text-red-500" />}
                差异&gt;10分
              </CardDescription>
              <CardTitle className={`text-xl ${overview.largeDifferenceCount > 0 ? "text-red-600" : ""}`}>
                {overview.largeDifferenceCount}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* 筛选和搜索 */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="搜索学生姓名、学号、题目、导师..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={selectedYear} onValueChange={setSelectedYear}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="选择学年" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__current__">当前学年</SelectItem>
                  {academicYears.map((year: { id: number; yearName: string; displayName: string | null }) => (
                    <SelectItem key={year.id} value={year.yearName}>
                      {year.displayName || year.yearName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="筛选状态" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="both_scored">双方已评</SelectItem>
                  <SelectItem value="first_only">仅第一导师</SelectItem>
                  <SelectItem value="second_only">仅第二导师</SelectItem>
                  <SelectItem value="not_scored">未评分</SelectItem>
                  <SelectItem value="large_diff">差异&gt;10分</SelectItem>
                  <SelectItem value="final_confirmed">最终成绩已确定</SelectItem>
                  <SelectItem value="final_pending">待确定最终成绩</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleExport} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                导出CSV
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 数据表格 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              评分详情
            </CardTitle>
            <CardDescription>
              共 {filteredStatistics.length} 条记录
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-gray-500">加载中...</div>
            ) : filteredStatistics.length === 0 ? (
              <div className="text-center py-8 text-gray-500">暂无数据</div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>学生</TableHead>
                      <TableHead>论文题目</TableHead>
                      <TableHead>第一导师</TableHead>
                      <TableHead>第二导师</TableHead>
                      <TableHead className="text-center">第一导师评分</TableHead>
                      <TableHead className="text-center">第二导师评分</TableHead>
                      <TableHead className="text-center">最终成绩</TableHead>
                      <TableHead className="text-center">分数差异</TableHead>
                      <TableHead className="text-center">状态</TableHead>
                      <TableHead className="text-center">评语</TableHead>
                      <TableHead className="text-center">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredStatistics.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{item.studentName}</div>
                            <div className="text-xs text-gray-500">
                              {item.chineseStudentId && <span>{item.chineseStudentId}</span>}
                              {item.chineseStudentId && item.englishStudentId && <span> / </span>}
                              {item.englishStudentId && <span>{item.englishStudentId}</span>}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="max-w-[200px] truncate" title={item.topicTitle}>
                            {item.topicTitle}
                          </div>
                        </TableCell>
                        <TableCell>{item.teacherName}</TableCell>
                        <TableCell>{item.secondTeacherName || "-"}</TableCell>
                        <TableCell className="text-center">
                          {item.firstScore !== null ? (
                            <span className="font-medium">{item.firstScore}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          {item.secondScore !== null ? (
                            <span className="font-medium">{item.secondScore}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          {item.finalScore !== null ? (
                            <span className="font-bold text-indigo-700">{item.finalScore}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell className={`text-center ${getDifferenceColor(item.scoreDifference)}`}>
                          {item.scoreDifference !== null ? (
                            <span className="flex items-center justify-center gap-1">
                              {item.scoreDifference > 10 && <AlertTriangle className="h-4 w-4" />}
                              {item.scoreDifference}
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          {getScoreStatusBadge(item.firstScore, item.secondScore, item.finalScore)}
                        </TableCell>
                        <TableCell className="text-center">
                          {(item.firstTeacherComment || item.secondTeacherComment) ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedComment({
                                studentName: item.studentName,
                                firstComment: item.firstTeacherComment,
                                secondComment: item.secondTeacherComment,
                              })}
                            >
                              <MessageSquare className="h-4 w-4" />
                            </Button>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick({
                              id: item.id,
                              studentName: item.studentName,
                              topicTitle: item.topicTitle,
                            })}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 评语查看对话框 */}
        <Dialog open={!!selectedComment} onOpenChange={() => setSelectedComment(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>评审评语 - {selectedComment?.studentName}</DialogTitle>
              <DialogDescription>查看导师的评审意见</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-sm text-gray-700 mb-2">第一导师评语</h4>
                <div className="bg-gray-50 rounded-lg p-4 min-h-[100px]">
                  {selectedComment?.firstComment || <span className="text-gray-400">暂无评语</span>}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-sm text-gray-700 mb-2">第二导师评语</h4>
                <div className="bg-gray-50 rounded-lg p-4 min-h-[100px]">
                  {selectedComment?.secondComment || <span className="text-gray-400">暂无评语</span>}
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* 删除确认对话框 - 第一步 */}
        <AlertDialog open={deleteConfirmStep === 1} onOpenChange={(open) => !open && handleDeleteCancel()}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
                警告：删除评分记录
              </AlertDialogTitle>
              <AlertDialogDescription className="space-y-3">
                <p>您即将删除以下评分记录：</p>
                <div className="bg-gray-100 p-3 rounded-lg">
                  <p><strong>学生：</strong>{deleteTarget?.studentName}</p>
                  <p><strong>论文题目：</strong>{deleteTarget?.topicTitle}</p>
                </div>
                <p className="text-red-600 font-medium">
                  此操作将永久删除该记录，包括所有评分和评语信息。
                </p>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={handleDeleteCancel}>取消</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteConfirm}
                className="bg-red-600 hover:bg-red-700"
              >
                我已知晓，继续
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* 删除确认对话框 - 第二步（最终确认） */}
        <AlertDialog open={deleteConfirmStep === 2} onOpenChange={(open) => !open && handleDeleteCancel()}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-6 w-6" />
                最终确认
              </AlertDialogTitle>
              <AlertDialogDescription className="space-y-4">
                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <p className="text-red-800 font-bold text-lg mb-2">❗ 严重警告</p>
                  <ul className="text-red-700 space-y-2 list-disc list-inside">
                    <li>一旦删除就<strong>无法恢复</strong></li>
                    <li>所有评分、评语、历史记录将永久丢失</li>
                    <li>可能影响学生成绩和毕业资格</li>
                    <li>请确保您有充分的理由执行此操作</li>
                  </ul>
                </div>
                <p className="text-gray-700">
                  如果您确定要删除该记录，请点击“确认删除”按钮。
                </p>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={handleDeleteCancel}>取消</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteConfirm}
                className="bg-red-600 hover:bg-red-700"
                disabled={deleteRecordMutation.isPending}
              >
                {deleteRecordMutation.isPending ? "删除中..." : "确认删除"}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
