import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, Upload, Download, FileSpreadsheet, AlertCircle } from "lucide-react";

export default function BulkImport() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [importType, setImportType] = useState<"teacher" | "student">("student");
  const [csvData, setCsvData] = useState("");
  const [importResult, setImportResult] = useState<{ success: number; failed: number; errors: string[] } | null>(null);

  const utils = trpc.useUtils();
  const importMutation = trpc.admin.bulkImportUsers.useMutation({
    onSuccess: (data) => {
      setImportResult(data);
      if (data.success > 0) {
        toast.success(language === "zh" ? `成功导入 ${data.success} 个用户` : `Successfully imported ${data.success} users`);
        utils.admin.getUsers.invalidate();
      }
      if (data.failed > 0) {
        toast.error(language === "zh" ? `${data.failed} 个用户导入失败` : `${data.failed} users failed to import`);
      }
    },
    onError: (e) => toast.error(e.message),
  });

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  const parseCSV = (csv: string) => {
    const lines = csv.trim().split("\n");
    if (lines.length < 2) return [];

    const headers = lines[0].split(",").map(h => h.trim().toLowerCase());
    const users = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(",").map(v => v.trim());
      if (values.length < 2) continue;

      const user: any = {
        role: importType,
      };

      headers.forEach((header, index) => {
        const value = values[index] || "";
        switch (header) {
          case "email":
          case "邮箱":
          case "用户名":
            user.email = value;
            break;
          case "password":
          case "密码":
            user.password = value;
            break;
          case "name":
          case "姓名":
            user.name = value;
            break;
          case "teachertype":
          case "导师类型":
            user.teacherType = value === "british" || value === "英方" ? "british" : "chinese";
            break;
          case "studenttype":
          case "学生类型":
            user.studentType = value === "transfer" || value === "分流" ? "transfer" : "non_transfer";
            break;
          case "studentmajor":
          case "专业":
            user.studentMajor = value === "communication" || value === "通信" || value === "通信工程" ? "communication" : "electronic_info";
            break;
          case "studentid":
          case "学号":
          case "中方学号":
            user.studentId = value;
            break;
          case "candidateno":
          case "英方学号":
            user.candidateNo = value;
            break;
          case "studentclass":
          case "班级":
            user.studentClass = value;
            break;
          case "faculty":
          case "学院":
            user.faculty = value;
            break;
        }
      });

      if (user.email && user.password) {
        users.push(user);
      }
    }

    return users;
  };

  const handleImport = () => {
    const users = parseCSV(csvData);
    if (users.length === 0) {
      toast.error(language === "zh" ? "没有有效的用户数据" : "No valid user data found");
      return;
    }
    importMutation.mutate({ users });
  };

  const downloadTemplate = () => {
    let template = "";
    if (importType === "student") {
      template = "email,password,name,studentType,studentMajor,studentId,candidateNo,studentClass,faculty\nstudent@example.com,zjsu@stu,张三,non_transfer,electronic_info,2021001,UK001,21电信1班,萨塞克斯人工智能学院";
    } else {
      template = "email,password,name,teacherType\nteacher@example.com,zjsu@tea,李教授,chinese";
    }
    
    const blob = new Blob(["\ufeff" + template], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${importType}_template.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}>
              <Globe className="w-4 h-4 mr-2" />{language === "zh" ? "EN" : "中"}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />{t.logout}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => setLocation("/admin/users")}>
            <ArrowLeft className="w-4 h-4 mr-2" />{t.back}
          </Button>
          <h1 className="text-2xl font-bold">{language === "zh" ? "批量导入用户" : "Bulk Import Users"}</h1>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>{language === "zh" ? "导入设置" : "Import Settings"}</CardTitle>
              <CardDescription>{language === "zh" ? "选择导入类型并粘贴CSV数据" : "Select import type and paste CSV data"}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>{language === "zh" ? "导入类型" : "Import Type"}</Label>
                <Select value={importType} onValueChange={(v: "teacher" | "student") => setImportType(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="student">{language === "zh" ? "学生" : "Students"}</SelectItem>
                    <SelectItem value="teacher">{language === "zh" ? "导师" : "Teachers"}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>{language === "zh" ? "CSV数据" : "CSV Data"}</Label>
                  <Button variant="link" size="sm" onClick={downloadTemplate}>
                    <Download className="w-4 h-4 mr-1" />
                    {language === "zh" ? "下载模板" : "Download Template"}
                  </Button>
                </div>
                <Textarea
                  placeholder={language === "zh" 
                    ? "粘贴CSV格式数据，第一行为表头...\n例如：email,password,name,studentType,studentMajor" 
                    : "Paste CSV data here, first row as headers...\nExample: email,password,name,studentType,studentMajor"}
                  value={csvData}
                  onChange={(e) => setCsvData(e.target.value)}
                  rows={10}
                  className="font-mono text-sm"
                />
              </div>

              <Button onClick={handleImport} disabled={importMutation.isPending || !csvData.trim()} className="w-full">
                <Upload className="w-4 h-4 mr-2" />
                {importMutation.isPending 
                  ? (language === "zh" ? "导入中..." : "Importing...")
                  : (language === "zh" ? "开始导入" : "Start Import")}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileSpreadsheet className="w-5 h-5" />
                  {language === "zh" ? "CSV格式说明" : "CSV Format Guide"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <p className="text-gray-600">
                    {language === "zh" 
                      ? "支持的字段（表头不区分大小写）："
                      : "Supported fields (headers are case-insensitive):"}
                  </p>
                  {importType === "student" ? (
                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                      <li><code className="bg-gray-100 px-1 rounded">email/邮箱</code> - {language === "zh" ? "登录邮箱（必填）" : "Login email (required)"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">password/密码</code> - {language === "zh" ? "登录密码（必填）" : "Password (required)"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">name/姓名</code> - {language === "zh" ? "学生姓名" : "Student name"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">studentType/学生类型</code> - {language === "zh" ? "transfer/分流 或 non_transfer/非分流" : "transfer/Single-Degree or non_transfer/Dual-Degree"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">studentMajor/专业</code> - electronic_info/电子信息工程 或 communication/通信工程</li>
                      <li><code className="bg-gray-100 px-1 rounded">studentId/学号</code> - {language === "zh" ? "中方学号" : "Chinese student ID"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">candidateNo/英方学号</code> - {language === "zh" ? "英方学号" : "UK candidate number"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">studentClass/班级</code> - {language === "zh" ? "学生班级" : "Class"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">faculty/学院</code> - {language === "zh" ? "所属学院" : "Faculty"}</li>
                    </ul>
                  ) : (
                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                      <li><code className="bg-gray-100 px-1 rounded">email/邮箱</code> - {language === "zh" ? "登录邮箱（必填）" : "Login email (required)"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">password/密码</code> - {language === "zh" ? "登录密码（必填）" : "Password (required)"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">name/姓名</code> - {language === "zh" ? "导师姓名" : "Teacher name"}</li>
                      <li><code className="bg-gray-100 px-1 rounded">teacherType/导师类型</code> - chinese/中方 或 british/英方</li>
                    </ul>
                  )}
                </div>
              </CardContent>
            </Card>

            {importResult && (
              <Card className={importResult.failed > 0 ? "border-orange-200" : "border-green-200"}>
                <CardHeader>
                  <CardTitle>{language === "zh" ? "导入结果" : "Import Result"}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-green-600">
                      {language === "zh" ? `成功: ${importResult.success} 个` : `Success: ${importResult.success}`}
                    </p>
                    {importResult.failed > 0 && (
                      <>
                        <p className="text-red-600">
                          {language === "zh" ? `失败: ${importResult.failed} 个` : `Failed: ${importResult.failed}`}
                        </p>
                        {importResult.errors.length > 0 && (
                          <div className="mt-2 p-3 bg-red-50 rounded-lg">
                            <p className="text-sm font-medium text-red-800 mb-1 flex items-center gap-1">
                              <AlertCircle className="w-4 h-4" />
                              {language === "zh" ? "错误详情:" : "Error details:"}
                            </p>
                            <ul className="text-sm text-red-700 list-disc list-inside">
                              {importResult.errors.slice(0, 10).map((err, i) => (
                                <li key={i}>{err}</li>
                              ))}
                              {importResult.errors.length > 10 && (
                                <li>...{language === "zh" ? `还有 ${importResult.errors.length - 10} 个错误` : `and ${importResult.errors.length - 10} more errors`}</li>
                              )}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
