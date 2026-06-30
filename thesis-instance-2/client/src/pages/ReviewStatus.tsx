import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, Download, CheckCircle, Clock, AlertCircle, UserX, Loader2 } from "lucide-react";
import { useEffect } from "react";
import { toast } from "sonner";

export default function ReviewStatus() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [, setLocation] = useLocation();

  const { data: reviewStatuses, isLoading } = trpc.admin.getTeacherReviewStatuses.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });
  
  const { data: incompleteTeachers } = trpc.admin.getIncompleteReviewTeachers.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });

  const exportMutation = trpc.admin.exportIncompleteReviewTeachers.useMutation({
    onSuccess: (data) => {
      const byteCharacters = atob(data.base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/vnd.ms-excel" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = data.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success(language === "zh" ? "导出成功" : "Export successful");
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "partial":
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case "not_started":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case "no_students":
        return <UserX className="w-4 h-4 text-gray-400" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
      completed: { label: language === "zh" ? "已完成" : "Completed", variant: "default" },
      partial: { label: language === "zh" ? "部分完成" : "Partial", variant: "secondary" },
      not_started: { label: language === "zh" ? "未开始" : "Not Started", variant: "destructive" },
      no_students: { label: language === "zh" ? "无学生" : "No Students", variant: "outline" },
    };
    const config = statusMap[status] || { label: status, variant: "outline" as const };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  // 统计数据
  const stats = reviewStatuses ? {
    total: reviewStatuses.length,
    completed: reviewStatuses.filter(t => t.status === "completed").length,
    partial: reviewStatuses.filter(t => t.status === "partial").length,
    notStarted: reviewStatuses.filter(t => t.status === "not_started").length,
    noStudents: reviewStatuses.filter(t => t.status === "no_students").length,
  } : { total: 0, completed: 0, partial: 0, notStarted: 0, noStudents: 0 };

  if (loading || isLoading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => setLocation("/admin")}><ArrowLeft className="w-4 h-4 mr-2" />{language === "zh" ? "返回" : "Back"}</Button>
          <h1 className="text-xl font-semibold">{language === "zh" ? "导师审核监控" : "Teacher Review Monitor"}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* 统计卡片 */}
        <div className="grid md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{language === "zh" ? "导师总数" : "Total Teachers"}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                {language === "zh" ? "已完成" : "Completed"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <Clock className="w-4 h-4 text-yellow-500" />
                {language === "zh" ? "部分完成" : "Partial"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.partial}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                {language === "zh" ? "未开始" : "Not Started"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.notStarted}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <UserX className="w-4 h-4 text-gray-400" />
                {language === "zh" ? "无学生申请" : "No Students"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-400">{stats.noStudents}</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="all" className="space-y-4">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="all">{language === "zh" ? "全部导师" : "All Teachers"}</TabsTrigger>
              <TabsTrigger value="incomplete">{language === "zh" ? "未完成审核" : "Incomplete"}</TabsTrigger>
            </TabsList>
            <Button variant="outline" onClick={() => exportMutation.mutate()} disabled={exportMutation.isPending}>
              {exportMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
              {language === "zh" ? "导出未完成名单" : "Export Incomplete"}
            </Button>
          </div>

          <TabsContent value="all">
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{language === "zh" ? "导师姓名" : "Teacher Name"}</TableHead>
                      <TableHead>{language === "zh" ? "邮箱" : "Email"}</TableHead>
                      <TableHead>{language === "zh" ? "导师类型" : "Type"}</TableHead>
                      <TableHead>{language === "zh" ? "审核状态" : "Status"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "待审核" : "Pending"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "已同意" : "Approved"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "已拒绝" : "Rejected"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "总申请" : "Total"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reviewStatuses?.map((teacher) => (
                      <TableRow key={teacher.teacherId}>
                        <TableCell className="font-medium">{teacher.teacherName}</TableCell>
                        <TableCell>{teacher.teacherEmail}</TableCell>
                        <TableCell>
                          {teacher.teacherType === "chinese" ? (language === "zh" ? "中方导师" : "ZJSU") : 
                           teacher.teacherType === "british" ? (language === "zh" ? "英方导师" : "Sussex") : "-"}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(teacher.status)}
                            {getStatusBadge(teacher.status)}
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className={teacher.totalPending > 0 ? "text-yellow-600 font-medium" : ""}>{teacher.totalPending}</span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="text-green-600">{teacher.totalApproved}</span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="text-red-600">{teacher.totalRejected}</span>
                        </TableCell>
                        <TableCell className="text-center">{teacher.totalStudents}</TableCell>
                      </TableRow>
                    ))}
                    {(!reviewStatuses || reviewStatuses.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                          {language === "zh" ? "暂无导师数据" : "No teacher data"}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="incomplete">
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{language === "zh" ? "导师姓名" : "Teacher Name"}</TableHead>
                      <TableHead>{language === "zh" ? "邮箱" : "Email"}</TableHead>
                      <TableHead>{language === "zh" ? "导师类型" : "Type"}</TableHead>
                      <TableHead>{language === "zh" ? "审核状态" : "Status"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "待审核" : "Pending"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "已同意" : "Approved"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "已拒绝" : "Rejected"}</TableHead>
                      <TableHead className="text-center">{language === "zh" ? "总申请" : "Total"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {incompleteTeachers?.map((teacher) => (
                      <TableRow key={teacher.teacherId}>
                        <TableCell className="font-medium">{teacher.teacherName}</TableCell>
                        <TableCell>{teacher.teacherEmail}</TableCell>
                        <TableCell>
                          {teacher.teacherType === "chinese" ? (language === "zh" ? "中方导师" : "ZJSU") : 
                           teacher.teacherType === "british" ? (language === "zh" ? "英方导师" : "Sussex") : "-"}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(teacher.status)}
                            {getStatusBadge(teacher.status)}
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="text-yellow-600 font-medium">{teacher.totalPending}</span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="text-green-600">{teacher.totalApproved}</span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="text-red-600">{teacher.totalRejected}</span>
                        </TableCell>
                        <TableCell className="text-center">{teacher.totalStudents}</TableCell>
                      </TableRow>
                    ))}
                    {(!incompleteTeachers || incompleteTeachers.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                          {language === "zh" ? "所有导师均已完成审核" : "All teachers have completed review"}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
