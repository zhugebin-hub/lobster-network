import { useState, useRef } from "react";
import { trpc } from "@/lib/trpc";
import { prefixPath, prefixFileUrl } from "@/lib/basePath";
import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";

import { 
  Plus, 
  Calendar, 
  FileText, 
  Paperclip, 
  Send, 
  Edit2, 
  Trash2, 
  MessageSquare,
  Download,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  Upload,
  X,
  FileDown,
  ArrowLeft
} from "lucide-react";

export default function StudentGuidanceLogs() {
  const { user } = useAuth();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
  const [newComment, setNewComment] = useState("");
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // 表单状态
  const [formData, setFormData] = useState({
    guidanceDate: new Date().toISOString().split("T")[0],
    topic: "",
    content: "",
  });
  
  const utils = trpc.useUtils();
  
  // 获取指导记录列表
  const { data: logs, isLoading } = trpc.guidance.getMyLogs.useQuery({});
  
  // 获取记录详情
  const { data: logDetail, isLoading: isLoadingDetail } = trpc.guidance.getLogDetail.useQuery(
    { logId: selectedLogId! },
    { enabled: !!selectedLogId }
  );
  
  // 创建记录
  const createLogMutation = trpc.guidance.createLog.useMutation({
    onSuccess: () => {
      toast.success("指导记录创建成功");
      setIsCreateDialogOpen(false);
      resetForm();
      utils.guidance.getMyLogs.invalidate();
    },
    onError: (error) => {
      toast.error(error.message || "创建失败");
    },
  });
  
  // 更新记录
  const updateLogMutation = trpc.guidance.updateLog.useMutation({
    onSuccess: () => {
      toast.success("指导记录更新成功");
      setIsEditDialogOpen(false);
      resetForm();
      utils.guidance.getMyLogs.invalidate();
      if (selectedLogId) {
        utils.guidance.getLogDetail.invalidate({ logId: selectedLogId });
      }
    },
    onError: (error) => {
      toast.error(error.message || "更新失败");
    },
  });
  
  // 删除记录
  const deleteLogMutation = trpc.guidance.deleteLog.useMutation({
    onSuccess: () => {
      toast.success("指导记录已删除");
      utils.guidance.getMyLogs.invalidate();
    },
    onError: (error) => {
      toast.error(error.message || "删除失败");
    },
  });
  
  // 上传附件
  const uploadAttachmentMutation = trpc.guidance.uploadAttachment.useMutation({
    onSuccess: () => {
      toast.success("附件上传成功");
      if (selectedLogId) {
        utils.guidance.getLogDetail.invalidate({ logId: selectedLogId });
      }
    },
    onError: (error) => {
      toast.error(error.message || "上传失败");
    },
  });
  
  // 删除附件
  const deleteAttachmentMutation = trpc.guidance.deleteAttachment.useMutation({
    onSuccess: () => {
      toast.success("附件已删除");
      if (selectedLogId) {
        utils.guidance.getLogDetail.invalidate({ logId: selectedLogId });
      }
    },
    onError: (error) => {
      toast.error(error.message || "删除失败");
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

  // 导出PDF
  const exportMyPdfMutation = trpc.guidance.exportMyLogsPdf.useMutation({
    onSuccess: (data) => {
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
  
  const resetForm = () => {
    setFormData({
      guidanceDate: new Date().toISOString().split("T")[0],
      topic: "",
      content: "",
    });
  };
  
  const handleCreate = (status: "draft" | "submitted") => {
    createLogMutation.mutate({
      guidanceDate: new Date(formData.guidanceDate),
      topic: formData.topic,
      content: formData.content,
      status,
    });
  };
  
  const handleUpdate = (status?: "draft" | "submitted") => {
    if (!selectedLogId) return;
    updateLogMutation.mutate({
      logId: selectedLogId,
      guidanceDate: new Date(formData.guidanceDate),
      topic: formData.topic,
      content: formData.content,
      status,
    });
  };
  
  const handleDelete = (logId: number) => {
    if (confirm("确定要删除这条指导记录吗？")) {
      deleteLogMutation.mutate({ logId });
    }
  };
  
  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0 || !selectedLogId) return;
    
    setUploadingFiles(true);
    
    for (const file of Array.from(files)) {
      // 检查文件大小
      if (file.size > 20 * 1024 * 1024) {
        toast.error(`文件 ${file.name} 超过20MB限制`);
        continue;
      }
      
      // 检查文件类型
      const allowedTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "image/jpeg",
        "image/png",
      ];
      if (!allowedTypes.includes(file.type)) {
        toast.error(`文件 ${file.name} 类型不支持，仅支持PDF、DOCX、JPG、PNG`);
        continue;
      }
      
      try {
        // 上传到服务器
        const formData = new FormData();
        formData.append("file", file);
        
        const response = await fetch(prefixPath("/api/upload"), {
          method: "POST",
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error("文件上传失败");
        }
        
        const result = await response.json();
        
        // 保存附件记录
        await uploadAttachmentMutation.mutateAsync({
          logId: selectedLogId,
          fileName: file.name,
          fileUrl: result.url,
          fileKey: result.fileKey,
          mimeType: file.type,
          fileSize: file.size,
        });
      } catch (error) {
        toast.error(`文件 ${file.name} 上传失败`);
      }
    }
    
    setUploadingFiles(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };
  
  const openEditDialog = (log: NonNullable<typeof logs>[0]) => {
    setSelectedLogId(log.id);
    setFormData({
      guidanceDate: new Date(log.guidanceDate).toISOString().split("T")[0],
      topic: log.topic,
      content: log.content,
    });
    setIsEditDialogOpen(true);
  };
  
  const openDetailDialog = (logId: number) => {
    setSelectedLogId(logId);
    setIsDetailDialogOpen(true);
  };
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "draft":
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />草稿</Badge>;
      case "submitted":
        return <Badge variant="outline" className="text-blue-600 border-blue-600"><Send className="w-3 h-3 mr-1" />已提交</Badge>;
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

  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/student")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold">我的指导记录</h1>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-muted-foreground">记录与导师的每次指导交流</p>
          </div>
          <div className="flex items-center gap-2">
            {logs && logs.length > 0 && (
              <Button 
                variant="outline" 
                disabled={exportMyPdfMutation.isPending}
                onClick={() => {
                  if (!user?.id) return;
                  toast.info("正在生成PDF文件，请稍候...");
                  exportMyPdfMutation.mutate();
                }}
              >
                <FileDown className="w-4 h-4 mr-2" />
                {exportMyPdfMutation.isPending ? "生成中..." : "导出PDF"}
              </Button>
            )}
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => { resetForm(); setIsCreateDialogOpen(true); }}>
                <Plus className="w-4 h-4 mr-2" />
                新建记录
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>新建指导记录</DialogTitle>
                <DialogDescription>记录本次指导的主题和内容</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="guidanceDate">指导日期</Label>
                    <Input
                      id="guidanceDate"
                      type="date"
                      value={formData.guidanceDate}
                      onChange={(e) => setFormData({ ...formData, guidanceDate: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="topic">指导主题/摘要</Label>
                  <Input
                    id="topic"
                    placeholder="简要描述本次指导的主题"
                    value={formData.topic}
                    onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="content">详细内容与收获</Label>
                  <Textarea
                    id="content"
                    placeholder="详细记录本次指导的内容、讨论要点和收获..."
                    className="min-h-[200px]"
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter className="gap-2">
                <Button variant="outline" onClick={() => handleCreate("draft")} disabled={createLogMutation.isPending}>
                  保存为草稿
                </Button>
                <Button onClick={() => handleCreate("submitted")} disabled={createLogMutation.isPending}>
                  <Send className="w-4 h-4 mr-2" />
                  提交给导师
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          </div>
        </div>
        
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">总记录数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{logs?.length || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">草稿</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-500">
                {logs?.filter(l => l.status === "draft").length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">已提交</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {logs?.filter(l => l.status === "submitted").length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">已确认</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {logs?.filter(l => l.status === "confirmed").length || 0}
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* 记录列表 */}
        <Card>
          <CardHeader>
            <CardTitle>指导记录时间线</CardTitle>
            <CardDescription>按时间倒序显示所有指导记录</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">加载中...</div>
            ) : !logs || logs.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">暂无指导记录</p>
                <p className="text-sm text-muted-foreground mt-1">点击"新建记录"开始记录您的指导过程</p>
              </div>
            ) : (
              <div className="space-y-4">
                {logs.map((log) => (
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
                        {log.attachmentCount > 0 && (
                          <Badge variant="outline" className="text-xs">
                            <Paperclip className="w-3 h-3 mr-1" />
                            {log.attachmentCount}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">{log.content}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" onClick={() => openDetailDialog(log.id)}>
                        <Eye className="w-4 h-4" />
                      </Button>
                      {log.status === "draft" && (
                        <>
                          <Button variant="ghost" size="sm" onClick={() => openEditDialog(log)}>
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-destructive" onClick={() => handleDelete(log.id)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* 编辑对话框 */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>编辑指导记录</DialogTitle>
              <DialogDescription>修改指导记录的内容</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="editGuidanceDate">指导日期</Label>
                  <Input
                    id="editGuidanceDate"
                    type="date"
                    value={formData.guidanceDate}
                    onChange={(e) => setFormData({ ...formData, guidanceDate: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="editTopic">指导主题/摘要</Label>
                <Input
                  id="editTopic"
                  placeholder="简要描述本次指导的主题"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="editContent">详细内容与收获</Label>
                <Textarea
                  id="editContent"
                  placeholder="详细记录本次指导的内容、讨论要点和收获..."
                  className="min-h-[200px]"
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter className="gap-2">
              <Button variant="outline" onClick={() => handleUpdate()} disabled={updateLogMutation.isPending}>
                保存
              </Button>
              <Button onClick={() => handleUpdate("submitted")} disabled={updateLogMutation.isPending}>
                <Send className="w-4 h-4 mr-2" />
                提交给导师
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        
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
                  
                  <Separator />
                  
                  {/* 附件区域 */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Paperclip className="w-4 h-4" />
                        附件 ({logDetail.attachments?.length || 0})
                      </h3>
                      {logDetail.status !== "confirmed" && (
                        <div>
                          <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
                            className="hidden"
                            onChange={(e) => handleFileUpload(e.target.files)}
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => fileInputRef.current?.click()}
                            disabled={uploadingFiles}
                          >
                            <Upload className="w-4 h-4 mr-2" />
                            {uploadingFiles ? "上传中..." : "上传附件"}
                          </Button>
                        </div>
                      )}
                    </div>
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
                            <div className="flex items-center gap-2">
                              <Button variant="ghost" size="sm" asChild>
                                <a href={prefixFileUrl(attachment.fileUrl)} target="_blank" rel="noopener noreferrer">
                                  <Download className="w-4 h-4" />
                                </a>
                              </Button>
                              {logDetail.status === "draft" && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="text-destructive"
                                  onClick={() => deleteAttachmentMutation.mutate({ attachmentId: attachment.id })}
                                >
                                  <X className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
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
                      评论 ({logDetail.comments?.length || 0})
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
                        placeholder="添加评论..."
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
