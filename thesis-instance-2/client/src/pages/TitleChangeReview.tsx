import { useState } from "react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, FileEdit, Clock, CheckCircle, XCircle, Check, X, User } from "lucide-react";

export default function TitleChangeReview() {
  const [, setLocation] = useLocation();
  const { language, setLanguage, t } = useLanguage();
  const [showReviewDialog, setShowReviewDialog] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<any>(null);
  const [reviewComment, setReviewComment] = useState("");
  const [isApproving, setIsApproving] = useState(true);

  // 获取待审核的题目修改申请
  const { data: pendingRequests, isLoading: pendingLoading, refetch: refetchPending } = trpc.titleChange.getPendingRequests.useQuery();
  
  // 获取所有题目修改申请（包括已处理的）
  const { data: allRequests, isLoading: allLoading, refetch: refetchAll } = trpc.titleChange.getAllRequests.useQuery();

  // 审核题目修改申请
  const reviewMutation = trpc.titleChange.review.useMutation({
    onSuccess: () => {
      toast.success(isApproving 
        ? (language === "zh" ? "已通过题目修改申请" : "Title change request approved")
        : (language === "zh" ? "已拒绝题目修改申请" : "Title change request rejected"));
      setShowReviewDialog(false);
      setReviewComment("");
      refetchPending();
      refetchAll();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleOpenReviewDialog = (request: any, approve: boolean) => {
    setSelectedRequest(request);
    setIsApproving(approve);
    setReviewComment("");
    setShowReviewDialog(true);
  };

  const handleReview = () => {
    if (!selectedRequest) return;
    reviewMutation.mutate({
      requestId: selectedRequest.id,
      approved: isApproving,
      reviewComment: reviewComment.trim() || undefined,
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200"><Clock className="w-3 h-3 mr-1" />{language === "zh" ? "待审核" : "Pending"}</Badge>;
      case "approved":
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200"><CheckCircle className="w-3 h-3 mr-1" />{language === "zh" ? "已通过" : "Approved"}</Badge>;
      case "rejected":
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200"><XCircle className="w-3 h-3 mr-1" />{language === "zh" ? "已拒绝" : "Rejected"}</Badge>;
      default:
        return null;
    }
  };

  const RequestCard = ({ request, showActions = false }: { request: any; showActions?: boolean }) => (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-gray-400" />
          <span className="font-medium">{request.studentName}</span>
          <span className="text-sm text-gray-500">
            ({request.chineseStudentId || "-"} / {request.englishStudentId || "-"})
          </span>
        </div>
        {getStatusBadge(request.status)}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-500">{language === "zh" ? "原题目" : "Original Title"}</p>
          <p className="font-medium text-gray-700">{request.originalTitle}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">{language === "zh" ? "新题目" : "New Title"}</p>
          <p className="font-medium text-blue-600">{request.newTitle}</p>
        </div>
      </div>
      {request.reason && (
        <div>
          <p className="text-sm text-gray-500">{language === "zh" ? "修改原因" : "Reason"}</p>
          <p className="text-gray-700">{request.reason}</p>
        </div>
      )}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{language === "zh" ? "申请时间" : "Submitted"}: {new Date(request.createdAt).toLocaleString()}</span>
        {request.reviewedAt && (
          <span>{language === "zh" ? "审核时间" : "Reviewed"}: {new Date(request.reviewedAt).toLocaleString()}</span>
        )}
      </div>
      {request.reviewComment && (
        <div className="bg-gray-50 rounded p-3">
          <p className="text-sm text-gray-500">{language === "zh" ? "审核意见" : "Review Comment"}</p>
          <p className="text-gray-700">{request.reviewComment}</p>
        </div>
      )}
      {showActions && request.status === "pending" && (
        <div className="flex justify-end gap-2 pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={() => handleOpenReviewDialog(request, false)}
          >
            <X className="w-4 h-4 mr-1" />
            {language === "zh" ? "拒绝" : "Reject"}
          </Button>
          <Button
            size="sm"
            className="bg-green-600 hover:bg-green-700"
            onClick={() => handleOpenReviewDialog(request, true)}
          >
            <Check className="w-4 h-4 mr-1" />
            {language === "zh" ? "通过" : "Approve"}
          </Button>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")} className="flex items-center gap-2">
              <Globe className="w-4 h-4" />
              {language === "zh" ? "English" : "中文"}
            </Button>
            <Button variant="ghost" onClick={() => setLocation("/teacher")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              {language === "zh" ? "返回控制台" : "Back to Dashboard"}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Page Title */}
          <div className="flex items-center gap-3">
            <FileEdit className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {language === "zh" ? "题目修改审核" : "Title Change Review"}
              </h1>
              <p className="text-gray-500">
                {language === "zh" ? "审核学生的题目修改申请" : "Review student title change requests"}
              </p>
            </div>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="pending">
            <TabsList>
              <TabsTrigger value="pending" className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {language === "zh" ? "待审核" : "Pending"}
                {pendingRequests && pendingRequests.length > 0 && (
                  <Badge variant="destructive" className="ml-1">{pendingRequests.length}</Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="all">
                {language === "zh" ? "全部记录" : "All Records"}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="pending" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>{language === "zh" ? "待审核申请" : "Pending Requests"}</CardTitle>
                  <CardDescription>
                    {language === "zh" ? "以下是等待您审核的题目修改申请" : "The following requests are waiting for your review"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {pendingLoading ? (
                    <div className="text-center py-8 text-gray-500">
                      {language === "zh" ? "加载中..." : "Loading..."}
                    </div>
                  ) : pendingRequests && pendingRequests.length > 0 ? (
                    <div className="space-y-4">
                      {pendingRequests.map((request) => (
                        <RequestCard key={request.id} request={request} showActions />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-300" />
                      {language === "zh" ? "暂无待审核的申请" : "No pending requests"}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="all" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>{language === "zh" ? "全部申请记录" : "All Request Records"}</CardTitle>
                  <CardDescription>
                    {language === "zh" ? "查看所有题目修改申请的历史记录" : "View all title change request history"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {allLoading ? (
                    <div className="text-center py-8 text-gray-500">
                      {language === "zh" ? "加载中..." : "Loading..."}
                    </div>
                  ) : allRequests && allRequests.length > 0 ? (
                    <div className="space-y-4">
                      {allRequests.map((request) => (
                        <RequestCard key={request.id} request={request} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      {language === "zh" ? "暂无申请记录" : "No request records"}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      {/* Review Dialog */}
      <Dialog open={showReviewDialog} onOpenChange={setShowReviewDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {isApproving 
                ? (language === "zh" ? "确认通过申请" : "Confirm Approval")
                : (language === "zh" ? "确认拒绝申请" : "Confirm Rejection")}
            </DialogTitle>
            <DialogDescription>
              {isApproving 
                ? (language === "zh" ? "通过后，课题题目将更新为学生申请的新题目" : "After approval, the topic title will be updated to the new title")
                : (language === "zh" ? "请填写拒绝原因，以便学生了解" : "Please provide a reason for rejection")}
            </DialogDescription>
          </DialogHeader>
          {selectedRequest && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">{language === "zh" ? "学生" : "Student"}</p>
                  <p className="font-medium">{selectedRequest.studentName}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{language === "zh" ? "学号" : "Student ID"}</p>
                  <p className="font-medium">{selectedRequest.chineseStudentId || "-"}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">{language === "zh" ? "原题目" : "Original Title"}</p>
                <p className="p-2 bg-gray-50 rounded">{selectedRequest.originalTitle}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">{language === "zh" ? "新题目" : "New Title"}</p>
                <p className="p-2 bg-blue-50 rounded text-blue-700">{selectedRequest.newTitle}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  {language === "zh" ? "审核意见" : "Review Comment"} ({language === "zh" ? "选填" : "Optional"})
                </label>
                <Textarea
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder={isApproving 
                    ? (language === "zh" ? "可以添加一些建议或说明" : "You can add suggestions or notes")
                    : (language === "zh" ? "请说明拒绝的原因" : "Please explain the reason for rejection")}
                  className="mt-1"
                  rows={3}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReviewDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              onClick={handleReview} 
              disabled={reviewMutation.isPending}
              className={isApproving ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"}
            >
              {isApproving ? <Check className="w-4 h-4 mr-2" /> : <X className="w-4 h-4 mr-2" />}
              {reviewMutation.isPending 
                ? (language === "zh" ? "处理中..." : "Processing...") 
                : isApproving 
                  ? (language === "zh" ? "确认通过" : "Confirm Approval")
                  : (language === "zh" ? "确认拒绝" : "Confirm Rejection")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
