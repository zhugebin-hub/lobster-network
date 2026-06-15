import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, Plus, Calendar, Check, Trash2, Copy, Loader2, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";

export default function YearManagement() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [, setLocation] = useLocation();
  
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [copyDialogOpen, setCopyDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [yearToDelete, setYearToDelete] = useState<{ id: number; name: string } | null>(null);
  
  // 创建学年表单（简化版）
  const [newYearName, setNewYearName] = useState("");
  const [newDisplayName, setNewDisplayName] = useState("");
  const [chineseTeacherQuota, setChineseTeacherQuota] = useState(5);
  
  // 复制课题
  const [sourceYear, setSourceYear] = useState("");
  const [targetYear, setTargetYear] = useState("");

  const { data: years, refetch: refetchYears } = trpc.admin.getAllYears.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  
  const createYearMutation = trpc.admin.createYear.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "学年创建成功" : "Year created successfully");
      setCreateDialogOpen(false);
      refetchYears();
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message);
    }
  });
  
  const setCurrentYearMutation = trpc.admin.setCurrentYear.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "当前学年已切换" : "Current year switched");
      refetchYears();
    },
    onError: (error) => {
      toast.error(error.message);
    }
  });
  
  const deleteYearMutation = trpc.admin.deleteYear.useMutation({
    onSuccess: (data) => {
      const { deletedData } = data;
      toast.success(
        language === "zh" 
          ? `学年已删除，共删除：${deletedData.topics}个课题、${deletedData.wishes}条志愿、${deletedData.matches}条匹配、${deletedData.students}个学生账户` 
          : `Year deleted. Removed: ${deletedData.topics} topics, ${deletedData.wishes} wishes, ${deletedData.matches} matches, ${deletedData.students} students`
      );
      setDeleteDialogOpen(false);
      setYearToDelete(null);
      refetchYears();
    },
    onError: (error) => {
      toast.error(error.message);
    }
  });
  
  const copyTopicsMutation = trpc.admin.copyTopicsFromYear.useMutation({
    onSuccess: (data) => {
      toast.success(language === "zh" ? `已复制 ${data.copiedCount} 个课题` : `Copied ${data.copiedCount} topics`);
      setCopyDialogOpen(false);
    },
    onError: (error) => {
      toast.error(error.message);
    }
  });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const resetForm = () => {
    setNewYearName("");
    setNewDisplayName("");
    setChineseTeacherQuota(5);
  };

  const handleCreateYear = () => {
    if (!newYearName.trim()) {
      toast.error(language === "zh" ? "请输入学年名称" : "Please enter year name");
      return;
    }
    createYearMutation.mutate({
      yearName: newYearName.trim(),
      displayName: newDisplayName.trim() || newYearName.trim(),
      chineseTeacherQuota,
    });
  };

  const handleCopyTopics = () => {
    if (!sourceYear || !targetYear) {
      toast.error(language === "zh" ? "请选择源学年和目标学年" : "Please select source and target year");
      return;
    }
    copyTopicsMutation.mutate({ sourceYearName: sourceYear, targetYearName: targetYear });
  };

  const handleDeleteYear = () => {
    if (yearToDelete) {
      deleteYearMutation.mutate({ id: yearToDelete.id });
    }
  };

  const openDeleteDialog = (year: { id: number; yearName: string; displayName: string | null }) => {
    setYearToDelete({ id: year.id, name: year.displayName || year.yearName });
    setDeleteDialogOpen(true);
  };

  const getStatusBadge = (status: string, isCurrentYear: boolean) => {
    if (isCurrentYear) {
      return <Badge className="bg-green-500">{language === "zh" ? "当前活跃" : "Active"}</Badge>;
    }
    switch (status) {
      case "draft":
        return <Badge variant="secondary">{language === "zh" ? "草稿" : "Draft"}</Badge>;
      case "active":
        return <Badge className="bg-blue-500">{language === "zh" ? "进行中" : "In Progress"}</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => setLocation("/admin")}><ArrowLeft className="w-4 h-4 mr-2" />{language === "zh" ? "返回" : "Back"}</Button>
          <h1 className="text-xl font-semibold">{language === "zh" ? "年度管理" : "Year Management"}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <p className="text-gray-600">{language === "zh" ? "管理学年配置，时间配置请在系统配置中设置" : "Manage academic years, time settings in System Config"}</p>
          <div className="flex gap-2">
            <Dialog open={copyDialogOpen} onOpenChange={setCopyDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline"><Copy className="w-4 h-4 mr-2" />{language === "zh" ? "复制课题" : "Copy Topics"}</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{language === "zh" ? "从历史学年复制课题" : "Copy Topics from History"}</DialogTitle>
                  <DialogDescription>{language === "zh" ? "将历史学年的课题模板复制到新学年" : "Copy topic templates from a previous year"}</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "源学年" : "Source Year"}</Label>
                    <select className="w-full border rounded-md p-2" value={sourceYear} onChange={(e) => setSourceYear(e.target.value)}>
                      <option value="">{language === "zh" ? "选择源学年" : "Select source year"}</option>
                      {years?.map((y) => (
                        <option key={y.id} value={y.yearName}>{y.displayName || y.yearName}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "目标学年" : "Target Year"}</Label>
                    <select className="w-full border rounded-md p-2" value={targetYear} onChange={(e) => setTargetYear(e.target.value)}>
                      <option value="">{language === "zh" ? "选择目标学年" : "Select target year"}</option>
                      {years?.map((y) => (
                        <option key={y.id} value={y.yearName}>{y.displayName || y.yearName}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCopyDialogOpen(false)}>{language === "zh" ? "取消" : "Cancel"}</Button>
                  <Button onClick={handleCopyTopics} disabled={copyTopicsMutation.isPending}>
                    {copyTopicsMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                    {language === "zh" ? "复制" : "Copy"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button><Plus className="w-4 h-4 mr-2" />{language === "zh" ? "创建学年" : "Create Year"}</Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>{language === "zh" ? "创建新学年" : "Create New Year"}</DialogTitle>
                  <DialogDescription>{language === "zh" ? "配置新学年的基本参数，时间配置请在系统配置中设置" : "Configure basic parameters, time settings in System Config"}</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "学年名称 *" : "Year Name *"}</Label>
                    <Input placeholder="2024-2025" value={newYearName} onChange={(e) => setNewYearName(e.target.value)} />
                  </div>
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "显示名称" : "Display Name"}</Label>
                    <Input placeholder="2024-2025学年" value={newDisplayName} onChange={(e) => setNewDisplayName(e.target.value)} />
                  </div>
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "中方导师年度发布限额" : "ZJSU Teacher Quota"}</Label>
                    <Input type="number" min={1} value={chineseTeacherQuota} onChange={(e) => setChineseTeacherQuota(parseInt(e.target.value) || 5)} />
                    <p className="text-xs text-gray-500">{language === "zh" ? "中方导师每年可发布的题目数量上限，英方导师不受限制" : "Max topics ZJSU teachers can publish per year. Sussex teachers are unlimited."}</p>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>{language === "zh" ? "取消" : "Cancel"}</Button>
                  <Button onClick={handleCreateYear} disabled={createYearMutation.isPending}>
                    {createYearMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                    {language === "zh" ? "创建" : "Create"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="grid gap-4">
          {years?.map((year) => (
            <Card key={year.id} className={year.isCurrentYear ? "border-green-500 border-2" : ""}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-gray-500" />
                    <CardTitle className="text-lg">{year.displayName || year.yearName}</CardTitle>
                    {getStatusBadge(year.status, Boolean(year.isCurrentYear))}
                  </div>
                  <div className="flex gap-2">
                    {!year.isCurrentYear && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => setCurrentYearMutation.mutate({ id: year.id })}>
                          <Check className="w-4 h-4 mr-1" />{language === "zh" ? "设为当前" : "Set Active"}
                        </Button>
                        <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50" onClick={() => openDeleteDialog(year)}>
                          <Trash2 className="w-4 h-4 mr-1" />{language === "zh" ? "删除" : "Delete"}
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">{language === "zh" ? "中方导师年度限额" : "ZJSU Teacher Quota"}:</span>
                    <span className="ml-2 font-medium">{year.chineseTeacherQuota || 5} {language === "zh" ? "个题目" : "topics"}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">{language === "zh" ? "英方导师限额" : "Sussex Teacher Quota"}:</span>
                    <span className="ml-2 font-medium">{language === "zh" ? "不限" : "Unlimited"}</span>
                  </div>
                </div>
                {(year.studentSelectionStart || year.teacherConfirmStart) && (
                  <div className="mt-4 pt-4 border-t grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">{language === "zh" ? "学生选题时间" : "Student Selection"}:</span>
                      <div className="font-medium">
                        {year.studentSelectionStart ? new Date(year.studentSelectionStart).toLocaleString() : "-"} ~ {year.studentSelectionEnd ? new Date(year.studentSelectionEnd).toLocaleString() : "-"}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-500">{language === "zh" ? "导师确认时间" : "Teacher Confirm"}:</span>
                      <div className="font-medium">
                        {year.teacherConfirmStart ? new Date(year.teacherConfirmStart).toLocaleString() : "-"} ~ {year.teacherConfirmEnd ? new Date(year.teacherConfirmEnd).toLocaleString() : "-"}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
          
          {(!years || years.length === 0) && (
            <Card className="py-12">
              <CardContent className="text-center text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>{language === "zh" ? "暂无学年数据，请创建新学年" : "No years found, please create a new year"}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </main>

      {/* 删除确认对话框 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              {language === "zh" ? "确认删除学年" : "Confirm Delete Year"}
            </DialogTitle>
            <DialogDescription className="pt-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-800 font-medium mb-2">
                  {language === "zh" ? "⚠️ 警告：此操作不可撤销！" : "⚠️ Warning: This action cannot be undone!"}
                </p>
                <p className="text-red-700 text-sm">
                  {language === "zh" 
                    ? `删除学年 "${yearToDelete?.name}" 将永久删除以下所有数据：`
                    : `Deleting year "${yearToDelete?.name}" will permanently remove:`}
                </p>
                <ul className="text-red-700 text-sm mt-2 list-disc list-inside">
                  <li>{language === "zh" ? "该学年的所有课题" : "All topics for this year"}</li>
                  <li>{language === "zh" ? "该学年的所有学生志愿" : "All student wishes for this year"}</li>
                  <li>{language === "zh" ? "该学年的所有匹配结果" : "All matching results for this year"}</li>
                  <li>{language === "zh" ? "该学年的所有学生账户" : "All student accounts for this year"}</li>
                </ul>
              </div>
              <p className="text-gray-600">
                {language === "zh" 
                  ? "请确认您已备份所需数据。删除后数据将无法找回。"
                  : "Please ensure you have backed up any needed data. Deleted data cannot be recovered."}
              </p>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button variant="destructive" onClick={handleDeleteYear} disabled={deleteYearMutation.isPending}>
              {deleteYearMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              {language === "zh" ? "确认删除" : "Confirm Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
