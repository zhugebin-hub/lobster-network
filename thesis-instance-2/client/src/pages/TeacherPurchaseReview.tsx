import { useAuth } from "@/_core/hooks/useAuth";
import { prefixFileUrl } from "@/lib/basePath";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, FileText, CheckCircle, XCircle, Clock, Loader2, AlertCircle, MessageSquare, History, Download, Search, Filter, Trash2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useEffect, useState } from "react";
import { toast } from "sonner";

// 审核状态映射
const statusMap: Record<string, { label: string; labelEn: string; color: string }> = {
  pending_lab: { label: "待实验室管理员审核", labelEn: "Pending Lab Admin", color: "bg-yellow-100 text-yellow-800" },
  pending_teacher: { label: "待导师审核", labelEn: "Pending Supervisor", color: "bg-blue-100 text-blue-800" },
  pending_asset: { label: "待资产分管领导审核", labelEn: "Pending Asset Leader", color: "bg-purple-100 text-purple-800" },
  approved: { label: "审核通过", labelEn: "Approved", color: "bg-green-100 text-green-800" },
  rejected_lab: { label: "实验室管理员拒绝", labelEn: "Rejected by Lab Admin", color: "bg-red-100 text-red-800" },
  rejected_teacher: { label: "导师拒绝", labelEn: "Rejected by Supervisor", color: "bg-red-100 text-red-800" },
  rejected_asset: { label: "资产分管领导拒绝", labelEn: "Rejected by Asset Leader", color: "bg-red-100 text-red-800" },
};

export default function TeacherPurchaseReview() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [, setLocation] = useLocation();

  // 审核相关状态
  const [reviewComment, setReviewComment] = useState("");
  const [reviewingRequest, setReviewingRequest] = useState<any>(null);
  const [reviewAction, setReviewAction] = useState<"approve" | "reject" | null>(null);
  const [selectedRequest, setSelectedRequest] = useState<any>(null);
  
  // 审核记录筛选状态
  const [historyClassFilter, setHistoryClassFilter] = useState("");
  const [historyNameFilter, setHistoryNameFilter] = useState("");
  const [historyResultFilter, setHistoryResultFilter] = useState<"all" | "approved" | "rejected">("all");
  const [historyStartDate, setHistoryStartDate] = useState("");
  const [historyEndDate, setHistoryEndDate] = useState("");
  const [activeTab, setActiveTab] = useState("pending");
  
  // 微信信息状态（必须在条件return之前调用）
  const [editingWechat, setEditingWechat] = useState(false);
  const [newWechatId, setNewWechatId] = useState("");
  const [newWechatNote, setNewWechatNote] = useState("");

  // 删除确认对话框状态
  const [deletingRecord, setDeletingRecord] = useState<any>(null);

  // 查询
  const { data: pendingRequests, refetch: refetchPending } = trpc.purchase.getPendingTeacherReview.useQuery(undefined, { enabled: isAuthenticated && (user?.role === "teacher" || user?.role === "admin") });
  const { data: isLabAdmin } = trpc.purchase.isLabAdmin.useQuery(undefined, { enabled: isAuthenticated });
  const { data: isAssetLeader } = trpc.purchase.isAssetLeader.useQuery(undefined, { enabled: isAuthenticated });
  const { data: wechatInfo } = trpc.purchase.getLabAdminWechat.useQuery(undefined, { enabled: isAuthenticated });
  const { data: mySpecialRoles } = trpc.purchase.getMySpecialRoles.useQuery(undefined, { enabled: isAuthenticated });

  // 实验室管理员待审核
  const { data: pendingLabRequests, refetch: refetchLabRequests } = trpc.purchase.getPendingLabReview.useQuery(undefined, { enabled: isAuthenticated && isLabAdmin });
  // 资产分管领导待审核
  const { data: pendingAssetRequests, refetch: refetchAssetRequests } = trpc.purchase.getPendingAssetReview.useQuery(undefined, { enabled: isAuthenticated && isAssetLeader });
  // 审核记录查询
  const { data: reviewHistory, refetch: refetchHistory } = trpc.purchase.getTeacherReviewHistory.useQuery(
    {
      studentClass: historyClassFilter || undefined,
      studentName: historyNameFilter || undefined,
      startDate: historyStartDate ? new Date(historyStartDate) : undefined,
      endDate: historyEndDate ? new Date(historyEndDate + "T23:59:59") : undefined,
      result: historyResultFilter === "all" ? undefined : historyResultFilter,
    },
    { enabled: isAuthenticated && (user?.role === "teacher" || user?.role === "admin") }
  );
  // 获取班级列表用于筛选
  const { data: activeClasses } = trpc.purchase.getActiveClasses.useQuery(undefined, { enabled: isAuthenticated });

  // Mutations
  const teacherReviewMutation = trpc.purchase.teacherReview.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "审核完成" : "Review completed");
      refetchPending();
      setReviewingRequest(null);
      setReviewComment("");
    },
    onError: (error) => toast.error(error.message),
  });

  const labReviewMutation = trpc.purchase.labReview.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "审核完成" : "Review completed");
      refetchLabRequests();
      setReviewingRequest(null);
      setReviewComment("");
    },
    onError: (error) => toast.error(error.message),
  });

  const assetReviewMutation = trpc.purchase.assetReview.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "审核完成" : "Review completed");
      refetchAssetRequests();
      setReviewingRequest(null);
      setReviewComment("");
    },
    onError: (error) => toast.error(error.message),
  });

  const updateWechatMutation = trpc.purchase.updateLabAdminWechat.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "微信信息更新成功" : "WeChat info updated");
    },
    onError: (error) => toast.error(error.message),
  });

  // 删除记录mutation
  const deleteRecordMutation = trpc.purchase.deleteReviewRecord.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "记录已删除" : "Record deleted");
      refetchHistory();
      setDeletingRecord(null);
    },
    onError: (error) => toast.error(error.message),
  });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "teacher" && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  const handleReview = async (approved: boolean, reviewType: "teacher" | "lab" | "asset") => {
    if (!reviewingRequest) return;
    
    if (reviewType === "teacher") {
      await teacherReviewMutation.mutateAsync({
        requestId: reviewingRequest.id,
        approved,
        comment: reviewComment,
      });
    } else if (reviewType === "lab") {
      await labReviewMutation.mutateAsync({
        requestId: reviewingRequest.id,
        approved,
        comment: reviewComment,
      });
    } else if (reviewType === "asset") {
      await assetReviewMutation.mutateAsync({
        requestId: reviewingRequest.id,
        approved,
        comment: reviewComment,
      });
    }
  };

  const handleDeleteRecord = async () => {
    if (!deletingRecord) return;
    await deleteRecordMutation.mutateAsync({ requestId: deletingRecord.id });
  };

  // 检查是否有删除权限（仅限实验室管理员和资产分管领导）
  const canDeleteRecords = isLabAdmin || isAssetLeader;

  const labAdminRole = mySpecialRoles?.find(r => r.roleType === "lab_admin");

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/teacher")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold">{language === "zh" ? "采购申请审核" : "Purchase Request Review"}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-6">
        {/* 待审核/审核记录切换 */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-md">
            <TabsTrigger value="pending" className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              {language === "zh" ? "待审核" : "Pending"}
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="w-4 h-4" />
              {language === "zh" ? "审核记录" : "Review History"}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="space-y-6 mt-6">
        {/* 特殊角色提示 */}
        {(isLabAdmin || isAssetLeader) && (
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="py-4">
              <div className="flex items-center gap-2 text-blue-800">
                <AlertCircle className="w-5 h-5" />
                <span>
                  {language === "zh" ? "您当前的特殊角色：" : "Your special roles: "}
                  {isLabAdmin && <Badge className="ml-2 bg-blue-600">{language === "zh" ? "实验室管理员" : "Lab Admin"}</Badge>}
                  {isAssetLeader && <Badge className="ml-2 bg-purple-600">{language === "zh" ? "资产分管领导" : "Asset Leader"}</Badge>}
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 实验室管理员微信信息配置 */}
        {isLabAdmin && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                {language === "zh" ? "微信联系方式配置" : "WeChat Contact Settings"}
              </CardTitle>
              <CardDescription>
                {language === "zh" ? "学生审核通过后将看到此微信信息" : "Students will see this WeChat info after approval"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {editingWechat ? (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "微信号" : "WeChat ID"}</Label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border rounded-md"
                      value={newWechatId}
                      onChange={(e) => setNewWechatId(e.target.value)}
                      placeholder={language === "zh" ? "请输入微信号" : "Enter WeChat ID"}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "备注说明" : "Note"}</Label>
                    <Textarea
                      value={newWechatNote}
                      onChange={(e) => setNewWechatNote(e.target.value)}
                      placeholder={language === "zh" ? "请输入备注说明" : "Enter note"}
                      rows={2}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={async () => {
                        await updateWechatMutation.mutateAsync({
                          wechatId: newWechatId,
                          wechatNote: newWechatNote,
                        });
                        setEditingWechat(false);
                      }}
                      disabled={updateWechatMutation.isPending}
                    >
                      {updateWechatMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                      {language === "zh" ? "保存" : "Save"}
                    </Button>
                    <Button variant="outline" onClick={() => setEditingWechat(false)}>
                      {language === "zh" ? "取消" : "Cancel"}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  {wechatInfo ? (
                    <>
                      <p><strong>{language === "zh" ? "微信号" : "WeChat ID"}:</strong> {wechatInfo.wechatId}</p>
                      {wechatInfo.wechatNote && <p><strong>{language === "zh" ? "备注" : "Note"}:</strong> {wechatInfo.wechatNote}</p>}
                    </>
                  ) : (
                    <p className="text-gray-500">{language === "zh" ? "尚未配置微信信息" : "WeChat info not configured"}</p>
                  )}
                  <Button
                    variant="outline"
                    onClick={() => {
                      setNewWechatId(wechatInfo?.wechatId || "");
                      setNewWechatNote(wechatInfo?.wechatNote || "");
                      setEditingWechat(true);
                    }}
                  >
                    {language === "zh" ? "编辑" : "Edit"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* 实验室管理员待审核 */}
        {isLabAdmin && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {language === "zh" ? "实验室管理员待审核" : "Lab Admin Pending Review"}
                {pendingLabRequests && pendingLabRequests.length > 0 && (
                  <Badge variant="destructive">{pendingLabRequests.length}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!pendingLabRequests || pendingLabRequests.length === 0 ? (
                <p className="text-gray-500 text-center py-4">{language === "zh" ? "暂无待审核申请" : "No pending requests"}</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                      <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                      <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                      <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                      <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingLabRequests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>{request.studentName}</TableCell>
                        <TableCell>{request.studentClass}</TableCell>
                        <TableCell className="font-medium">¥{request.totalAmount}</TableCell>
                        <TableCell>{new Date(request.applyTime).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setSelectedRequest(request)}
                            >
                              {language === "zh" ? "查看" : "View"}
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => {
                                setReviewingRequest({ ...request, reviewType: "lab" });
                                setReviewAction("approve");
                              }}
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              {language === "zh" ? "通过" : "Approve"}
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => {
                                setReviewingRequest({ ...request, reviewType: "lab" });
                                setReviewAction("reject");
                              }}
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              {language === "zh" ? "拒绝" : "Reject"}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        )}

        {/* 资产分管领导待审核 */}
        {isAssetLeader && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {language === "zh" ? "资产分管领导待审核" : "Asset Leader Pending Review"}
                {pendingAssetRequests && pendingAssetRequests.length > 0 && (
                  <Badge variant="destructive">{pendingAssetRequests.length}</Badge>
                )}
              </CardTitle>
              <CardDescription>
                {language === "zh" ? "超过1500元的采购申请需要您审核" : "Purchase requests over 1500 CNY require your approval"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!pendingAssetRequests || pendingAssetRequests.length === 0 ? (
                <p className="text-gray-500 text-center py-4">{language === "zh" ? "暂无待审核申请" : "No pending requests"}</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                      <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                      <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                      <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                      <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingAssetRequests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>{request.studentName}</TableCell>
                        <TableCell>{request.studentClass}</TableCell>
                        <TableCell className="font-medium text-orange-600">¥{request.totalAmount}</TableCell>
                        <TableCell>{new Date(request.applyTime).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setSelectedRequest(request)}
                            >
                              {language === "zh" ? "查看" : "View"}
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => {
                                setReviewingRequest({ ...request, reviewType: "asset" });
                                setReviewAction("approve");
                              }}
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              {language === "zh" ? "通过" : "Approve"}
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => {
                                setReviewingRequest({ ...request, reviewType: "asset" });
                                setReviewAction("reject");
                              }}
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              {language === "zh" ? "拒绝" : "Reject"}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        )}

        {/* 导师待审核 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              {language === "zh" ? "导师待审核" : "Supervisor Pending Review"}
              {pendingRequests && pendingRequests.length > 0 && (
                <Badge variant="destructive">{pendingRequests.length}</Badge>
              )}
            </CardTitle>
            <CardDescription>
              {language === "zh" ? "您指导学生的采购申请" : "Purchase requests from your students"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!pendingRequests || pendingRequests.length === 0 ? (
              <p className="text-gray-500 text-center py-4">{language === "zh" ? "暂无待审核申请" : "No pending requests"}</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                    <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                    <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                    <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                    <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingRequests.map((request) => (
                    <TableRow key={request.id}>
                      <TableCell>{request.studentName}</TableCell>
                      <TableCell>{request.studentClass}</TableCell>
                      <TableCell className="font-medium">
                        ¥{request.totalAmount}
                        {request.isOverBudget === 1 && (
                          <Badge variant="outline" className="ml-2 text-orange-600 border-orange-600">
                            {language === "zh" ? "超额" : "Over Budget"}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>{new Date(request.applyTime).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedRequest(request)}
                          >
                            {language === "zh" ? "查看" : "View"}
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => {
                              setReviewingRequest({ ...request, reviewType: "teacher" });
                              setReviewAction("approve");
                            }}
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            {language === "zh" ? "通过" : "Approve"}
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => {
                              setReviewingRequest({ ...request, reviewType: "teacher" });
                              setReviewAction("reject");
                            }}
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            {language === "zh" ? "拒绝" : "Reject"}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* 申请详情对话框 */}
        <Dialog open={!!selectedRequest} onOpenChange={(open) => !open && setSelectedRequest(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{language === "zh" ? "采购申请详情" : "Purchase Request Details"}</DialogTitle>
            </DialogHeader>
            {selectedRequest && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>{language === "zh" ? "学生姓名" : "Student Name"}</Label>
                    <p className="mt-1">{selectedRequest.studentName}</p>
                  </div>
                  <div>
                    <Label>{language === "zh" ? "班级" : "Class"}</Label>
                    <p className="mt-1">{selectedRequest.studentClass}</p>
                  </div>
                  <div>
                    <Label>{language === "zh" ? "学号" : "Student ID"}</Label>
                    <p className="mt-1">{selectedRequest.studentNo}</p>
                  </div>
                  <div>
                    <Label>{language === "zh" ? "申请金额" : "Amount"}</Label>
                    <p className="mt-1 font-medium">¥{selectedRequest.totalAmount}</p>
                  </div>
                </div>
                <div>
                  <Label>{language === "zh" ? "申请理由" : "Reason"}</Label>
                  <p className="mt-1 whitespace-pre-wrap">{selectedRequest.reason || "-"}</p>
                </div>
                <div>
                  <Label>{language === "zh" ? "申请表文件" : "Application Form"}</Label>
                  <a
                    href={prefixFileUrl(selectedRequest.fileUrl)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-1 text-blue-600 hover:underline flex items-center gap-1"
                  >
                    <Download className="w-4 h-4" />
                    {selectedRequest.fileName || (language === "zh" ? "下载申请表" : "Download Form")}
                  </a>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
          </TabsContent>

          {/* 审核记录Tab */}
          <TabsContent value="history" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="w-5 h-5" />
                  {language === "zh" ? "审核记录" : "Review History"}
                </CardTitle>
                <CardDescription>
                  {language === "zh" ? "查看您指导学生的所有采购申请记录" : "View all purchase request records from your students"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* 筛选区域 */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
                  {/* 班级筛选 */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium">{language === "zh" ? "班级" : "Class"}</label>
                    <Select value={historyClassFilter || "__all__"} onValueChange={(v) => setHistoryClassFilter(v === "__all__" ? "" : v)}>
                      <SelectTrigger>
                        <SelectValue placeholder={language === "zh" ? "全部班级" : "All Classes"} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__all__">{language === "zh" ? "全部班级" : "All Classes"}</SelectItem>
                        {activeClasses?.map((cls) => (
                          <SelectItem key={cls} value={cls}>{cls}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  {/* 姓名筛选 */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium">{language === "zh" ? "姓名" : "Name"}</label>
                    <Input
                      placeholder={language === "zh" ? "输入姓名" : "Enter name"}
                      value={historyNameFilter}
                      onChange={(e) => setHistoryNameFilter(e.target.value)}
                    />
                  </div>
                  {/* 开始日期 */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium">{language === "zh" ? "开始日期" : "Start Date"}</label>
                    <Input
                      type="date"
                      value={historyStartDate}
                      onChange={(e) => setHistoryStartDate(e.target.value)}
                    />
                  </div>
                  {/* 结束日期 */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium">{language === "zh" ? "结束日期" : "End Date"}</label>
                    <Input
                      type="date"
                      value={historyEndDate}
                      onChange={(e) => setHistoryEndDate(e.target.value)}
                    />
                  </div>
                  {/* 审核结果 */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium">{language === "zh" ? "审核结果" : "Result"}</label>
                    <Select value={historyResultFilter} onValueChange={(v) => setHistoryResultFilter(v as any)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{language === "zh" ? "全部" : "All"}</SelectItem>
                        <SelectItem value="approved">{language === "zh" ? "通过" : "Approved"}</SelectItem>
                        <SelectItem value="rejected">{language === "zh" ? "未通过" : "Rejected"}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* 导出按钮 */}
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setHistoryClassFilter("");
                      setHistoryNameFilter("");
                      setHistoryStartDate("");
                      setHistoryEndDate("");
                      setHistoryResultFilter("all");
                    }}
                  >
                    {language === "zh" ? "重置筛选" : "Reset Filters"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      if (!reviewHistory || reviewHistory.length === 0) {
                        toast.error(language === "zh" ? "没有可导出的记录" : "No records to export");
                        return;
                      }
                      // 导出CSV
                      const headers = [
                        language === "zh" ? "班级" : "Class",
                        language === "zh" ? "姓名" : "Name",
                        language === "zh" ? "学号" : "Student ID",
                        language === "zh" ? "金额(元)" : "Amount(CNY)",
                        language === "zh" ? "申请时间" : "Apply Time",
                        language === "zh" ? "通过时间" : "Approved Time",
                        language === "zh" ? "审核状态" : "Status",
                      ];
                      const rows = reviewHistory.map((r) => [
                        r.studentClass,
                        r.studentName,
                        r.studentNo,
                        r.totalAmount,
                        new Date(r.applyTime).toLocaleString(),
                        r.approvedTime ? new Date(r.approvedTime).toLocaleString() : "-",
                        language === "zh" ? r.displayStatus : r.displayStatusEn,
                      ]);
                      const csvContent = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
                      const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `purchase_review_history_${new Date().toISOString().slice(0, 10)}.csv`;
                      a.click();
                      URL.revokeObjectURL(url);
                      toast.success(language === "zh" ? "导出成功" : "Export successful");
                    }}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {language === "zh" ? "导出记录" : "Export Records"}
                  </Button>
                </div>

                {/* 记录表格 */}
                {!reviewHistory || reviewHistory.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    {language === "zh" ? "暂无审核记录" : "No review records"}
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                        <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                        <TableHead>{language === "zh" ? "学号" : "Student ID"}</TableHead>
                        <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                        <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                        <TableHead>{language === "zh" ? "通过时间" : "Approved Time"}</TableHead>
                        <TableHead>{language === "zh" ? "审核状态" : "Status"}</TableHead>
                        <TableHead>{language === "zh" ? "申请表" : "File"}</TableHead>
                        {canDeleteRecords && (
                          <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                        )}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {reviewHistory.map((record) => (
                        <TableRow key={record.id}>
                          <TableCell>{record.studentClass}</TableCell>
                          <TableCell>{record.studentName}</TableCell>
                          <TableCell>{record.studentNo}</TableCell>
                          <TableCell className="font-medium">¥{record.totalAmount}</TableCell>
                          <TableCell>{new Date(record.applyTime).toLocaleDateString()}</TableCell>
                          <TableCell>
                            {record.approvedTime 
                              ? new Date(record.approvedTime).toLocaleDateString() 
                              : "-"}
                          </TableCell>
                          <TableCell>
                            <Badge className={statusMap[record.status]?.color || "bg-gray-100"}>
                              {language === "zh" ? record.displayStatus : record.displayStatusEn}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <a 
                              href={prefixFileUrl(record.fileUrl)} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="text-blue-600 hover:underline flex items-center gap-1"
                            >
                              <Download className="w-4 h-4" />
                              {language === "zh" ? "下载" : "Download"}
                            </a>
                          </TableCell>
                          {canDeleteRecords && (
                            <TableCell>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => setDeletingRecord(record)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </TableCell>
                          )}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* 审核对话框 */}
        <Dialog open={!!reviewingRequest} onOpenChange={(open) => !open && setReviewingRequest(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {reviewAction === "approve" 
                  ? (language === "zh" ? "确认通过" : "Confirm Approval")
                  : (language === "zh" ? "确认拒绝" : "Confirm Rejection")}
              </DialogTitle>
              <DialogDescription>
                {reviewingRequest && (
                  <span>
                    {language === "zh" ? "学生" : "Student"}: {reviewingRequest.studentName} | 
                    {language === "zh" ? "金额" : "Amount"}: ¥{reviewingRequest.totalAmount}
                  </span>
                )}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              {reviewingRequest?.isOverBudget === 1 && reviewAction === "approve" && reviewingRequest?.reviewType === "teacher" && (
                <div className="p-3 bg-orange-50 rounded-lg text-orange-800 text-sm flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {language === "zh" 
                    ? "该申请超过1500元，通过后将进入资产分管领导审核环节" 
                    : "This request exceeds 1500 CNY and will require asset leader approval"}
                </div>
              )}
              <div className="space-y-2">
                <Label>{language === "zh" ? "审核意见（选填）" : "Comment (Optional)"}</Label>
                <Textarea
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder={language === "zh" ? "请输入审核意见" : "Enter comment"}
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setReviewingRequest(null)}>
                {language === "zh" ? "取消" : "Cancel"}
              </Button>
              <Button
                variant={reviewAction === "approve" ? "default" : "destructive"}
                onClick={() => handleReview(reviewAction === "approve", reviewingRequest?.reviewType)}
                disabled={teacherReviewMutation.isPending || labReviewMutation.isPending || assetReviewMutation.isPending}
              >
                {(teacherReviewMutation.isPending || labReviewMutation.isPending || assetReviewMutation.isPending) && (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                )}
                {reviewAction === "approve" 
                  ? (language === "zh" ? "通过" : "Approve")
                  : (language === "zh" ? "拒绝" : "Reject")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* 删除确认对话框 */}
        <Dialog open={!!deletingRecord} onOpenChange={(open) => !open && setDeletingRecord(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="text-red-600">
                {language === "zh" ? "确认删除记录" : "Confirm Delete Record"}
              </DialogTitle>
              <DialogDescription>
                {deletingRecord && (
                  <span>
                    {language === "zh" ? "确定要删除以下记录吗？此操作不可撤销。" : "Are you sure you want to delete this record? This action cannot be undone."}
                  </span>
                )}
              </DialogDescription>
            </DialogHeader>
            {deletingRecord && (
              <div className="space-y-2 py-4">
                <p><strong>{language === "zh" ? "学生" : "Student"}:</strong> {deletingRecord.studentName}</p>
                <p><strong>{language === "zh" ? "学号" : "Student ID"}:</strong> {deletingRecord.studentNo}</p>
                <p><strong>{language === "zh" ? "班级" : "Class"}:</strong> {deletingRecord.studentClass}</p>
                <p><strong>{language === "zh" ? "金额" : "Amount"}:</strong> ¥{deletingRecord.totalAmount}</p>
                <p><strong>{language === "zh" ? "申请时间" : "Apply Time"}:</strong> {new Date(deletingRecord.applyTime).toLocaleDateString()}</p>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeletingRecord(null)}>
                {language === "zh" ? "取消" : "Cancel"}
              </Button>
              <Button
                variant="destructive"
                onClick={handleDeleteRecord}
                disabled={deleteRecordMutation.isPending}
              >
                {deleteRecordMutation.isPending && (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                )}
                {language === "zh" ? "确认删除" : "Delete"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
