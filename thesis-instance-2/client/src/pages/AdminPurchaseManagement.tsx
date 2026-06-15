import { useAuth } from "@/_core/hooks/useAuth";
import { prefixFileUrl } from "@/lib/basePath";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, UserPlus, UserMinus, FileText, CheckCircle, XCircle, Clock, MessageSquare, Loader2, Search, AlertCircle } from "lucide-react";
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

export default function AdminPurchaseManagement() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [, setLocation] = useLocation();

  // 角色任命相关状态
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [wechatId, setWechatId] = useState("");
  const [wechatNote, setWechatNote] = useState("");
  const [appointingRole, setAppointingRole] = useState<"lab_admin" | "asset_leader" | null>(null);

  // 审核相关状态
  const [reviewComment, setReviewComment] = useState("");
  const [reviewingRequest, setReviewingRequest] = useState<any>(null);
  const [reviewAction, setReviewAction] = useState<"approve" | "reject" | null>(null);

  // 筛选状态
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // 查询
  const { data: allUsers } = trpc.admin.getUsers.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: labAdmins, refetch: refetchLabAdmins } = trpc.purchase.getSpecialRoles.useQuery({ roleType: "lab_admin" }, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: assetLeaders, refetch: refetchAssetLeaders } = trpc.purchase.getSpecialRoles.useQuery({ roleType: "asset_leader" }, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: pendingLabRequests, refetch: refetchLabRequests } = trpc.purchase.getPendingLabReview.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: pendingAssetRequests, refetch: refetchAssetRequests } = trpc.purchase.getPendingAssetReview.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  const { data: allRequests, refetch: refetchAllRequests } = trpc.purchase.getAllRequests.useQuery(
    statusFilter === "all" ? {} : { status: statusFilter },
    { enabled: isAuthenticated && user?.role === "admin" }
  );
  const { data: wechatInfo, refetch: refetchWechat } = trpc.purchase.getLabAdminWechat.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });

  // Mutations
  const appointMutation = trpc.purchase.appointRole.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "任命成功" : "Appointment successful");
      refetchLabAdmins();
      refetchAssetLeaders();
      setAppointingRole(null);
      setSelectedUserId("");
      setWechatId("");
      setWechatNote("");
    },
    onError: (error) => toast.error(error.message),
  });

  const revokeMutation = trpc.purchase.revokeRole.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "撤销成功" : "Revocation successful");
      refetchLabAdmins();
      refetchAssetLeaders();
    },
    onError: (error) => toast.error(error.message),
  });

  const labReviewMutation = trpc.purchase.labReview.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "审核完成" : "Review completed");
      refetchLabRequests();
      refetchAllRequests();
      setReviewingRequest(null);
      setReviewComment("");
    },
    onError: (error) => toast.error(error.message),
  });

  const assetReviewMutation = trpc.purchase.assetReview.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "审核完成" : "Review completed");
      refetchAssetRequests();
      refetchAllRequests();
      setReviewingRequest(null);
      setReviewComment("");
    },
    onError: (error) => toast.error(error.message),
  });

  const updateWechatMutation = trpc.purchase.updateLabAdminWechat.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "微信信息更新成功" : "WeChat info updated");
      refetchWechat();
      refetchLabAdmins();
    },
    onError: (error) => toast.error(error.message),
  });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  // 可任命的用户（导师和管理员）
  const appointableUsers = allUsers?.filter(u => u.role === "teacher" || u.role === "admin") || [];

  const handleAppoint = async () => {
    if (!selectedUserId || !appointingRole) return;
    await appointMutation.mutateAsync({
      userId: parseInt(selectedUserId),
      roleType: appointingRole,
      wechatId: appointingRole === "lab_admin" ? wechatId : undefined,
      wechatNote: appointingRole === "lab_admin" ? wechatNote : undefined,
    });
  };

  const handleReview = async (approved: boolean) => {
    if (!reviewingRequest) return;
    
    if (reviewingRequest.status === "pending_lab") {
      await labReviewMutation.mutateAsync({
        requestId: reviewingRequest.id,
        approved,
        comment: reviewComment,
      });
    } else if (reviewingRequest.status === "pending_asset") {
      await assetReviewMutation.mutateAsync({
        requestId: reviewingRequest.id,
        approved,
        comment: reviewComment,
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/admin")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold">{language === "zh" ? "采购审核管理" : "Purchase Review Management"}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="roles" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="roles">{language === "zh" ? "角色任命" : "Role Assignment"}</TabsTrigger>
            <TabsTrigger value="lab-review">
              {language === "zh" ? "实验室审核" : "Lab Review"}
              {pendingLabRequests && pendingLabRequests.length > 0 && (
                <Badge className="ml-2 bg-red-500">{pendingLabRequests.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="asset-review">
              {language === "zh" ? "资产审核" : "Asset Review"}
              {pendingAssetRequests && pendingAssetRequests.length > 0 && (
                <Badge className="ml-2 bg-red-500">{pendingAssetRequests.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="all-requests">{language === "zh" ? "全部申请" : "All Requests"}</TabsTrigger>
          </TabsList>

          {/* 角色任命 Tab */}
          <TabsContent value="roles" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* 实验室管理员 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserPlus className="w-5 h-5" />
                    {language === "zh" ? "实验室管理员" : "Lab Admin"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" ? "负责初步审核学生的采购申请" : "Responsible for initial review of purchase requests"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 当前任命列表 */}
                  {labAdmins && labAdmins.length > 0 ? (
                    <div className="space-y-2">
                      {labAdmins.map((admin) => (
                        <div key={admin.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{admin.userName}</p>
                            <p className="text-sm text-gray-500">{admin.userEmail}</p>
                            {admin.wechatId && (
                              <p className="text-sm text-blue-600 flex items-center gap-1">
                                <MessageSquare className="w-3 h-3" />
                                {admin.wechatId}
                              </p>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600"
                            onClick={() => revokeMutation.mutate({ userId: admin.userId, roleType: "lab_admin" })}
                          >
                            <UserMinus className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      {language === "zh" ? "暂无实验室管理员" : "No lab admin assigned"}
                    </p>
                  )}

                  {/* 任命按钮 */}
                  <Dialog open={appointingRole === "lab_admin"} onOpenChange={(open) => !open && setAppointingRole(null)}>
                    <DialogTrigger asChild>
                      <Button className="w-full" onClick={() => setAppointingRole("lab_admin")}>
                        <UserPlus className="w-4 h-4 mr-2" />
                        {language === "zh" ? "任命实验室管理员" : "Appoint Lab Admin"}
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>{language === "zh" ? "任命实验室管理员" : "Appoint Lab Admin"}</DialogTitle>
                        <DialogDescription>
                          {language === "zh" ? "选择用户并填写微信联系方式" : "Select user and fill in WeChat contact"}
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label>{language === "zh" ? "选择用户" : "Select User"}</Label>
                          <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                            <SelectTrigger>
                              <SelectValue placeholder={language === "zh" ? "请选择用户" : "Select user"} />
                            </SelectTrigger>
                            <SelectContent>
                              {appointableUsers.map((u) => (
                                <SelectItem key={u.id} value={u.id.toString()}>
                                  {u.name} ({u.email})
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>{language === "zh" ? "微信号" : "WeChat ID"}</Label>
                          <Input
                            value={wechatId}
                            onChange={(e) => setWechatId(e.target.value)}
                            placeholder={language === "zh" ? "请输入微信号" : "Enter WeChat ID"}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>{language === "zh" ? "备注说明" : "Note"}</Label>
                          <Textarea
                            value={wechatNote}
                            onChange={(e) => setWechatNote(e.target.value)}
                            placeholder={language === "zh" ? "请输入备注说明" : "Enter note"}
                            rows={2}
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setAppointingRole(null)}>
                          {language === "zh" ? "取消" : "Cancel"}
                        </Button>
                        <Button onClick={handleAppoint} disabled={!selectedUserId || appointMutation.isPending}>
                          {appointMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                          {language === "zh" ? "确认任命" : "Confirm"}
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>

                  {/* 微信信息配置 */}
                  {wechatInfo && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-blue-800 mb-2">
                        {language === "zh" ? "当前微信联系方式" : "Current WeChat Contact"}
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
                </CardContent>
              </Card>

              {/* 资产分管领导 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserPlus className="w-5 h-5" />
                    {language === "zh" ? "资产分管领导" : "Asset Leader"}
                  </CardTitle>
                  <CardDescription>
                    {language === "zh" ? "负责审核超过1500元的采购申请" : "Responsible for reviewing requests over 1500 CNY"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 当前任命列表 */}
                  {assetLeaders && assetLeaders.length > 0 ? (
                    <div className="space-y-2">
                      {assetLeaders.map((leader) => (
                        <div key={leader.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{leader.userName}</p>
                            <p className="text-sm text-gray-500">{leader.userEmail}</p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600"
                            onClick={() => revokeMutation.mutate({ userId: leader.userId, roleType: "asset_leader" })}
                          >
                            <UserMinus className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      {language === "zh" ? "暂无资产分管领导" : "No asset leader assigned"}
                    </p>
                  )}

                  {/* 任命按钮 */}
                  <Dialog open={appointingRole === "asset_leader"} onOpenChange={(open) => !open && setAppointingRole(null)}>
                    <DialogTrigger asChild>
                      <Button className="w-full" onClick={() => setAppointingRole("asset_leader")}>
                        <UserPlus className="w-4 h-4 mr-2" />
                        {language === "zh" ? "任命资产分管领导" : "Appoint Asset Leader"}
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>{language === "zh" ? "任命资产分管领导" : "Appoint Asset Leader"}</DialogTitle>
                        <DialogDescription>
                          {language === "zh" ? "选择用户进行任命" : "Select user to appoint"}
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label>{language === "zh" ? "选择用户" : "Select User"}</Label>
                          <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                            <SelectTrigger>
                              <SelectValue placeholder={language === "zh" ? "请选择用户" : "Select user"} />
                            </SelectTrigger>
                            <SelectContent>
                              {appointableUsers.map((u) => (
                                <SelectItem key={u.id} value={u.id.toString()}>
                                  {u.name} ({u.email})
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setAppointingRole(null)}>
                          {language === "zh" ? "取消" : "Cancel"}
                        </Button>
                        <Button onClick={handleAppoint} disabled={!selectedUserId || appointMutation.isPending}>
                          {appointMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                          {language === "zh" ? "确认任命" : "Confirm"}
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 实验室审核 Tab */}
          <TabsContent value="lab-review">
            <Card>
              <CardHeader>
                <CardTitle>{language === "zh" ? "待实验室管理员审核" : "Pending Lab Admin Review"}</CardTitle>
                <CardDescription>
                  {language === "zh" ? "作为管理员，您可以代为审核" : "As admin, you can review on behalf"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!pendingLabRequests || pendingLabRequests.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    {language === "zh" ? "暂无待审核申请" : "No pending requests"}
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                        <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                        <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                        <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                        <TableHead>{language === "zh" ? "文件" : "File"}</TableHead>
                        <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {pendingLabRequests.map((request) => (
                        <TableRow key={request.id}>
                          <TableCell>{new Date(request.applyTime).toLocaleDateString()}</TableCell>
                          <TableCell>{request.studentName}</TableCell>
                          <TableCell>{request.studentClass}</TableCell>
                          <TableCell>
                            ¥{request.totalAmount}
                            {request.isOverBudget === 1 && (
                              <Badge className="ml-2 bg-orange-100 text-orange-800">
                                {language === "zh" ? "超额" : "Over"}
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <a href={prefixFileUrl(request.fileUrl)} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {language === "zh" ? "查看" : "View"}
                            </a>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600"
                                onClick={() => {
                                  setReviewingRequest(request);
                                  setReviewAction("approve");
                                }}
                              >
                                <CheckCircle className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-red-600"
                                onClick={() => {
                                  setReviewingRequest(request);
                                  setReviewAction("reject");
                                }}
                              >
                                <XCircle className="w-4 h-4" />
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
          </TabsContent>

          {/* 资产审核 Tab */}
          <TabsContent value="asset-review">
            <Card>
              <CardHeader>
                <CardTitle>{language === "zh" ? "待资产分管领导审核" : "Pending Asset Leader Review"}</CardTitle>
                <CardDescription>
                  {language === "zh" ? "超过1500元的申请需要额外审批" : "Requests over 1500 CNY require additional approval"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!pendingAssetRequests || pendingAssetRequests.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    {language === "zh" ? "暂无待审核申请" : "No pending requests"}
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                        <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                        <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                        <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                        <TableHead>{language === "zh" ? "文件" : "File"}</TableHead>
                        <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {pendingAssetRequests.map((request) => (
                        <TableRow key={request.id}>
                          <TableCell>{new Date(request.applyTime).toLocaleDateString()}</TableCell>
                          <TableCell>{request.studentName}</TableCell>
                          <TableCell>{request.studentClass}</TableCell>
                          <TableCell className="text-orange-600 font-medium">¥{request.totalAmount}</TableCell>
                          <TableCell>
                            <a href={prefixFileUrl(request.fileUrl)} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {language === "zh" ? "查看" : "View"}
                            </a>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600"
                                onClick={() => {
                                  setReviewingRequest(request);
                                  setReviewAction("approve");
                                }}
                              >
                                <CheckCircle className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-red-600"
                                onClick={() => {
                                  setReviewingRequest(request);
                                  setReviewAction("reject");
                                }}
                              >
                                <XCircle className="w-4 h-4" />
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
          </TabsContent>

          {/* 全部申请 Tab */}
          <TabsContent value="all-requests">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{language === "zh" ? "全部采购申请" : "All Purchase Requests"}</CardTitle>
                    <CardDescription>
                      {language === "zh" ? "查看所有学生的采购申请记录" : "View all student purchase requests"}
                    </CardDescription>
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{language === "zh" ? "全部状态" : "All Status"}</SelectItem>
                      <SelectItem value="pending_lab">{language === "zh" ? "待实验室审核" : "Pending Lab"}</SelectItem>
                      <SelectItem value="pending_teacher">{language === "zh" ? "待导师审核" : "Pending Teacher"}</SelectItem>
                      <SelectItem value="pending_asset">{language === "zh" ? "待资产审核" : "Pending Asset"}</SelectItem>
                      <SelectItem value="approved">{language === "zh" ? "已通过" : "Approved"}</SelectItem>
                      <SelectItem value="rejected_lab">{language === "zh" ? "实验室拒绝" : "Rejected by Lab"}</SelectItem>
                      <SelectItem value="rejected_teacher">{language === "zh" ? "导师拒绝" : "Rejected by Teacher"}</SelectItem>
                      <SelectItem value="rejected_asset">{language === "zh" ? "资产拒绝" : "Rejected by Asset"}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                {!allRequests || allRequests.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    {language === "zh" ? "暂无申请记录" : "No requests found"}
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{language === "zh" ? "申请时间" : "Apply Time"}</TableHead>
                        <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                        <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                        <TableHead>{language === "zh" ? "金额" : "Amount"}</TableHead>
                        <TableHead>{language === "zh" ? "状态" : "Status"}</TableHead>
                        <TableHead>{language === "zh" ? "文件" : "File"}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {allRequests.map((request) => {
                        const status = statusMap[request.status] || statusMap.pending_lab;
                        return (
                          <TableRow key={request.id}>
                            <TableCell>{new Date(request.applyTime).toLocaleDateString()}</TableCell>
                            <TableCell>{request.studentName}</TableCell>
                            <TableCell>{request.studentClass}</TableCell>
                            <TableCell>
                              ¥{request.totalAmount}
                              {request.isOverBudget === 1 && (
                                <Badge className="ml-2 bg-orange-100 text-orange-800">
                                  {language === "zh" ? "超额" : "Over"}
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              <Badge className={status.color}>
                                {language === "zh" ? status.label : status.labelEn}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <a href={prefixFileUrl(request.fileUrl)} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                                <FileText className="w-4 h-4" />
                                {language === "zh" ? "查看" : "View"}
                              </a>
                            </TableCell>
                          </TableRow>
                        );
                      })}
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
                onClick={() => handleReview(reviewAction === "approve")}
                disabled={labReviewMutation.isPending || assetReviewMutation.isPending}
              >
                {(labReviewMutation.isPending || assetReviewMutation.isPending) && (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                )}
                {reviewAction === "approve" 
                  ? (language === "zh" ? "通过" : "Approve")
                  : (language === "zh" ? "拒绝" : "Reject")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
}
