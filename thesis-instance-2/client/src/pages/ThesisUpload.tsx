import { useState, useRef, useEffect } from "react";
import { prefixPath, prefixFileUrl } from "@/lib/basePath";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft, 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  Clock,
  User,
  BookOpen,
  Download,
  History,
  RefreshCw,
  Hourglass,
  CheckCheck
} from "lucide-react";
import { toast } from "sonner";

export default function ThesisUpload() {
  const [, setLocation] = useLocation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [draftInfo, setDraftInfo] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [language] = useState("zh");

  // 获取论文终稿信息
  const fetchDraftInfo = async () => {
    try {
      const response = await fetch(prefixPath("/api/trpc/thesis.getMyDraft"));
      const result = await response.json();
      if (result.result?.data?.json) {
        setDraftInfo(result.result.data.json);
        // 如果有终稿，获取历史版本
        if (result.result.data.json?.draft?.id) {
          const historyRes = await fetch(`${prefixPath("/api/trpc/thesis.getDraftHistory")}?input=${encodeURIComponent(JSON.stringify({ json: { draftId: result.result.data.json.draft.id } }))}`);
          const historyResult = await historyRes.json();
          if (historyResult.result?.data?.json) {
            setHistory(historyResult.result.data.json);
          }
        }
      }
    } catch (error) {
      console.error("获取论文信息失败:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDraftInfo();
  }, []);

  // 处理文件选择
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 检查文件类型
    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ];
    if (!allowedTypes.includes(file.type)) {
      toast.error("只支持 PDF、DOC、DOCX 格式的文件");
      return;
    }

    // 检查文件大小 (50MB)
    if (file.size > 50 * 1024 * 1024) {
      toast.error("文件大小不能超过 50MB");
      return;
    }

    setSelectedFile(file);
  };

  // 上传文件到服务器
  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(10);

    try {
      // 创建 FormData
      const formData = new FormData();
      formData.append("file", selectedFile);

      setUploadProgress(30);

      // 上传到服务器
      const response = await fetch(prefixPath("/api/upload"), {
        method: "POST",
        body: formData,
      });

      setUploadProgress(70);

      if (!response.ok) {
        throw new Error("文件上传失败");
      }

      const result = await response.json();
      setUploadProgress(90);

      // 保存论文记录
      const saveResponse = await fetch(prefixPath("/api/trpc/thesis.uploadDraft"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          json: {
            fileName: selectedFile.name,
            fileKey: result.fileKey,
            fileUrl: result.url,
            fileSize: selectedFile.size,
            mimeType: selectedFile.type,
          }
        }),
      });

      if (!saveResponse.ok) {
        const errorData = await saveResponse.json().catch(() => ({}));
        throw new Error(errorData?.error?.json?.message || "保存论文记录失败");
      }

      const saveResult = await saveResponse.json();
      setUploadProgress(100);
      
      // 检查是否为宽限期提交
      if (saveResult?.result?.data?.json?.isLateSubmission) {
        const penalty = saveResult.result.data.json.latePenalty;
        toast.warning(`论文已在宽限期内提交，将扣除${penalty}分`, {
          duration: 5000,
        });
      } else {
        toast.success("论文上传成功！");
      }
      setSelectedFile(null);
      fetchDraftInfo();
    } catch (error: any) {
      toast.error(error.message || "上传失败");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  // 格式化日期
  const formatDate = (date: Date | string) => {
    return new Date(date).toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // 获取时间段状态的显示颜色和图标
  const getUploadPeriodDisplay = () => {
    if (!draftInfo?.uploadPeriodStatus) return null;
    
    const status = draftInfo.uploadPeriodStatus;
    const startTime = draftInfo.uploadStartTime ? new Date(draftInfo.uploadStartTime) : null;
    const endTime = draftInfo.uploadEndTime ? new Date(draftInfo.uploadEndTime) : null;
    const gracePeriod = draftInfo.gracePeriod;
    const graceEndTime = gracePeriod?.graceEndTime ? new Date(gracePeriod.graceEndTime) : null;
    
    switch (status) {
      case "进行中":
        return {
          color: "border-green-200 bg-green-50",
          textColor: "text-green-700",
          icon: CheckCheck,
          title: "论文上传时间段进行中",
          description: `截止时间：${endTime?.toLocaleString("zh-CN") || "未设置"}`,
          penalty: 0,
          showGraceInfo: false,
        };
      case "等待中":
        return {
          color: "border-blue-200 bg-blue-50",
          textColor: "text-blue-700",
          icon: Hourglass,
          title: "论文上传时间段未开始",
          description: `开始时间：${startTime?.toLocaleString("zh-CN") || "未设置"}`,
          penalty: 0,
          showGraceInfo: false,
        };
      case "宽限期-24小时内":
        return {
          color: "border-orange-200 bg-orange-50",
          textColor: "text-orange-700",
          icon: AlertCircle,
          title: "宽限期 - 24小时内",
          description: `已超过截止时间 ${gracePeriod?.hoursOverdue || 0} 小时，提交将扣除5分`,
          penalty: 5,
          showGraceInfo: true,
          graceEndTime,
        };
      case "宽限期-7天内":
        return {
          color: "border-red-200 bg-red-50",
          textColor: "text-red-700",
          icon: AlertCircle,
          title: "宽限期 - 超过24小时",
          description: `已超过截止时间 ${gracePeriod?.daysOverdue || 0} 天 ${(gracePeriod?.hoursOverdue || 0) % 24} 小时，提交将扣除10分`,
          penalty: 10,
          showGraceInfo: true,
          graceEndTime,
        };
      case "已关闭":
        return {
          color: "border-gray-400 bg-gray-100",
          textColor: "text-gray-700",
          icon: AlertCircle,
          title: "论文提交已关闭",
          description: `宽限期已于 ${graceEndTime?.toLocaleString("zh-CN") || "未知"} 结束，无法再提交`,
          penalty: 0,
          showGraceInfo: false,
        };
      case "未配置":
        return {
          color: "border-gray-200 bg-gray-50",
          textColor: "text-gray-700",
          icon: Clock,
          title: "论文上传时间段未配置",
          description: "管理员未配置论文上传时间段",
          penalty: 0,
          showGraceInfo: false,
        };
      default:
        return null;
    }
  };

  // 获取状态标签
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "submitted":
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">已提交</Badge>;
      case "reviewed":
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">已查看</Badge>;
      case "approved":
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">已通过</Badge>;
      default:
        return <Badge variant="outline">未知</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  // 检查是否已匹配课题
  if (!draftInfo?.match) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-2xl mx-auto">
          <Button
            variant="ghost"
            onClick={() => setLocation("/student")}
            className="mb-6"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回控制台
          </Button>

          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              您还未匹配课题，无法上传论文终稿。请先完成志愿填报并等待匹配结果。
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* 返回按钮 */}
        <Button
          variant="ghost"
          onClick={() => setLocation("/student")}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          返回控制台
        </Button>

        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">论文终稿提交</h1>
          <p className="text-gray-600 mt-1">上传您的毕业论文终稿，支持 PDF、DOC、DOCX 格式</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：课题和导师信息 */}
          <div className="lg:col-span-1 space-y-6">
            {/* 课题信息 */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-blue-600" />
                  已选课题
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-500">课题名称</p>
                    <p className="font-medium">{draftInfo.topic?.titleEn || draftInfo.topic?.title}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 导师信息 */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <User className="h-5 w-5 text-green-600" />
                  指导教师
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-500">教师姓名</p>
                    <p className="font-medium">{draftInfo.teacher?.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">联系邮箱</p>
                    <p className="text-sm text-blue-600">{draftInfo.teacher?.email}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 右侧：上传区域和历史记录 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 时间段状态提示 */}
            {(() => {
              const display = getUploadPeriodDisplay();
              if (!display) return null;
              const IconComponent = display.icon;
              return (
                <Card className={`border-2 ${display.color}`}>
                  <CardHeader className="pb-3">
                    <CardTitle className={`text-lg flex items-center gap-2 ${display.textColor}`}>
                      <IconComponent className="h-5 w-5" />
                      {display.title}
                      {display.penalty > 0 && (
                        <Badge variant="destructive" className="ml-2">
                          扣{display.penalty}分
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription>{display.description}</CardDescription>
                  </CardHeader>
                  {display.showGraceInfo && (
                    <CardContent className="pt-0">
                      <div className="bg-white/80 rounded-lg p-4 space-y-3">
                        <div className="text-sm font-medium text-gray-700">宽限期扣分规则：</div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                          <div className={`p-3 rounded-lg border ${display.penalty === 5 ? 'bg-orange-100 border-orange-300' : 'bg-gray-50 border-gray-200'}`}>
                            <div className="font-medium">截止后24小时内</div>
                            <div className="text-orange-600 font-bold">扣除5分</div>
                          </div>
                          <div className={`p-3 rounded-lg border ${display.penalty === 10 ? 'bg-red-100 border-red-300' : 'bg-gray-50 border-gray-200'}`}>
                            <div className="font-medium">超过24小时至7天内</div>
                            <div className="text-red-600 font-bold">扣除10分</div>
                          </div>
                          <div className="p-3 rounded-lg border bg-gray-50 border-gray-200">
                            <div className="font-medium">7天后</div>
                            <div className="text-gray-600 font-bold">系统关闭</div>
                          </div>
                        </div>
                        {display.graceEndTime && (
                          <div className="text-sm text-gray-600 pt-2 border-t">
                            <Clock className="h-4 w-4 inline mr-1" />
                            宽限期结束时间：{display.graceEndTime.toLocaleString("zh-CN")}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  )}
                </Card>
              );
            })()}

            {/* 当前论文状态 */}
            {draftInfo.draft && (
              <Card className={draftInfo.draft.lateSubmission ? "border-orange-200 bg-orange-50/50" : "border-green-200 bg-green-50/50"}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <CheckCircle className={draftInfo.draft.lateSubmission ? "h-5 w-5 text-orange-600" : "h-5 w-5 text-green-600"} />
                      已提交论文
                      {draftInfo.draft.lateSubmission === 1 && (
                        <Badge variant="outline" className="bg-orange-100 text-orange-700 border-orange-300 ml-2">
                          宽限期提交
                        </Badge>
                      )}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      {draftInfo.draft.latePenalty > 0 && (
                        <Badge variant="destructive">
                          扣{draftInfo.draft.latePenalty}分
                        </Badge>
                      )}
                      {getStatusBadge(draftInfo.draft.status)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between p-4 bg-white rounded-lg border">
                    <div className="flex items-center gap-3">
                      <FileText className="h-10 w-10 text-blue-600" />
                      <div>
                        <p className="font-medium">{draftInfo.draft.fileName}</p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(draftInfo.draft.fileSize)} · 版本 {draftInfo.draft.version}
                        </p>
                        <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                          <Clock className="h-3 w-3" />
                          提交于 {formatDate(draftInfo.draft.submittedAt)}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(prefixFileUrl(draftInfo.draft!.fileUrl), "_blank")}
                    >
                      <Download className="h-4 w-4 mr-1" />
                      下载
                    </Button>
                  </div>
                  {draftInfo.draft.lateSubmission === 1 && (
                    <Alert className="mt-4 bg-orange-50 border-orange-200">
                      <AlertCircle className="h-4 w-4 text-orange-600" />
                      <AlertDescription className="text-orange-700">
                        该论文在宽限期内提交，最终成绩将扣除 <strong>{draftInfo.draft.latePenalty}</strong> 分。
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* 最终成绩显示 */}
                  {draftInfo.draft.finalScore !== null && draftInfo.draft.finalScore !== undefined && (
                    <div className="mt-4 bg-green-50 border border-green-200 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <CheckCheck className="h-5 w-5 text-green-600" />
                        <span className="text-sm font-medium text-green-800">最终成绩</span>
                      </div>
                      <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-3xl font-bold text-green-700">{draftInfo.draft.finalScore}</span>
                        <span className="text-sm text-green-600">分</span>
                        {draftInfo.draft.latePenalty > 0 && (
                          <span className="text-xs text-orange-600 ml-2">
                            (已扣除迟交罚分{draftInfo.draft.latePenalty}分)
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* 评分进度显示 */}
                  {draftInfo.draft.finalScore === null && draftInfo.draft.score !== null && (
                    <div className="mt-4 bg-blue-50 border border-blue-200 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Clock className="h-5 w-5 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">评分进度</span>
                      </div>
                      <div className="mt-2 text-sm text-blue-700">
                        {draftInfo.draft.secondTeacherScore !== null 
                          ? "两位导师已完成评分，最终成绩确认中..."
                          : "第一导师已评分，等待第二导师评分..."}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* 上传区域 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Upload className="h-5 w-5 text-blue-600" />
                  {draftInfo.draft ? "更新论文" : "上传论文"}
                </CardTitle>
                <CardDescription>
                  {draftInfo.draft 
                    ? "您可以上传新版本的论文，系统会保留历史版本记录" 
                    : "请上传您的毕业论文终稿"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* 文件选择区域 */}
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                      selectedFile 
                        ? "border-blue-300 bg-blue-50" 
                        : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
                    }`}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    {selectedFile ? (
                      <div className="space-y-2">
                        <FileText className="h-12 w-12 text-blue-600 mx-auto" />
                        <p className="font-medium text-gray-900">{selectedFile.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                        <Button
                          variant="link"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedFile(null);
                          }}
                        >
                          重新选择
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                        <p className="text-gray-600">点击选择文件或拖拽文件到此处</p>
                        <p className="text-sm text-gray-400">支持 PDF、DOC、DOCX 格式，最大 50MB</p>
                      </div>
                    )}
                  </div>

                  {/* 上传进度 */}
                  {uploading && (
                    <div className="space-y-2">
                      <Progress value={uploadProgress} className="h-2" />
                      <p className="text-sm text-center text-gray-500">
                        上传中... {uploadProgress}%
                      </p>
                    </div>
                  )}

                  {/* 确认上传按钮 */}
                  {selectedFile && !uploading && (
                    <Alert className="bg-yellow-50 border-yellow-200">
                      <AlertCircle className="h-4 w-4 text-yellow-600" />
                      <AlertDescription className="text-yellow-800">
                        {draftInfo.draft 
                          ? "确认上传后，当前版本将被归档，新版本将成为最新论文。" 
                          : "请确认文件内容无误后再上传，上传后导师将收到通知。"}
                      </AlertDescription>
                    </Alert>
                  )}

                  <Button
                    className="w-full"
                    size="lg"
                    disabled={!selectedFile || uploading}
                    onClick={handleUpload}
                  >
                    {uploading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        上传中...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        {draftInfo.draft ? "确认更新" : "确认上传"}
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 历史版本 */}
            {history && history.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <History className="h-5 w-5 text-gray-600" />
                    历史版本
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {history.map((item: any) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-8 w-8 text-gray-400" />
                          <div>
                            <p className="font-medium text-sm">{item.fileName}</p>
                            <p className="text-xs text-gray-500">
                              版本 {item.version} · {formatFileSize(item.fileSize)}
                            </p>
                            <p className="text-xs text-gray-400">
                              归档于 {formatDate(item.archivedAt)}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(prefixFileUrl(item.fileUrl), "_blank")}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
