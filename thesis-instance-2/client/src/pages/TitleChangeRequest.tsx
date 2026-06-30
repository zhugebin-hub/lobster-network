import { useState } from "react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, FileEdit, Clock, CheckCircle, XCircle, Send, AlertCircle } from "lucide-react";

export default function TitleChangeRequest() {
  const [, setLocation] = useLocation();
  const { language, setLanguage, t } = useLanguage();
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [reason, setReason] = useState("");
  const [selectedMatchId, setSelectedMatchId] = useState<number | null>(null);
  const [currentTitle, setCurrentTitle] = useState("");

  // 获取学生的匹配结果
  const { data: matchResult, isLoading: matchLoading } = trpc.match.myMatch.useQuery();
  
  // 获取题目修改申请历史
  const { data: requests, isLoading: requestsLoading, refetch: refetchRequests } = trpc.titleChange.getMyRequests.useQuery();

  // 提交题目修改申请
  const submitMutation = trpc.titleChange.submit.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "申请已提交，请等待导师审核" : "Request submitted, waiting for supervisor review");
      setShowSubmitDialog(false);
      setNewTitle("");
      setReason("");
      refetchRequests();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleOpenSubmitDialog = (matchId: number, title: string) => {
    setSelectedMatchId(matchId);
    setCurrentTitle(title);
    setNewTitle(title);
    setShowSubmitDialog(true);
  };

  const handleSubmit = () => {
    if (!selectedMatchId || !newTitle.trim()) {
      toast.error(language === "zh" ? "请填写新题目" : "Please enter new title");
      return;
    }
    if (newTitle.trim() === currentTitle) {
      toast.error(language === "zh" ? "新题目与原题目相同" : "New title is the same as original");
      return;
    }
    submitMutation.mutate({
      matchId: selectedMatchId,
      newTitle: newTitle.trim(),
      reason: reason.trim() || undefined,
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

  // 检查是否有待处理的申请
  const hasPendingRequest = requests?.some(r => r.status === "pending");

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
            <Button variant="ghost" onClick={() => setLocation("/student")}>
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
                {language === "zh" ? "题目修改申请" : "Title Change Request"}
              </h1>
              <p className="text-gray-500">
                {language === "zh" ? "申请修改您的毕业设计题目" : "Request to change your graduation design title"}
              </p>
            </div>
          </div>

          {/* Current Match Info */}
          <Card>
            <CardHeader>
              <CardTitle>{language === "zh" ? "当前课题信息" : "Current Topic Information"}</CardTitle>
              <CardDescription>
                {language === "zh" ? "您当前匹配的课题信息" : "Your currently matched topic information"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {matchLoading ? (
                <div className="text-center py-8 text-gray-500">
                  {language === "zh" ? "加载中..." : "Loading..."}
                </div>
              ) : matchResult ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{language === "zh" ? "课题题目" : "Topic Title"}</p>
                      <p className="font-medium">{matchResult.topic?.titleEn || matchResult.topic?.title || "-"}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{language === "zh" ? "指导导师" : "Supervisor"}</p>
                      <p className="font-medium">{matchResult.teacher?.name || "-"}</p>
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <Button
                      onClick={() => handleOpenSubmitDialog(
                        matchResult.id,
                        matchResult.topic?.titleEn || matchResult.topic?.title || ""
                      )}
                      disabled={hasPendingRequest}
                    >
                      <FileEdit className="w-4 h-4 mr-2" />
                      {hasPendingRequest 
                        ? (language === "zh" ? "有待处理的申请" : "Pending Request Exists")
                        : (language === "zh" ? "申请修改题目" : "Request Title Change")}
                    </Button>
                  </div>
                  {hasPendingRequest && (
                    <div className="flex items-center gap-2 text-yellow-600 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      {language === "zh" ? "您有待处理的题目修改申请，请等待导师审核后再提交新申请" : "You have a pending request, please wait for supervisor review"}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {language === "zh" ? "暂无匹配结果" : "No match result yet"}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Request History */}
          <Card>
            <CardHeader>
              <CardTitle>{language === "zh" ? "申请历史" : "Request History"}</CardTitle>
              <CardDescription>
                {language === "zh" ? "您的题目修改申请记录" : "Your title change request records"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {requestsLoading ? (
                <div className="text-center py-8 text-gray-500">
                  {language === "zh" ? "加载中..." : "Loading..."}
                </div>
              ) : requests && requests.length > 0 ? (
                <div className="space-y-4">
                  {requests.map((request) => (
                    <div key={request.id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          {new Date(request.createdAt).toLocaleString()}
                        </span>
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
                      {request.reviewComment && (
                        <div className="bg-gray-50 rounded p-3">
                          <p className="text-sm text-gray-500">{language === "zh" ? "导师意见" : "Supervisor Comment"}</p>
                          <p className="text-gray-700">{request.reviewComment}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {language === "zh" ? "暂无申请记录" : "No request records"}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Submit Dialog */}
      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "申请修改题目" : "Request Title Change"}</DialogTitle>
            <DialogDescription>
              {language === "zh" ? "请填写新的题目和修改原因，提交后需等待导师审核" : "Please enter new title and reason, submission requires supervisor approval"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium text-gray-700">
                {language === "zh" ? "原题目" : "Original Title"}
              </label>
              <p className="mt-1 p-3 bg-gray-50 rounded-lg text-gray-600">{currentTitle}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">
                {language === "zh" ? "新题目" : "New Title"} <span className="text-red-500">*</span>
              </label>
              <Input
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder={language === "zh" ? "请输入新的题目" : "Enter new title"}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">
                {language === "zh" ? "修改原因" : "Reason"} ({language === "zh" ? "选填" : "Optional"})
              </label>
              <Textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder={language === "zh" ? "请说明修改题目的原因" : "Please explain the reason for title change"}
                className="mt-1"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubmitDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleSubmit} disabled={submitMutation.isPending}>
              <Send className="w-4 h-4 mr-2" />
              {submitMutation.isPending 
                ? (language === "zh" ? "提交中..." : "Submitting...") 
                : (language === "zh" ? "提交申请" : "Submit Request")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
