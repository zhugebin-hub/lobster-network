import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { prefixFileUrl } from "@/lib/basePath";
import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { 
  Users, 
  Calendar, 
  FileText, 
  Paperclip, 
  Send, 
  MessageSquare,
  Download,
  Eye,
  Clock,
  CheckCircle,
  Search,
  ArrowLeft,
  Package,
  User,
  FileDown
} from "lucide-react";

export default function TeacherGuidanceLogs() {
  const { user } = useAuth();
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [newComment, setNewComment] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  
  const utils = trpc.useUtils();
  
  // 获取学生列表
  const { data: students, isLoading: isLoadingStudents } = trpc.guidance.getStudents.useQuery({});
  
  // 获取选中学生的指导记录
  const { data: studentLogs, isLoading: isLoadingLogs } = trpc.guidance.getStudentLogs.useQuery(
    { studentId: selectedStudentId! },
    { enabled: !!selectedStudentId }
  );
  
  // 获取记录详情
  const { data: logDetail, isLoading: isLoadingDetail } = trpc.guidance.getLogDetail.useQuery(
    { logId: selectedLogId! },
    { enabled: !!selectedLogId }
  );
  
  // 获取学生所有附件（用于批量下载）
  const { data: studentAttachments } = trpc.guidance.getStudentAttachments.useQuery(
    { studentId: selectedStudentId! },
    { enabled: !!selectedStudentId }
  );
  
  // 确认记录
  const confirmLogMutation = trpc.guidance.confirmLog.useMutation({
    onSuccess: () => {
      toast.success("记录已确认");
      if (selectedStudentId) {
        utils.guidance.getStudentLogs.invalidate({ studentId: selectedStudentId });
      }
      if (selectedLogId) {
        utils.guidance.getLogDetail.invalidate({ logId: selectedLogId });
      }
    },
    onError: (error) => {
      toast.error(error.message || "确认失败");
    },
  });
  
  // 添加评论
  const addCommentMutation = trpc.guidance.addComment.useMutation({
    onSuccess: () => {
      toast.success("评论已添加");
      setNewComment("");
      if (selectedLogId) {
        utils.guidance.getLogDetail.invalidate({ logId: selectedLogId });
      }
    },
    onError: (error) => {
      toast.error(error.message || "评论失败");
    },
  });
  
  const openDetailDialog = (logId: number) => {
    setSelectedLogId(logId);
    setIsDetailDialogOpen(true);
  };
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "draft":
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />草稿</Badge>;
      case "submitted":
        return <Badge variant="outline" className="text-blue-600 border-blue-600"><Send className="w-3 h-3 mr-1" />待确认</Badge>;
      case "confirmed":
        return <Badge variant="default" className="bg-green-600"><CheckCircle className="w-3 h-3 mr-1" />已确认</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };
  
  const formatDate = (date: Date | string) => {
    return new Date(date).toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };
  
  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return "未知大小";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };
  
  // 过滤学生列表
  const filteredStudents = students?.filter(student => 
    (student.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.studentId?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.email.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // 批量下载ZIP压缩包
  const handleBatchDownload = () => {
    if (!selectedStudentId) return;
    if (!studentAttachments || studentAttachments.length === 0) {
      toast.error("该学生没有上传任何附件");
      return;
    }
    
    toast.info("正在生成ZIP压缩包，请稍候...");
    
    // 使用ZIP下载API
    const link = document.createElement("a");
    link.href = `/api/guidance/download-attachments/${selectedStudentId}`;
    link.download = "attachments.zip";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  // 导出PDF
  const exportPdfMutation = trpc.guidance.exportStudentLogsPdf.useMutation({
    onSuccess: (data) => {
      // 将 base64 转换为 Blob 并下载
      const byteCharacters = atob(data.base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast.success("PDF导出成功");
    },
    onError: (error) => {
      toast.error(error.message || "PDF导出失败");
    },
  });

  const handleExportPdf = () => {
    if (!selectedStudentId) return;
    toast.info("正在生成PDF文件，请稍候...");
    exportPdfMutation.mutate({ studentId: selectedStudentId });
  };

  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/teacher")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold">
            {selectedStudentId ? "学生指导记录" : "指导记录管理"}
          </h1>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {selectedStudentId && (
              <Button variant="ghost" size="sm" onClick={() => setSelectedStudentId(null)}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                返回学生列表
              </Button>
            )}
            <div>
              <p className="text-muted-foreground">
                {selectedStudentId 
                  ? `查看和管理学生的指导记录`
                  : "查看所指导学生的指导记录"
                }
              </p>
            </div>
          </div>
          {selectedStudentId && (
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={handleExportPdf} disabled={exportPdfMutation.isPending}>
                <FileDown className="w-4 h-4 mr-2" />
                {exportPdfMutation.isPending ? "生成中..." : "导出PDF"}
              </Button>
              {studentAttachments && studentAttachments.length > 0 && (
                <Button variant="outline" onClick={handleBatchDownload}>
                  <Package className="w-4 h-4 mr-2" />
                  下载附件ZIP ({studentAttachments.length})
                </Button>
              )}
            </div>
          )}
        </div>
        
        {!selectedStudentId ? (
          // 学生列表视图
          <>
            {/* 搜索栏 */}
            <div className="flex items-center gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="搜索学生姓名、学号或邮箱..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            {/* 统计卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">指导学生数</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{students?.length || 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">待确认记录</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">
                    {students?.reduce((sum, s) => sum + s.submittedLogs, 0) || 0}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">已确认记录</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {students?.reduce((sum, s) => sum + s.confirmedLogs, 0) || 0}
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* 学生列表 */}
            <Card>
              <CardHeader>
                <CardTitle>学生列表</CardTitle>
                <CardDescription>点击学生查看其指导记录</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoadingStudents ? (
                  <div className="text-center py-8 text-muted-foreground">加载中...</div>
                ) : !filteredStudents || filteredStudents.length === 0 ? (
                  <div className="text-center py-12">
                    <Users className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">暂无指导学生</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredStudents.map((student) => (
                      <Card
                        key={student.id}
                        className="cursor-pointer hover:border-primary transition-colors"
                        onClick={() => setSelectedStudentId(student.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                              <User className="w-5 h-5 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-semibold truncate">{student.name}</h3>
                              <p className="text-sm text-muted-foreground truncate">{student.studentId}</p>
                              <div className="flex items-center gap-2 mt-2">
                                <Badge variant="outline" className="text-xs">
                                  总计 {student.totalLogs}
                                </Badge>
                                {student.submittedLogs > 0 && (
                                  <Badge variant="secondary" className="text-xs text-orange-600">
                                    待确认 {student.submittedLogs}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          // 学生指导记录视图
          <>
            {/* 学生信息卡片 */}
            {students?.find(s => s.id === selectedStudentId) && (
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold">
                        {students.find(s => s.id === selectedStudentId)?.name}
                      </h2>
                      <p className="text-sm text-muted-foreground">
                        {students.find(s => s.id === selectedStudentId)?.studentId} · 
                        {students.find(s => s.id === selectedStudentId)?.email}
                      </p>
                    </div>
                    <div className="ml-auto flex items-center gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold">
                          {students.find(s => s.id === selectedStudentId)?.totalLogs || 0}
                        </div>
                        <div className="text-xs text-muted-foreground">总记录</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {students.find(s => s.id === selectedStudentId)?.submittedLogs || 0}
                        </div>
                        <div className="text-xs text-muted-foreground">待确认</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {students.find(s => s.id === selectedStudentId)?.confirmedLogs || 0}
                        </div>
                        <div className="text-xs text-muted-foreground">已确认</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {/* 记录列表 */}
            <Card>
              <CardHeader>
                <CardTitle>指导记录时间线</CardTitle>
                <CardDescription>按时间倒序显示学生的指导记录</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoadingLogs ? (
                  <div className="text-center py-8 text-muted-foreground">加载中...</div>
                ) : !studentLogs || studentLogs.length === 0 ? (
                  <div className="text-center py-12">
                    <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">该学生暂无指导记录</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {studentLogs.map((log) => (
                      <div
                        key={log.id}
                        className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex-shrink-0 w-16 text-center">
                          <div className="text-2xl font-bold">{new Date(log.guidanceDate).getDate()}</div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(log.guidanceDate).toLocaleDateString("zh-CN", { month: "short" })}
                          </div>
                        </div>
                        <Separator orientation="vertical" className="h-auto self-stretch" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold truncate">{log.topic}</h3>
                            {getStatusBadge(log.status)}
                            {(log.attachments?.length || 0) > 0 && (
                              <Badge variant="outline" className="text-xs">
                                <Paperclip className="w-3 h-3 mr-1" />
                                {log.attachments?.length || 0}
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2">{log.content}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm" onClick={() => openDetailDialog(log.id)}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          {log.status === "submitted" && (
                            <Button
                              size="sm"
                              onClick={() => confirmLogMutation.mutate({ logId: log.id })}
                              disabled={confirmLogMutation.isPending}
                            >
                              <CheckCircle className="w-4 h-4 mr-2" />
                              确认
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
        
        {/* 详情对话框 */}
        <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
          <DialogContent className="max-w-3xl max-h-[90vh]">
            <DialogHeader>
              <DialogTitle>指导记录详情</DialogTitle>
            </DialogHeader>
            {isLoadingDetail ? (
              <div className="text-center py-8">加载中...</div>
            ) : logDetail ? (
              <ScrollArea className="max-h-[70vh]">
                <div className="space-y-6 pr-4">
                  {/* 基本信息 */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {formatDate(logDetail.guidanceDate)}
                      </span>
                      {getStatusBadge(logDetail.status)}
                    </div>
                    <h2 className="text-xl font-semibold mb-2">{logDetail.topic}</h2>
                    <div className="prose prose-sm max-w-none">
                      <p className="whitespace-pre-wrap">{logDetail.content}</p>
                    </div>
                  </div>
                  
                  {/* 确认按钮 */}
                  {logDetail.status === "submitted" && (
                    <div className="flex justify-end">
                      <Button
                        onClick={() => confirmLogMutation.mutate({ logId: logDetail.id })}
                        disabled={confirmLogMutation.isPending}
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        确认此记录
                      </Button>
                    </div>
                  )}
                  
                  <Separator />
                  
                  {/* 附件区域 */}
                  <div>
                    <h3 className="font-semibold flex items-center gap-2 mb-3">
                      <Paperclip className="w-4 h-4" />
                      附件 ({logDetail.attachments?.length || 0})
                    </h3>
                    {logDetail.attachments && logDetail.attachments.length > 0 ? (
                      <div className="space-y-2">
                        {logDetail.attachments.map((attachment) => (
                          <div
                            key={attachment.id}
                            className="flex items-center justify-between p-3 bg-muted rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <FileText className="w-5 h-5 text-muted-foreground" />
                              <div>
                                <p className="text-sm font-medium">{attachment.fileName}</p>
                                <p className="text-xs text-muted-foreground">
                                  {formatFileSize(attachment.fileSize)}
                                </p>
                              </div>
                            </div>
                            <Button variant="ghost" size="sm" asChild>
                              <a href={prefixFileUrl(attachment.fileUrl)} target="_blank" rel="noopener noreferrer">
                                <Download className="w-4 h-4" />
                              </a>
                            </Button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">暂无附件</p>
                    )}
                  </div>
                  
                  <Separator />
                  
                  {/* 评论区域 */}
                  <div>
                    <h3 className="font-semibold flex items-center gap-2 mb-3">
                      <MessageSquare className="w-4 h-4" />
                      评论与反馈 ({logDetail.comments?.length || 0})
                    </h3>
                    {logDetail.comments && logDetail.comments.length > 0 ? (
                      <div className="space-y-3 mb-4">
                        {logDetail.comments.map((comment) => (
                          <div key={comment.id} className="p-3 bg-muted rounded-lg">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-sm">{comment.userName}</span>
                              <Badge variant="outline" className="text-xs">
                                {comment.userRole === "teacher" ? "导师" : "学生"}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {formatDate(comment.createdAt)}
                              </span>
                            </div>
                            <p className="text-sm">{comment.content}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground mb-4">暂无评论</p>
                    )}
                    
                    {/* 添加评论 */}
                    <div className="flex gap-2">
                      <Textarea
                        placeholder="添加评论或反馈..."
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        className="min-h-[80px]"
                      />
                    </div>
                    <div className="flex justify-end mt-2">
                      <Button
                        size="sm"
                        onClick={() => {
                          if (selectedLogId && newComment.trim()) {
                            addCommentMutation.mutate({
                              logId: selectedLogId,
                              content: newComment.trim(),
                            });
                          }
                        }}
                        disabled={!newComment.trim() || addCommentMutation.isPending}
                      >
                        <Send className="w-4 h-4 mr-2" />
                        发送
                      </Button>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center py-8 text-muted-foreground">记录不存在</div>
            )}
          </DialogContent>
        </Dialog>
      </div>
      </main>
    </div>
  );
}
