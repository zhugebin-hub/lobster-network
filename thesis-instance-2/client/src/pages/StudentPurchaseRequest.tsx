import { useAuth } from "@/_core/hooks/useAuth";
import { prefixPath, prefixFileUrl } from "@/lib/basePath";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, Download, Upload, FileText, Clock, CheckCircle, XCircle, AlertCircle, MessageSquare, Loader2 } from "lucide-react";
import { useEffect, useState, useRef } from "react";
import { toast } from "sonner";

// 审核状态映射
const statusMap: Record<string, { label: string; labelEn: string; color: string; icon: React.ReactNode }> = {
  pending_lab: { label: "待实验室管理员审核", labelEn: "Pending Lab Admin Review", color: "bg-yellow-100 text-yellow-800", icon: <Clock className="w-4 h-4" /> },
  pending_teacher: { label: "待导师审核", labelEn: "Pending Supervisor Review", color: "bg-blue-100 text-blue-800", icon: <Clock className="w-4 h-4" /> },
  pending_asset: { label: "待资产分管领导审核", labelEn: "Pending Asset Leader Review", color: "bg-purple-100 text-purple-800", icon: <Clock className="w-4 h-4" /> },
  approved: { label: "审核通过", labelEn: "Approved", color: "bg-green-100 text-green-800", icon: <CheckCircle className="w-4 h-4" /> },
  rejected_lab: { label: "实验室管理员拒绝", labelEn: "Rejected by Lab Admin", color: "bg-red-100 text-red-800", icon: <XCircle className="w-4 h-4" /> },
  rejected_teacher: { label: "导师拒绝", labelEn: "Rejected by Supervisor", color: "bg-red-100 text-red-800", icon: <XCircle className="w-4 h-4" /> },
  rejected_asset: { label: "资产分管领导拒绝", labelEn: "Rejected by Asset Leader", color: "bg-red-100 text-red-800", icon: <XCircle className="w-4 h-4" /> },
};

export default function StudentPurchaseRequest() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [, setLocation] = useLocation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 表单状态
  const [studentName, setStudentName] = useState("");
  const [studentClass, setStudentClass] = useState("");
  const [studentNo, setStudentNo] = useState("");
  const [totalAmount, setTotalAmount] = useState("");
  const [reason, setReason] = useState("");
  const [uploadedFile, setUploadedFile] = useState<{ url: string; key: string; name: string } | null>(null);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<any>(null);

  // 查询
  const { data: myRequests, refetch: refetchRequests } = trpc.purchase.getMyRequests.useQuery(undefined, { enabled: isAuthenticated });
  const { data: wechatInfo } = trpc.purchase.getLabAdminWechat.useQuery(undefined, { enabled: isAuthenticated });
  const { data: match } = trpc.match.myMatch.useQuery(undefined, { enabled: isAuthenticated });
  const { data: activeClasses } = trpc.purchase.getActiveClasses.useQuery(undefined, { enabled: isAuthenticated });

  // 提交申请
  const submitMutation = trpc.purchase.submitRequest.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "申请提交成功" : "Request submitted successfully");
      refetchRequests();
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "student" && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  useEffect(() => {
    // 自动填充用户信息
    if (user) {
      setStudentName(user.name || "");
      setStudentClass(user.studentClass || "");
      setStudentNo(user.studentId || "");
    }
  }, [user]);

  const resetForm = () => {
    setTotalAmount("");
    setReason("");
    setUploadedFile(null);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 验证文件类型
    const allowedTypes = [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
      "application/pdf",
    ];
    if (!allowedTypes.includes(file.type)) {
      toast.error(language === "zh" ? "请上传 Word 或 PDF 文件" : "Please upload Word or PDF file");
      return;
    }

    // 验证文件大小 (20MB)
    if (file.size > 20 * 1024 * 1024) {
      toast.error(language === "zh" ? "文件大小不能超过 20MB" : "File size cannot exceed 20MB");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(prefixPath("/api/upload"), {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      setUploadedFile({
        url: data.url,
        key: data.fileKey,  // API返回的是fileKey而不是key
        name: file.name,
      });
      toast.success(language === "zh" ? "文件上传成功" : "File uploaded successfully");
    } catch (error) {
      toast.error(language === "zh" ? "文件上传失败" : "File upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async () => {
    if (!studentName.trim()) {
      toast.error(language === "zh" ? "请输入学生姓名" : "Please enter student name");
      return;
    }
    if (!studentClass.trim()) {
      toast.error(language === "zh" ? "请输入班级" : "Please enter class");
      return;
    }
    if (!studentNo.trim()) {
      toast.error(language === "zh" ? "请输入学号" : "Please enter student ID");
      return;
    }
    if (!totalAmount.trim()) {
      toast.error(language === "zh" ? "请输入总费用" : "Please enter total amount");
      return;
    }
    if (!uploadedFile) {
      toast.error(language === "zh" ? "请上传申请文件" : "Please upload application file");
      return;
    }

    setSubmitting(true);
    try {
      await submitMutation.mutateAsync({
        studentName,
        studentClass,
        studentNo,
        totalAmount,
        reason,
        fileUrl: uploadedFile.url,
        fileKey: uploadedFile.key,
        fileName: uploadedFile.name,
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  // 检查是否有已通过的申请
  const approvedRequest = myRequests?.find(r => r.status === "approved");

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/student")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold">{language === "zh" ? "毕设采购申请" : "Thesis Purchase Request"}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* 采购申请流程图 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              {language === "zh" ? "采购申请流程" : "Purchase Request Process"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <div className="flex items-start gap-0 min-w-[700px] py-4">
                {/* 步骤1: 学生填写信息 */}
                <div className="flex flex-col items-center">
                  <div className="w-32 h-16 bg-blue-100 border-2 border-blue-500 rounded-lg flex items-center justify-center text-center px-2">
                    <span className="text-sm font-medium text-blue-700">
                      {language === "zh" ? "学生填写信息" : "Student Fills Info"}
                    </span>
                  </div>
                </div>
                {/* 箭头 */}
                <div className="flex items-center h-16">
                  <div className="w-8 h-0.5 bg-blue-400"></div>
                  <div className="w-0 h-0 border-t-4 border-b-4 border-l-6 border-t-transparent border-b-transparent border-l-blue-400"></div>
                </div>
                {/* 步骤2: 实验室管理员审核 */}
                <div className="flex flex-col items-center">
                  <div className="w-36 h-16 bg-blue-100 border-2 border-blue-500 rounded-lg flex items-center justify-center text-center px-2">
                    <span className="text-sm font-medium text-blue-700">
                      {language === "zh" ? "实验室管理员审核" : "Lab Admin Review"}
                    </span>
                  </div>
                </div>
                {/* 箭头 */}
                <div className="flex items-center h-16">
                  <div className="w-8 h-0.5 bg-blue-400"></div>
                  <div className="w-0 h-0 border-t-4 border-b-4 border-l-6 border-t-transparent border-b-transparent border-l-blue-400"></div>
                </div>
                {/* 步骤3: 导师审核 */}
                <div className="flex flex-col items-center relative">
                  <div className="w-28 h-16 bg-blue-100 border-2 border-blue-500 rounded-lg flex items-center justify-center text-center px-2">
                    <span className="text-sm font-medium text-blue-700">
                      {language === "zh" ? "导师审核" : "Supervisor Review"}
                    </span>
                  </div>
                  {/* 超额分支 */}
                  <div className="absolute top-16 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
                    <div className="w-0.5 h-6 bg-orange-400"></div>
                    <div className="text-xs text-orange-600 whitespace-nowrap mb-1">
                      {language === "zh" ? "超额（即总费用超过1500元）" : "Over 1500 CNY"}
                    </div>
                    <div className="w-0 h-0 border-l-4 border-r-4 border-t-6 border-l-transparent border-r-transparent border-t-orange-400"></div>
                    <div className="w-28 h-14 bg-orange-100 border-2 border-orange-500 rounded-lg flex items-center justify-center text-center px-2 mt-1">
                      <span className="text-xs font-medium text-orange-700">
                        {language === "zh" ? "资产分管领导审核" : "Asset Leader Review"}
                      </span>
                    </div>
                    <div className="w-0.5 h-6 bg-orange-400"></div>
                  </div>
                </div>
                {/* 箭头 */}
                <div className="flex items-center h-16">
                  <div className="w-8 h-0.5 bg-blue-400"></div>
                  <div className="w-0 h-0 border-t-4 border-b-4 border-l-6 border-t-transparent border-b-transparent border-l-blue-400"></div>
                </div>
                {/* 步骤4: 加微信代付购买 */}
                <div className="flex flex-col items-center">
                  <div className="w-44 h-16 bg-green-100 border-2 border-green-500 rounded-lg flex items-center justify-center text-center px-2">
                    <span className="text-sm font-medium text-green-700">
                      {language === "zh" ? "加实验室管理员微信\n进行后续代付购买" : "Add Lab Admin WeChat\nfor Payment"}
                    </span>
                  </div>
                  <div className="mt-2 text-xs text-red-600 font-medium">
                    {language === "zh" ? "❗ 不可自行购买" : "❗ Do NOT purchase yourself"}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 未匹配导师提示 */}
        {!match && (
          <Card className="mb-6 border-orange-200 bg-orange-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-700">
                <AlertCircle className="w-5 h-5" />
                {language === "zh" ? "无法提交申请" : "Cannot Submit Request"}
              </CardTitle>
              <CardDescription className="text-orange-600">
                {language === "zh" 
                  ? "您还未确认导师，请先完成选题并等待导师确认后再提交采购申请" 
                  : "You haven't confirmed a supervisor yet. Please complete topic selection and wait for supervisor confirmation before submitting purchase requests."}
              </CardDescription>
            </CardHeader>
          </Card>
        )}

        {/* 审核通过后显示微信信息 */}
        {approvedRequest && wechatInfo && (
          <Card className="mb-6 border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-700">
                <CheckCircle className="w-5 h-5" />
                {language === "zh" ? "审核已通过" : "Request Approved"}
              </CardTitle>
              <CardDescription>
                {language === "zh" 
                  ? "请添加实验室管理员微信进行后续代付购买" 
                  : "Please add lab admin on WeChat for payment"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <MessageSquare className="w-8 h-8 text-green-600" />
                <div>
                  <p className="font-medium">{language === "zh" ? "微信号" : "WeChat ID"}: {wechatInfo.wechatId}</p>
                  {wechatInfo.wechatNote && (
                    <p className="text-sm text-gray-600">{wechatInfo.wechatNote}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid md:grid-cols-2 gap-6">
          {/* 申请表单 */}
          <Card>
            <CardHeader>
              <CardTitle>{language === "zh" ? "提交新申请" : "Submit New Request"}</CardTitle>
              <CardDescription>
                {language === "zh" 
                  ? "请下载模板文件，填写完成后上传" 
                  : "Download template, fill in and upload"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 下载模板 */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start gap-3">
                  <Download className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-medium text-blue-900">
                      {language === "zh" ? "下载申请模板" : "Download Application Template"}
                    </h4>
                    <p className="text-sm text-blue-700 mt-1">
                      {language === "zh" 
                        ? "请先下载《人工智能本科生耗材申请》模板文件，填写完成后再上传" 
                        : "Please download the template first, fill in and upload"}
                    </p>
                    <a 
                      href={prefixPath("/files/templates/人工智能本科生耗材申请.docx")} 
                      download="人工智能本科生耗材申请.docx"
                      className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-white border border-blue-300 rounded-md text-blue-600 hover:bg-blue-50 hover:text-blue-800 text-sm font-medium transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      {language === "zh" ? "下载申请模板 (.docx)" : "Download Template (.docx)"}
                    </a>
                  </div>
                </div>
              </div>

              {/* 申请时间 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "申请时间" : "Application Time"}</Label>
                <Input value={new Date().toLocaleString()} disabled />
              </div>

              {/* 学生姓名 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "学生姓名" : "Student Name"} *</Label>
                <Input 
                  value={studentName} 
                  onChange={(e) => setStudentName(e.target.value)}
                  placeholder={language === "zh" ? "请输入姓名" : "Enter name"}
                />
              </div>

              {/* 班级 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "班级" : "Class"} *</Label>
                <Select value={studentClass} onValueChange={setStudentClass}>
                  <SelectTrigger>
                    <SelectValue placeholder={language === "zh" ? "请选择班级" : "Select class"} />
                  </SelectTrigger>
                  <SelectContent>
                    {activeClasses && activeClasses.length > 0 ? (
                      activeClasses.map((cls) => (
                        <SelectItem key={cls} value={cls}>{cls}</SelectItem>
                      ))
                    ) : (
                      <SelectItem value="_loading" disabled>
                        {language === "zh" ? "加载中..." : "Loading..."}
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* 学号 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "学号" : "Student ID"} *</Label>
                <Input 
                  value={studentNo} 
                  onChange={(e) => setStudentNo(e.target.value)}
                  placeholder={language === "zh" ? "请输入学号" : "Enter student ID"}
                />
              </div>

              {/* 总费用 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "总费用（元）" : "Total Amount (CNY)"} *</Label>
                <Input 
                  type="number"
                  value={totalAmount} 
                  onChange={(e) => setTotalAmount(e.target.value)}
                  placeholder={language === "zh" ? "请输入总费用" : "Enter total amount"}
                />
                {parseFloat(totalAmount) > 1500 && (
                  <p className="text-sm text-orange-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {language === "zh" 
                      ? "超过1500元需要资产分管领导额外审批" 
                      : "Amount over 1500 CNY requires additional approval"}
                  </p>
                )}
              </div>

              {/* 申请原因 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "申请原因" : "Reason"}</Label>
                <Textarea 
                  value={reason} 
                  onChange={(e) => setReason(e.target.value)}
                  placeholder={language === "zh" ? "请输入申请原因（选填）" : "Enter reason (optional)"}
                  rows={3}
                />
              </div>

              {/* 文件上传 */}
              <div className="space-y-2">
                <Label>{language === "zh" ? "上传申请文件" : "Upload Application File"} *</Label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".doc,.docx,.pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                {uploadedFile ? (
                  <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                    <FileText className="w-5 h-5 text-green-600" />
                    <span className="flex-1 text-sm truncate">{uploadedFile.name}</span>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setUploadedFile(null)}
                    >
                      {language === "zh" ? "删除" : "Remove"}
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                  >
                    {uploading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Upload className="w-4 h-4 mr-2" />
                    )}
                    {uploading 
                      ? (language === "zh" ? "上传中..." : "Uploading...") 
                      : (language === "zh" ? "选择文件" : "Select File")}
                  </Button>
                )}
                <p className="text-xs text-gray-500">
                  {language === "zh" 
                    ? "支持 Word (.doc, .docx) 和 PDF 格式，最大 20MB" 
                    : "Supports Word (.doc, .docx) and PDF, max 20MB"}
                </p>
              </div>

              {/* 提交按钮 */}
              <Button 
                className="w-full" 
                onClick={handleSubmit}
                disabled={submitting || !uploadedFile || !match}
              >
                {submitting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                {!match 
                  ? (language === "zh" ? "请先确认导师" : "Confirm Supervisor First")
                  : (language === "zh" ? "提交申请" : "Submit Request")}
              </Button>
            </CardContent>
          </Card>

          {/* 申请记录 */}
          <Card>
            <CardHeader>
              <CardTitle>{language === "zh" ? "我的申请记录" : "My Requests"}</CardTitle>
              <CardDescription>
                {language === "zh" ? "查看申请状态和审核进度" : "View request status and progress"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!myRequests || myRequests.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  {language === "zh" ? "暂无申请记录" : "No requests yet"}
                </div>
              ) : (
                <div className="space-y-4">
                  {myRequests.map((request) => {
                    const status = statusMap[request.status] || statusMap.pending_lab;
                    return (
                      <Dialog key={request.id}>
                        <DialogTrigger asChild>
                          <div 
                            className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => setSelectedRequest(request)}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm text-gray-500">
                                {new Date(request.applyTime).toLocaleDateString()}
                              </span>
                              <Badge className={status.color}>
                                {status.icon}
                                <span className="ml-1">{language === "zh" ? status.label : status.labelEn}</span>
                              </Badge>
                            </div>
                            <p className="font-medium">¥{request.totalAmount}</p>
                            <p className="text-sm text-gray-600 truncate">{request.fileName}</p>
                          </div>
                        </DialogTrigger>
                        <DialogContent className="max-w-lg">
                          <DialogHeader>
                            <DialogTitle>{language === "zh" ? "申请详情" : "Request Details"}</DialogTitle>
                            <DialogDescription>
                              {language === "zh" ? "查看完整的申请信息和审核进度" : "View full request information and progress"}
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <Label className="text-gray-500">{language === "zh" ? "申请时间" : "Apply Time"}</Label>
                                <p>{new Date(request.applyTime).toLocaleString()}</p>
                              </div>
                              <div>
                                <Label className="text-gray-500">{language === "zh" ? "总费用" : "Total Amount"}</Label>
                                <p className="font-medium">¥{request.totalAmount}</p>
                              </div>
                              <div>
                                <Label className="text-gray-500">{language === "zh" ? "姓名" : "Name"}</Label>
                                <p>{request.studentName}</p>
                              </div>
                              <div>
                                <Label className="text-gray-500">{language === "zh" ? "班级" : "Class"}</Label>
                                <p>{request.studentClass}</p>
                              </div>
                            </div>
                            
                            {request.reason && (
                              <div>
                                <Label className="text-gray-500">{language === "zh" ? "申请原因" : "Reason"}</Label>
                                <p className="text-sm">{request.reason}</p>
                              </div>
                            )}

                            <div>
                              <Label className="text-gray-500">{language === "zh" ? "申请文件" : "Application File"}</Label>
                              <a 
                                href={prefixFileUrl(request.fileUrl)} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
                              >
                                <FileText className="w-4 h-4" />
                                {request.fileName}
                              </a>
                            </div>

                            {/* 审核进度 */}
                            <div>
                              <Label className="text-gray-500 mb-2 block">{language === "zh" ? "审核进度" : "Review Progress"}</Label>
                              <div className="space-y-2">
                                {/* 实验室管理员审核 */}
                                <div className={`flex items-center gap-2 p-2 rounded ${
                                  request.labReviewedAt ? (request.status === "rejected_lab" ? "bg-red-50" : "bg-green-50") : "bg-gray-50"
                                }`}>
                                  {request.labReviewedAt ? (
                                    request.status === "rejected_lab" ? <XCircle className="w-4 h-4 text-red-600" /> : <CheckCircle className="w-4 h-4 text-green-600" />
                                  ) : (
                                    <Clock className="w-4 h-4 text-gray-400" />
                                  )}
                                  <span className="text-sm">{language === "zh" ? "实验室管理员审核" : "Lab Admin Review"}</span>
                                  {request.labComment && <span className="text-xs text-gray-500 ml-auto">{request.labComment}</span>}
                                </div>

                                {/* 导师审核 */}
                                <div className={`flex items-center gap-2 p-2 rounded ${
                                  request.teacherReviewedAt ? (request.status === "rejected_teacher" ? "bg-red-50" : "bg-green-50") : "bg-gray-50"
                                }`}>
                                  {request.teacherReviewedAt ? (
                                    request.status === "rejected_teacher" ? <XCircle className="w-4 h-4 text-red-600" /> : <CheckCircle className="w-4 h-4 text-green-600" />
                                  ) : (
                                    <Clock className="w-4 h-4 text-gray-400" />
                                  )}
                                  <span className="text-sm">{language === "zh" ? "导师审核" : "Supervisor Review"}</span>
                                  {request.teacherComment && <span className="text-xs text-gray-500 ml-auto">{request.teacherComment}</span>}
                                </div>

                                {/* 资产分管领导审核（仅超额时显示） */}
                                {request.isOverBudget === 1 && (
                                  <div className={`flex items-center gap-2 p-2 rounded ${
                                    request.assetReviewedAt ? (request.status === "rejected_asset" ? "bg-red-50" : "bg-green-50") : "bg-gray-50"
                                  }`}>
                                    {request.assetReviewedAt ? (
                                      request.status === "rejected_asset" ? <XCircle className="w-4 h-4 text-red-600" /> : <CheckCircle className="w-4 h-4 text-green-600" />
                                    ) : (
                                      <Clock className="w-4 h-4 text-gray-400" />
                                    )}
                                    <span className="text-sm">{language === "zh" ? "资产分管领导审核" : "Asset Leader Review"}</span>
                                    {request.assetComment && <span className="text-xs text-gray-500 ml-auto">{request.assetComment}</span>}
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* 审核通过后显示微信信息 */}
                            {request.status === "approved" && wechatInfo && (
                              <div className="p-4 bg-green-50 rounded-lg">
                                <p className="font-medium text-green-700 mb-2">
                                  {language === "zh" ? "请添加实验室管理员微信" : "Please add lab admin on WeChat"}
                                </p>
                                <p className="flex items-center gap-2">
                                  <MessageSquare className="w-4 h-4" />
                                  {wechatInfo.wechatId}
                                </p>
                                {wechatInfo.wechatNote && (
                                  <p className="text-sm text-gray-600 mt-1">{wechatInfo.wechatNote}</p>
                                )}
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
