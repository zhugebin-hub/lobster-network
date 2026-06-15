import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, Download, Users, CheckCircle, Clock, AlertCircle, Loader2, BarChart3, UserCheck, UserX } from "lucide-react";
import { useEffect } from "react";
import { toast } from "sonner";

export default function Statistics() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [, setLocation] = useLocation();

  // 学生选题统计
  const { data: selectionStats, isLoading: statsLoading } = trpc.admin.getSelectionStats.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });
  
  // 未选择志愿的学生
  const { data: unselectedStudents } = trpc.admin.getUnselectedStudents.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });
  
  // 导师审核状态
  const { data: reviewStatuses } = trpc.admin.getTeacherReviewStatuses.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });
  
  // 匹配结果
  const { data: matches } = trpc.admin.getAllMatches.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });
  
  // 用户列表
  const { data: users } = trpc.admin.getUsers.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });

  // 导出未选学生
  const exportUnselectedMutation = trpc.admin.exportUnselectedStudents.useMutation({
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

  // 计算统计数据
  const teachers = users?.filter(u => u.role === "teacher") || [];
  const students = users?.filter(u => u.role === "student") || [];
  
  const reviewStats = reviewStatuses ? {
    total: reviewStatuses.length,
    completed: reviewStatuses.filter(t => t.status === "completed").length,
    partial: reviewStatuses.filter(t => t.status === "partial").length,
    notStarted: reviewStatuses.filter(t => t.status === "not_started").length,
    noStudents: reviewStatuses.filter(t => t.status === "no_students").length,
  } : { total: 0, completed: 0, partial: 0, notStarted: 0, noStudents: 0 };

  if (loading || statsLoading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => setLocation("/admin")}><ArrowLeft className="w-4 h-4 mr-2" />{language === "zh" ? "返回" : "Back"}</Button>
          <h1 className="text-xl font-semibold">{language === "zh" ? "数据统计" : "Statistics"}</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* 总览统计 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            {language === "zh" ? "总览统计" : "Overview Statistics"}
          </h2>
          <div className="grid md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">{language === "zh" ? "导师总数" : "Total Teachers"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{teachers.length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">{language === "zh" ? "学生总数" : "Total Students"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{students.length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">{language === "zh" ? "已匹配" : "Matched"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{matches?.length || 0}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">{language === "zh" ? "待匹配" : "Pending"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">{students.length - (matches?.length || 0)}</div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* 学生选题状态监控 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <UserCheck className="w-5 h-5" />
            {language === "zh" ? "学生选题状态监控" : "Student Selection Status"}
          </h2>
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  {language === "zh" ? "已选择志愿" : "Selected"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{selectionStats?.selectedStudents || 0}</div>
                <p className="text-sm text-gray-500">
                  {students.length > 0 ? `${((selectionStats?.selectedStudents || 0) / students.length * 100).toFixed(1)}%` : "0%"}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  {language === "zh" ? "未选择志愿" : "Not Selected"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{selectionStats?.unselectedStudents || 0}</div>
                <p className="text-sm text-gray-500">
                  {students.length > 0 ? `${((selectionStats?.unselectedStudents || 0) / students.length * 100).toFixed(1)}%` : "0%"}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Users className="w-4 h-4 text-blue-500" />
                  {language === "zh" ? "学生总数" : "Total Students"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{selectionStats?.totalStudents || 0}</div>
              </CardContent>
            </Card>
          </div>

          {/* 未选学生列表 */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{language === "zh" ? "未选择志愿的学生" : "Students Without Selections"}</CardTitle>
                  <CardDescription>{language === "zh" ? "以下学生尚未提交志愿" : "The following students have not submitted wishes"}</CardDescription>
                </div>
                <Button variant="outline" onClick={() => exportUnselectedMutation.mutate()} disabled={exportUnselectedMutation.isPending}>
                  {exportUnselectedMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                  {language === "zh" ? "导出名单" : "Export List"}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{language === "zh" ? "中方学号" : "Chinese Student ID"}</TableHead>
                    <TableHead>{language === "zh" ? "萨塞克斯学号" : "Sussex ID"}</TableHead>
                    <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                    <TableHead>{language === "zh" ? "萨塞克斯邮箱" : "Sussex Email"}</TableHead>
                    <TableHead>{language === "zh" ? "专业" : "Major"}</TableHead>
                    <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {unselectedStudents?.slice(0, 10).map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>{student.studentId || "-"}</TableCell>
                      <TableCell>{(student as any).sussexId || student.candidateNo || "-"}</TableCell>
                      <TableCell className="font-medium">{student.name}</TableCell>
                      <TableCell>{(student as any).sussexEmail || student.email}</TableCell>
                      <TableCell>
                        {student.studentMajor === "electronic_info" ? (language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering") : 
                         student.studentMajor === "communication" ? (language === "zh" ? "通信工程" : "Communications Engineering") : "-"}
                      </TableCell>
                      <TableCell>{student.studentClass || "-"}</TableCell>
                    </TableRow>
                  ))}
                  {(!unselectedStudents || unselectedStudents.length === 0) && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                        {language === "zh" ? "所有学生均已选择志愿" : "All students have selected wishes"}
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
              {unselectedStudents && unselectedStudents.length > 10 && (
                <p className="text-sm text-gray-500 mt-4 text-center">
                  {language === "zh" ? `还有 ${unselectedStudents.length - 10} 名学生未显示，请导出完整名单查看` : 
                   `${unselectedStudents.length - 10} more students not shown, export for full list`}
                </p>
              )}
            </CardContent>
          </Card>
        </section>

        {/* 导师审核状态统计 */}
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <UserX className="w-5 h-5" />
            {language === "zh" ? "导师审核状态统计" : "Teacher Review Status"}
          </h2>
          <div className="grid md:grid-cols-5 gap-4 mb-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">{language === "zh" ? "导师总数" : "Total"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reviewStats.total}</div>
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
                <div className="text-2xl font-bold text-green-600">{reviewStats.completed}</div>
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
                <div className="text-2xl font-bold text-yellow-600">{reviewStats.partial}</div>
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
                <div className="text-2xl font-bold text-red-600">{reviewStats.notStarted}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <UserX className="w-4 h-4 text-gray-400" />
                  {language === "zh" ? "无学生" : "No Students"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-400">{reviewStats.noStudents}</div>
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardContent className="pt-6">
              <Button variant="outline" onClick={() => setLocation("/admin/review-status")}>
                {language === "zh" ? "查看详细审核监控" : "View Detailed Review Monitor"}
              </Button>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}
