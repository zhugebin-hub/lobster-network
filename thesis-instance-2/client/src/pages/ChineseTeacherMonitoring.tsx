import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { trpc } from "@/lib/trpc";
import { ArrowLeft, BookOpen, Users, AlertTriangle, CheckCircle, Clock, FileText, RefreshCw, XCircle } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { useState } from "react";
import { useLocation } from "wouter";

export default function ChineseTeacherMonitoring() {
  const { user, loading: authLoading } = useAuth();
  const [, setLocation] = useLocation();
  const [topicFilter, setTopicFilter] = useState<"all" | "used" | "unused">("all");
  const [showBatchRejectDialog, setShowBatchRejectDialog] = useState(false);

  // 获取监控统计数据
  const { data: monitoringData, isLoading: monitoringLoading, refetch: refetchMonitoring } = trpc.admin.getChineseTeacherTopicMonitoring.useQuery();

  // 获取课题列表
  const { data: topicList, isLoading: topicListLoading, refetch: refetchTopicList } = trpc.admin.getChineseTeacherTopicList.useQuery({ status: topicFilter });

  // 获取待确认分流学生列表
  const { data: pendingStudents, isLoading: pendingStudentsLoading, refetch: refetchPendingStudents } = trpc.admin.getPendingTransferStudentsList.useQuery();
  
  // 检查是否处于分流优先模式
  const { data: priorityModeData } = trpc.match.checkTransferPriorityMode.useQuery();
  const isTransferPriorityMode = priorityModeData?.isActive || false;
  
  // 批量拒绝非分流学生志愿
  const batchRejectMutation = trpc.admin.batchRejectNonTransferStudentWishes.useMutation({
    onSuccess: (data) => {
      if (data.success) {
        toast.success(data.message);
        handleRefresh();
      } else {
        toast.error(data.message);
      }
      setShowBatchRejectDialog(false);
    },
    onError: (error) => {
      toast.error("操作失败：" + error.message);
      setShowBatchRejectDialog(false);
    }
  });

  const handleRefresh = () => {
    refetchMonitoring();
    refetchTopicList();
    refetchPendingStudents();
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user || user.role !== "admin") {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>访问受限</CardTitle>
            <CardDescription>您没有权限访问此页面</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setLocation("/")}>返回首页</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isLoading = monitoringLoading || topicListLoading || pendingStudentsLoading;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => setLocation("/admin")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              返回控制台
            </Button>
            <h1 className="text-xl font-semibold">中方导师课题与生源监控</h1>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-sm">
              当前学年: {monitoringData?.currentAcademicYear || "-"}
            </Badge>
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              刷新数据
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 已发布课题总数 */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">已发布课题总数</CardTitle>
              <BookOpen className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {monitoringLoading ? "-" : monitoringData?.publishedTopicsCount || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">当前学年中方导师已发布的课题</p>
            </CardContent>
          </Card>

          {/* 已使用课题数 */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">已使用课题数</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {monitoringLoading ? "-" : monitoringData?.usedTopicsCount || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">已被学生选定且导师确认</p>
            </CardContent>
          </Card>

          {/* 未使用课题数 - 核心预警指标 */}
          <Card className={monitoringData && monitoringData.unusedTopicsCount > 0 ? "border-amber-300 bg-amber-50" : ""}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">未使用课题数</CardTitle>
              <AlertTriangle className={`h-4 w-4 ${monitoringData && monitoringData.unusedTopicsCount > 0 ? "text-amber-500" : "text-gray-400"}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${monitoringData && monitoringData.unusedTopicsCount > 0 ? "text-amber-600" : "text-gray-600"}`}>
                {monitoringLoading ? "-" : monitoringData?.unusedTopicsCount || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">已发布但尚未被确认的课题</p>
              {monitoringData && monitoringData.unusedTopicsCount > 0 && (
                <Badge variant="outline" className="mt-2 text-amber-600 border-amber-300">
                  需关注
                </Badge>
              )}
            </CardContent>
          </Card>

          {/* 待确认分流学生数 */}
          <Card className={monitoringData && monitoringData.pendingTransferStudentsCount > 0 ? "border-red-300 bg-red-50" : ""}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">待确认分流学生</CardTitle>
              <Users className={`h-4 w-4 ${monitoringData && monitoringData.pendingTransferStudentsCount > 0 ? "text-red-500" : "text-gray-400"}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${monitoringData && monitoringData.pendingTransferStudentsCount > 0 ? "text-red-600" : "text-gray-600"}`}>
                {monitoringLoading ? "-" : monitoringData?.pendingTransferStudentsCount || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">尚未被任何导师确认志愿</p>
              {monitoringData && monitoringData.pendingTransferStudentsCount > 0 && (
                <Badge variant="outline" className="mt-2 text-red-600 border-red-300">
                  紧急
                </Badge>
              )}
            </CardContent>
          </Card>
        </div>

        {/* 分流优先模式操作区 */}
        {isTransferPriorityMode && (
          <Card className="border-red-300 bg-red-50">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <CardTitle className="text-red-800">分流学生优先模式已启动</CardTitle>
                </div>
                <Button 
                  variant="destructive" 
                  size="sm"
                  onClick={() => setShowBatchRejectDialog(true)}
                  disabled={batchRejectMutation.isPending}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  批量拒绝非分流学生
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-red-700">
                当前未使用课题数（{priorityModeData?.unusedTopicsCount || 0}）小于等于待确认分流学生数（{priorityModeData?.pendingTransferStudentsCount || 0}）。
                点击“批量拒绝非分流学生”按钮可以一键拒绝所有中方导师待审核的非分流学生志愿。
              </p>
            </CardContent>
          </Card>
        )}

        {/* 详细数据表格 */}
        <Tabs defaultValue="topics" className="space-y-4">
          <TabsList>
            <TabsTrigger value="topics" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              课题列表
            </TabsTrigger>
            <TabsTrigger value="students" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              待确认学生
              {monitoringData && monitoringData.pendingTransferStudentsCount > 0 && (
                <Badge variant="destructive" className="ml-1 h-5 w-5 p-0 flex items-center justify-center text-xs">
                  {monitoringData.pendingTransferStudentsCount}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {/* 课题列表 */}
          <TabsContent value="topics">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>中方导师课题列表</CardTitle>
                    <CardDescription>当前学年所有中方导师已发布的课题及其使用状态</CardDescription>
                  </div>
                  <Select value={topicFilter} onValueChange={(value: "all" | "used" | "unused") => setTopicFilter(value)}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="筛选状态" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">全部课题</SelectItem>
                      <SelectItem value="used">已使用</SelectItem>
                      <SelectItem value="unused">未使用</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                {topicListLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  </div>
                ) : topicList && topicList.length > 0 ? (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>课题标题</TableHead>
                          <TableHead>导师</TableHead>
                          <TableHead>状态</TableHead>
                          <TableHead>匹配学生</TableHead>
                          <TableHead>创建时间</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {topicList.map((topic) => (
                          <TableRow key={topic.id}>
                            <TableCell>
                              <div className="max-w-xs">
                                <div className="font-medium truncate" title={topic.titleEn || topic.title}>
                                  {topic.titleEn || topic.title}
                                </div>
                                {topic.title && topic.titleEn && (
                                  <div className="text-xs text-muted-foreground truncate" title={topic.title}>
                                    {topic.title}
                                  </div>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div>
                                <div className="font-medium">{topic.teacherName}</div>
                                <div className="text-xs text-muted-foreground">{topic.teacherEmail}</div>
                              </div>
                            </TableCell>
                            <TableCell>
                              {topic.isUsed ? (
                                <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  已使用
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="text-amber-600 border-amber-300">
                                  <Clock className="h-3 w-3 mr-1" />
                                  未使用
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              {topic.matchedStudentName ? (
                                <div>
                                  <div className="font-medium">{topic.matchedStudentName}</div>
                                  <div className="text-xs text-muted-foreground">{topic.matchedStudentId}</div>
                                </div>
                              ) : (
                                <span className="text-muted-foreground">-</span>
                              )}
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                              {new Date(topic.createdAt).toLocaleDateString("zh-CN")}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    暂无课题数据
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 待确认学生列表 */}
          <TabsContent value="students">
            <Card>
              <CardHeader>
                <CardTitle>待确认分流学生列表</CardTitle>
                <CardDescription>所有尚未被任何导师确认志愿的分流学生</CardDescription>
              </CardHeader>
              <CardContent>
                {pendingStudentsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  </div>
                ) : pendingStudents && pendingStudents.length > 0 ? (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>学生姓名</TableHead>
                          <TableHead>学号</TableHead>
                          <TableHead>班级</TableHead>
                          <TableHead>专业</TableHead>
                          <TableHead>已提交志愿数</TableHead>
                          <TableHead>最新志愿状态</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {pendingStudents.map((student) => (
                          <TableRow key={student.id}>
                            <TableCell>
                              <div>
                                <div className="font-medium">{student.name}</div>
                                <div className="text-xs text-muted-foreground">{student.email}</div>
                              </div>
                            </TableCell>
                            <TableCell>{student.studentId || "-"}</TableCell>
                            <TableCell>{student.studentClass || "-"}</TableCell>
                            <TableCell>
                              {student.studentMajor === "electronic_info" ? "电子信息" : 
                               student.studentMajor === "communication" ? "通信工程" : "-"}
                            </TableCell>
                            <TableCell>
                              <Badge variant={student.wishCount > 0 ? "default" : "destructive"}>
                                {student.wishCount}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {student.latestWishStatus ? (
                                <Badge variant="outline" className={
                                  student.latestWishStatus === "pending" ? "text-blue-600 border-blue-300" :
                                  student.latestWishStatus === "selected" ? "text-green-600 border-green-300" :
                                  student.latestWishStatus === "rejected" ? "text-red-600 border-red-300" :
                                  "text-gray-600 border-gray-300"
                                }>
                                  {student.latestWishStatus === "pending" ? "待审核" :
                                   student.latestWishStatus === "selected" ? "已选中" :
                                   student.latestWishStatus === "rejected" ? "已拒绝" :
                                   student.latestWishStatus === "matched" ? "已匹配" :
                                   student.latestWishStatus}
                                </Badge>
                              ) : (
                                <span className="text-muted-foreground">未提交志愿</span>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-green-600">
                    <CheckCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>所有分流学生都已被确认</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* 批量拒绝确认对话框 */}
      <Dialog open={showBatchRejectDialog} onOpenChange={setShowBatchRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-red-600 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              确认批量拒绝操作
            </DialogTitle>
            <DialogDescription className="text-left">
              <p className="mb-3">此操作将会：</p>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>拒绝所有中方导师课题下的非分流学生待审核志愿</li>
                <li>被拒绝的学生将进入下一志愿的审核队列</li>
                <li>此操作不可撤销</li>
              </ul>
              <p className="mt-3 font-medium text-red-600">确定要执行此操作吗？</p>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBatchRejectDialog(false)}>
              取消
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => batchRejectMutation.mutate()}
              disabled={batchRejectMutation.isPending}
            >
              {batchRejectMutation.isPending ? "处理中..." : "确认拒绝"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
