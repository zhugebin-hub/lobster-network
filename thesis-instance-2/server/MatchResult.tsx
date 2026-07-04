import { useState, useMemo, useCallback } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, FileSpreadsheet, Search, Filter, Undo2, AlertTriangle, Plus, Upload, Download, CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function MatchResult() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  
  // 筛选状态
  const [searchTerm, setSearchTerm] = useState("");
  const [facultyFilter, setFacultyFilter] = useState<string>("all");
  const [majorFilter, setMajorFilter] = useState<string>("all");
  const [teacherFilter, setTeacherFilter] = useState<string>("all");
  
  // 撤回对话框状态
  const [revokeDialogOpen, setRevokeDialogOpen] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<any>(null);

  // 单个添加对话框状态
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [addForm, setAddForm] = useState({
    studentId: "",
    studentName: "",
    sussexId: "",
    teacherName: "",
    topicTitle: "",
    remarks: "",
  });

  // 批量导入对话框状态
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importStep, setImportStep] = useState<"upload" | "preview" | "result">("upload");
  const [importData, setImportData] = useState<Array<{
    studentId: string;
    studentName: string;
    sussexId?: string;
    teacherName: string;
    topicTitle: string;
    remarks?: string;
  }>>([]);
  const [importResult, setImportResult] = useState<{
    success: boolean;
    totalCount: number;
    successCount: number;
    failedCount: number;
    errors: Array<{ row: number; studentName: string; studentId: string; reason: string }>;
  } | null>(null);

  const utils = trpc.useUtils();
  const { data: matches } = trpc.admin.getAllMatches.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });
  
  const revokeMutation = trpc.admin.revokeMatch.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "撤回成功" : "Revoke successful");
      utils.admin.getAllMatches.invalidate();
      setRevokeDialogOpen(false);
      setSelectedMatch(null);
    },
    onError: (e: any) => toast.error(e.message),
  });
  
  const exportMutation = trpc.admin.exportMatches.useMutation({
    onSuccess: (data: any) => {
      const byteCharacters = atob(data.base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/vnd.ms-excel' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = data.filename || `毕业论文选题匹配结果_${new Date().toISOString().split('T')[0]}.xls`;
      a.click();
      URL.revokeObjectURL(url);
      setShowExportDialog(false);
      toast.success(language === "zh" ? "导出成功" : "Export successful");
    },
    onError: (e: any) => toast.error(e.message),
    onSettled: () => setIsExporting(false),
  });

  // 单个添加 mutation
  const importSingleMutation = trpc.admin.importSingleMatch.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "添加匹配结果成功" : "Match result added successfully");
      utils.admin.getAllMatches.invalidate();
      setAddDialogOpen(false);
      setAddForm({ studentId: "", studentName: "", sussexId: "", teacherName: "", topicTitle: "", remarks: "" });
    },
    onError: (e: any) => toast.error(e.message),
  });

  // 批量导入 mutation
  const batchImportMutation = trpc.admin.batchImportMatches.useMutation({
    onSuccess: (data: any) => {
      setImportResult(data);
      setImportStep("result");
      if (data.success) {
        toast.success(language === "zh" ? `成功导入 ${data.successCount} 条匹配记录` : `Successfully imported ${data.successCount} match records`);
        utils.admin.getAllMatches.invalidate();
      }
    },
    onError: (e: any) => {
      toast.error(e.message);
    },
  });

  // 获取唯一的筛选选项
  const filterOptions = useMemo(() => {
    if (!matches) return { faculties: [], majors: [], teachers: [] };
    const faculties = Array.from(new Set(matches.map((m: any) => m.student?.faculty).filter((f: any): f is string => !!f)));
    const majors = Array.from(new Set(matches.map((m: any) => m.student?.studentMajor).filter(Boolean))) as string[];
    const teachers = Array.from(new Set(matches.map((m: any) => m.teacher?.name).filter((t: any): t is string => !!t)));
    return { faculties, majors, teachers };
  }, [matches]);

  // 筛选后的匹配结果
  const filteredMatches = useMemo(() => {
    if (!matches) return [];
    return matches.filter((m: any) => {
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        const matchesSearch = 
          m.student?.name?.toLowerCase().includes(search) ||
          m.student?.studentId?.toLowerCase().includes(search) ||
          m.teacher?.name?.toLowerCase().includes(search) ||
          m.topic?.title?.toLowerCase().includes(search);
        if (!matchesSearch) return false;
      }
      if (facultyFilter !== "all" && m.student?.faculty !== facultyFilter) return false;
      if (majorFilter !== "all" && m.student?.studentMajor !== majorFilter) return false;
      if (teacherFilter !== "all" && m.teacher?.name !== teacherFilter) return false;
      return true;
    });
  }, [matches, searchTerm, facultyFilter, majorFilter, teacherFilter]);

  const handleLogout = async () => { await logout(); setLocation("/"); };
  
  const handleExport = () => {
    setIsExporting(true);
    exportMutation.mutate();
  };

  const handleRevoke = (match: any) => {
    setSelectedMatch(match);
    setRevokeDialogOpen(true);
  };

  const confirmRevoke = () => {
    if (selectedMatch) {
      revokeMutation.mutate({ matchId: selectedMatch.id });
    }
  };

  const getMajorText = (major: string | null | undefined) => {
    if (major === "electronic_info") return language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering";
    if (major === "communication") return language === "zh" ? "通信工程" : "Communications Engineering";
    return "-";
  };

  // 处理单个添加提交
  const handleAddSubmit = () => {
    if (!addForm.studentId || !addForm.studentName || !addForm.teacherName || !addForm.topicTitle) {
      toast.error(language === "zh" ? "请填写所有必填字段" : "Please fill in all required fields");
      return;
    }
    importSingleMutation.mutate({
      studentId: addForm.studentId,
      studentName: addForm.studentName,
      sussexId: addForm.sussexId || undefined,
      teacherName: addForm.teacherName,
      topicTitle: addForm.topicTitle,
      remarks: addForm.remarks || undefined,
    });
  };

  // 处理Excel文件上传
  const handleFileUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 使用 SheetJS 解析 Excel
    try {
      const XLSX = await import("xlsx");
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json<any>(worksheet, { header: 1 });

      if (jsonData.length < 2) {
        toast.error(language === "zh" ? "Excel文件为空或格式不正确" : "Excel file is empty or format is incorrect");
        return;
      }

      // 查找表头行（包含"学生姓名"或"姓名"的行）
      let headerRowIndex = 0;
      for (let i = 0; i < Math.min(5, jsonData.length); i++) {
        const row = jsonData[i] as any[];
        if (row && row.some((cell: any) => {
          const cellStr = String(cell || "").trim();
          return cellStr.includes("姓名") || cellStr.includes("学号") || cellStr.includes("Name");
        })) {
          headerRowIndex = i;
          break;
        }
      }

      const headers = (jsonData[headerRowIndex] as any[]).map((h: any) => String(h || "").trim());
      
      // 智能匹配列索引
      const findCol = (keywords: string[]) => {
        return headers.findIndex(h => keywords.some(k => h.includes(k)));
      };

      const nameCol = findCol(["学生姓名", "姓名", "Name"]);
      const studentIdCol = findCol(["中方学号", "学号"]);
      const sussexIdCol = findCol(["英方学号", "Sussex", "Candidate"]);
      const topicCol = findCol(["论文题目", "毕设题目", "题目", "Topic"]);
      const teacherCol = findCol(["导师", "指导教师", "Supervisor"]);
      const remarksCol = findCol(["备注", "Remarks", "Note"]);

      if (nameCol === -1 || studentIdCol === -1 || topicCol === -1 || teacherCol === -1) {
        toast.error(language === "zh" 
          ? "Excel格式不正确，请确保包含以下列：学生姓名、中方学号、论文题目、导师" 
          : "Invalid Excel format. Required columns: Student Name, Student ID, Topic, Supervisor");
        return;
      }

      // 解析数据行
      const parsedItems: typeof importData = [];
      for (let i = headerRowIndex + 1; i < jsonData.length; i++) {
        const row = jsonData[i] as any[];
        if (!row || row.length === 0) continue;
        
        const studentName = String(row[nameCol] || "").trim();
        const studentId = String(row[studentIdCol] || "").trim();
        const topicTitle = String(row[topicCol] || "").trim();
        const teacherName = String(row[teacherCol] || "").trim();

        // 跳过空行
        if (!studentName && !studentId && !topicTitle) continue;

        parsedItems.push({
          studentId,
          studentName,
          sussexId: sussexIdCol >= 0 ? String(row[sussexIdCol] || "").trim() || undefined : undefined,
          teacherName,
          topicTitle,
          remarks: remarksCol >= 0 ? String(row[remarksCol] || "").trim() || undefined : undefined,
        });
      }

      if (parsedItems.length === 0) {
        toast.error(language === "zh" ? "未解析到有效数据" : "No valid data found");
        return;
      }

      setImportData(parsedItems);
      setImportStep("preview");
      toast.success(language === "zh" ? `解析到 ${parsedItems.length} 条记录` : `Parsed ${parsedItems.length} records`);
    } catch (err) {
      console.error("Excel parse error:", err);
      toast.error(language === "zh" ? "解析Excel文件失败" : "Failed to parse Excel file");
    }
    
    // 重置 input
    e.target.value = "";
  }, [language]);

  // 执行批量导入
  const handleBatchImport = () => {
    batchImportMutation.mutate({ items: importData });
  };

  // 下载导入模板
  const handleDownloadTemplate = async () => {
    try {
      const XLSX = await import("xlsx");
      const wb = XLSX.utils.book_new();
      const wsData = [
        ["序号", "学生姓名", "中方学号", "英方学号", "论文题目", "导师", "备注"],
        [1, "张三", "2037010101", "24001234", "基于深度学习的图像分类研究", "李教授", ""],
        [2, "李四", "2037010102", "24001235", "自然语言处理在情感分析中的应用", "王教授", "分流学生"],
      ];
      const ws = XLSX.utils.aoa_to_sheet(wsData);
      // 设置列宽
      ws["!cols"] = [
        { wch: 6 }, { wch: 12 }, { wch: 14 }, { wch: 14 }, 
        { wch: 50 }, { wch: 12 }, { wch: 15 }
      ];
      XLSX.utils.book_append_sheet(wb, ws, "匹配结果导入模板");
      XLSX.writeFile(wb, "匹配结果导入模板.xlsx");
      toast.success(language === "zh" ? "模板下载成功" : "Template downloaded");
    } catch (err) {
      toast.error(language === "zh" ? "下载模板失败" : "Failed to download template");
    }
  };

  // 重置导入对话框
  const resetImportDialog = () => {
    setImportDialogOpen(false);
    setImportStep("upload");
    setImportData([]);
    setImportResult(null);
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center"><GraduationCap className="w-6 h-6 text-white" /></div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}><Globe className="w-4 h-4 mr-2" />{language === "zh" ? "EN" : "中"}</Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}><LogOut className="w-4 h-4 mr-2" />{t.logout}</Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => setLocation("/admin")}><ArrowLeft className="w-4 h-4 mr-2" />{t.back}</Button>
            <h1 className="text-2xl font-bold">{language === "zh" ? "匹配结果" : "Match Results"}</h1>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => setAddDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              {language === "zh" ? "单个添加" : "Add Single"}
            </Button>
            <Button variant="outline" onClick={() => { resetImportDialog(); setImportDialogOpen(true); }}>
              <Upload className="w-4 h-4 mr-2" />
              {language === "zh" ? "批量导入" : "Batch Import"}
            </Button>
            <Button onClick={() => setShowExportDialog(true)}>
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              {language === "zh" ? "导出Excel" : "Export Excel"}
            </Button>
          </div>
        </div>

        {/* 筛选区域 */}
        <Card className="mb-6">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Filter className="w-5 h-5" />
              {language === "zh" ? "筛选条件" : "Filters"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder={language === "zh" ? "搜索学生/导师/题目..." : "Search student/teacher/topic..."}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <Select value={facultyFilter} onValueChange={setFacultyFilter}>
                <SelectTrigger>
                  <SelectValue placeholder={language === "zh" ? "学院" : "Faculty"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{language === "zh" ? "全部学院" : "All Faculties"}</SelectItem>
                  {filterOptions.faculties.map((f: string) => (
                    <SelectItem key={f} value={f}>{f}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={majorFilter} onValueChange={setMajorFilter}>
                <SelectTrigger>
                  <SelectValue placeholder={language === "zh" ? "专业" : "Major"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{language === "zh" ? "全部专业" : "All Courses"}</SelectItem>
                  <SelectItem value="electronic_info">{language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering"}</SelectItem>
                  <SelectItem value="communication">{language === "zh" ? "通信工程" : "Communications Engineering"}</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={teacherFilter} onValueChange={setTeacherFilter}>
                <SelectTrigger>
                  <SelectValue placeholder={language === "zh" ? "导师" : "Supervisor"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{language === "zh" ? "全部导师" : "All Supervisors"}</SelectItem>
                  {filterOptions.teachers.map((t: string) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{language === "zh" ? "匹配列表" : "Match List"}</CardTitle>
            <CardDescription>
              {language === "zh" 
                ? `共 ${filteredMatches.length} 条匹配记录${filteredMatches.length !== matches?.length ? ` (筛选自 ${matches?.length || 0} 条)` : ""}`
                : `Total ${filteredMatches.length} match records${filteredMatches.length !== matches?.length ? ` (filtered from ${matches?.length || 0})` : ""}`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">{language === "zh" ? "序号" : "No."}</TableHead>
                    <TableHead>{language === "zh" ? "学院" : "Faculty"}</TableHead>
                    <TableHead>{language === "zh" ? "专业" : "Major"}</TableHead>
                    <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                    <TableHead>{language === "zh" ? "学生姓名" : "Student"}</TableHead>
                    <TableHead>{language === "zh" ? "中方学号" : "Student ID"}</TableHead>
                    <TableHead>{language === "zh" ? "英方学号" : "Candidate No."}</TableHead>
                    <TableHead>{language === "zh" ? "导师" : "Supervisor"}</TableHead>
                    <TableHead>{language === "zh" ? "论文题目" : "Topic"}</TableHead>
                    <TableHead>{language === "zh" ? "志愿" : "Pref"}</TableHead>
                    <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredMatches.map((m: any, index: number) => (
                    <TableRow key={m.id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>{m.student?.faculty || "-"}</TableCell>
                      <TableCell>{getMajorText(m.student?.studentMajor)}</TableCell>
                      <TableCell>{m.student?.studentClass || "-"}</TableCell>
                      <TableCell className="font-medium">{m.student?.name || "-"}</TableCell>
                      <TableCell className="font-mono text-sm">{m.student?.studentId || "-"}</TableCell>
                      <TableCell className="font-mono text-sm">{m.student?.sussexId || m.student?.candidateNo || "-"}</TableCell>
                      <TableCell>{m.teacher?.name || "-"}</TableCell>
                      <TableCell className="max-w-xs truncate" title={m.topic?.titleEn || m.topic?.title}>{m.topic?.titleEn || m.topic?.title || "-"}</TableCell>
                      <TableCell>
                        <Badge variant={m.matchRound === 0 ? "secondary" : m.isAdjustment ? "secondary" : "outline"}>
                          {m.matchRound === 0
                            ? (language === "zh" ? "导入" : "Import")
                            : m.isAdjustment 
                              ? (language === "zh" ? "调剂" : "Adj")
                              : (language === "zh" ? `第${m.matchRound}志愿` : `#${m.matchRound}`)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRevoke(m)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Undo2 className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  {filteredMatches.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={11} className="text-center py-8 text-gray-500">
                        {language === "zh" ? "暂无匹配记录" : "No match records"}
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* 单个添加对话框 */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-600" />
              {language === "zh" ? "添加匹配结果" : "Add Match Result"}
            </DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? "手动添加一条匹配记录。系统将自动验证账号存在性和题目重名，并同步课题发布、题库和匹配状态。"
                : "Manually add a match record. The system will validate accounts and topic duplicates, then sync topic, library, and match status."}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{language === "zh" ? "学生姓名" : "Student Name"} <span className="text-red-500">*</span></Label>
                <Input
                  value={addForm.studentName}
                  onChange={(e) => setAddForm(prev => ({ ...prev, studentName: e.target.value }))}
                  placeholder={language === "zh" ? "如：张三" : "e.g. Zhang San"}
                />
              </div>
              <div className="space-y-2">
                <Label>{language === "zh" ? "中方学号" : "Student ID"} <span className="text-red-500">*</span></Label>
                <Input
                  value={addForm.studentId}
                  onChange={(e) => setAddForm(prev => ({ ...prev, studentId: e.target.value }))}
                  placeholder={language === "zh" ? "如：2037010101" : "e.g. 2037010101"}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{language === "zh" ? "英方学号" : "Sussex ID"}</Label>
                <Input
                  value={addForm.sussexId}
                  onChange={(e) => setAddForm(prev => ({ ...prev, sussexId: e.target.value }))}
                  placeholder={language === "zh" ? "如：24001234" : "e.g. 24001234"}
                />
              </div>
              <div className="space-y-2">
                <Label>{language === "zh" ? "导师姓名" : "Supervisor"} <span className="text-red-500">*</span></Label>
                <Input
                  value={addForm.teacherName}
                  onChange={(e) => setAddForm(prev => ({ ...prev, teacherName: e.target.value }))}
                  placeholder={language === "zh" ? "如：李教授" : "e.g. Prof. Li"}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>{language === "zh" ? "论文题目" : "Topic Title"} <span className="text-red-500">*</span></Label>
              <Input
                value={addForm.topicTitle}
                onChange={(e) => setAddForm(prev => ({ ...prev, topicTitle: e.target.value }))}
                placeholder={language === "zh" ? "输入课题标题" : "Enter topic title"}
              />
            </div>
            

            
            <div className="space-y-2">
              <Label>{language === "zh" ? "备注" : "Remarks"}</Label>
              <Textarea
                value={addForm.remarks}
                onChange={(e) => setAddForm(prev => ({ ...prev, remarks: e.target.value }))}
                placeholder={language === "zh" ? "选填备注信息" : "Optional remarks"}
                rows={2}
              />
            </div>

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-sm">
                {language === "zh" 
                  ? "系统将自动：1) 验证学生和导师账号是否存在；2) 检查题库中是否有同名课题（三年内）；3) 创建课题并添加到题库；4) 建立匹配关系。"
                  : "System will: 1) Verify student/teacher accounts; 2) Check topic name duplicates (within 3 years); 3) Create topic and add to library; 4) Establish match."}
              </AlertDescription>
            </Alert>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleAddSubmit} disabled={importSingleMutation.isPending}>
              {importSingleMutation.isPending ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{language === "zh" ? "添加中..." : "Adding..."}</>
              ) : (
                <><Plus className="w-4 h-4 mr-2" />{language === "zh" ? "确认添加" : "Confirm Add"}</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 批量导入对话框 */}
      <Dialog open={importDialogOpen} onOpenChange={(open) => { if (!open) resetImportDialog(); else setImportDialogOpen(true); }}>
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-blue-600" />
              {language === "zh" ? "批量导入匹配结果" : "Batch Import Match Results"}
            </DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? "上传Excel文件批量导入匹配结果。系统将验证所有数据后统一执行导入。"
                : "Upload Excel file to batch import match results. System validates all data before importing."}
            </DialogDescription>
          </DialogHeader>

          {/* 步骤指示器 */}
          <div className="flex items-center justify-center gap-4 py-3">
            {[
              { key: "upload", label: language === "zh" ? "上传文件" : "Upload" },
              { key: "preview", label: language === "zh" ? "预览确认" : "Preview" },
              { key: "result", label: language === "zh" ? "导入结果" : "Result" },
            ].map((step, i) => (
              <div key={step.key} className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  importStep === step.key ? "bg-blue-600 text-white" : 
                  (step.key === "upload" && importStep !== "upload") || (step.key === "preview" && importStep === "result") 
                    ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                }`}>
                  {(step.key === "upload" && importStep !== "upload") || (step.key === "preview" && importStep === "result") 
                    ? <CheckCircle2 className="w-5 h-5" /> : i + 1}
                </div>
                <span className={`text-sm ${importStep === step.key ? "font-medium text-blue-600" : "text-gray-500"}`}>{step.label}</span>
                {i < 2 && <div className="w-8 h-px bg-gray-300" />}
              </div>
            ))}
          </div>

          {/* 步骤1：上传文件 */}
          {importStep === "upload" && (
            <div className="space-y-4 py-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium mb-2">
                  {language === "zh" ? "拖拽或点击上传Excel文件" : "Drag or click to upload Excel file"}
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  {language === "zh" ? "支持 .xlsx、.xls 格式" : "Supports .xlsx, .xls formats"}
                </p>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="excel-upload"
                />
                <label htmlFor="excel-upload">
                  <Button variant="outline" className="cursor-pointer" asChild>
                    <span><Upload className="w-4 h-4 mr-2" />{language === "zh" ? "选择文件" : "Choose File"}</span>
                  </Button>
                </label>
              </div>

              <div className="flex items-center justify-between bg-blue-50 rounded-lg p-4">
                <div>
                  <p className="text-sm font-medium text-blue-900">{language === "zh" ? "需要导入模板？" : "Need import template?"}</p>
                  <p className="text-xs text-blue-700 mt-1">
                    {language === "zh" 
                      ? "模板包含：序号、学生姓名、中方学号、英方学号、论文题目、导师、备注" 
                      : "Template includes: No., Student Name, Student ID, Sussex ID, Topic, Supervisor, Remarks"}
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={handleDownloadTemplate}>
                  <Download className="w-4 h-4 mr-2" />
                  {language === "zh" ? "下载模板" : "Download"}
                </Button>
              </div>

              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{language === "zh" ? "导入规则" : "Import Rules"}</AlertTitle>
                <AlertDescription className="text-sm space-y-1 mt-2">
                  <p>• {language === "zh" ? "学生和导师账号必须已在系统中注册，否则该行导入失败" : "Student and teacher accounts must be registered in the system"}</p>
                  <p>• {language === "zh" ? "课题名称不能与题库中三年内的已有课题重名，否则该行导入失败" : "Topic title must not duplicate with existing topics in the library (within 3 years)"}</p>
                  <p>• {language === "zh" ? "如有任何一行验证失败，整批数据将不会导入" : "If any row fails validation, the entire batch will not be imported"}</p>
                  <p>• {language === "zh" ? "导入成功后，课题将自动添加到题库，匹配关系自动建立" : "After import, topics are auto-added to library and matches are established"}</p>
                </AlertDescription>
              </Alert>
            </div>
          )}

          {/* 步骤2：预览确认 */}
          {importStep === "preview" && (
            <div className="space-y-4 py-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">
                  {language === "zh" ? `共解析 ${importData.length} 条记录` : `Parsed ${importData.length} records`}
                </p>
                <Button variant="ghost" size="sm" onClick={() => setImportStep("upload")}>
                  {language === "zh" ? "重新上传" : "Re-upload"}
                </Button>
              </div>
              
              <div className="overflow-x-auto max-h-[400px] overflow-y-auto border rounded-lg">
                <Table>
                  <TableHeader className="sticky top-0 bg-white z-10">
                    <TableRow>
                      <TableHead className="w-12">{language === "zh" ? "行" : "Row"}</TableHead>
                      <TableHead>{language === "zh" ? "学生姓名" : "Student"}</TableHead>
                      <TableHead>{language === "zh" ? "中方学号" : "ID"}</TableHead>
                      <TableHead>{language === "zh" ? "英方学号" : "Sussex ID"}</TableHead>
                      <TableHead>{language === "zh" ? "导师" : "Supervisor"}</TableHead>
                      <TableHead>{language === "zh" ? "论文题目" : "Topic"}</TableHead>
                      <TableHead>{language === "zh" ? "备注" : "Remarks"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {importData.map((item, i) => (
                      <TableRow key={i}>
                        <TableCell className="text-gray-500">{i + 2}</TableCell>
                        <TableCell className="font-medium">{item.studentName}</TableCell>
                        <TableCell className="font-mono text-sm">{item.studentId}</TableCell>
                        <TableCell className="font-mono text-sm">{item.sussexId || "-"}</TableCell>
                        <TableCell>{item.teacherName}</TableCell>
                        <TableCell className="max-w-xs truncate" title={item.topicTitle}>{item.topicTitle}</TableCell>
                        <TableCell className="text-sm text-gray-500">{item.remarks || "-"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setImportStep("upload")}>
                  {language === "zh" ? "返回" : "Back"}
                </Button>
                <Button onClick={handleBatchImport} disabled={batchImportMutation.isPending}>
                  {batchImportMutation.isPending ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{language === "zh" ? "导入中..." : "Importing..."}</>
                  ) : (
                    <><Upload className="w-4 h-4 mr-2" />{language === "zh" ? `确认导入 ${importData.length} 条` : `Import ${importData.length} records`}</>
                  )}
                </Button>
              </DialogFooter>
            </div>
          )}

          {/* 步骤3：导入结果 */}
          {importStep === "result" && importResult && (
            <div className="space-y-4 py-4">
              {importResult.success ? (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertTitle className="text-green-800">
                    {language === "zh" ? "导入成功" : "Import Successful"}
                  </AlertTitle>
                  <AlertDescription className="text-green-700">
                    {language === "zh" 
                      ? `共 ${importResult.totalCount} 条记录，全部导入成功。课题已自动添加到题库，匹配关系已建立。`
                      : `All ${importResult.totalCount} records imported successfully. Topics added to library and matches established.`}
                  </AlertDescription>
                </Alert>
              ) : (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertTitle>
                    {language === "zh" ? "导入失败" : "Import Failed"}
                  </AlertTitle>
                  <AlertDescription>
                    {language === "zh" 
                      ? `共 ${importResult.totalCount} 条记录，${importResult.failedCount} 条验证失败。由于存在错误，整批数据未导入。请修正以下问题后重新导入。`
                      : `${importResult.failedCount} of ${importResult.totalCount} records failed validation. No data was imported. Please fix the issues below and retry.`}
                  </AlertDescription>
                </Alert>
              )}

              {/* 统计卡片 */}
              <div className="grid grid-cols-3 gap-4">
                <Card className="bg-gray-50">
                  <CardContent className="pt-4 pb-4 text-center">
                    <p className="text-2xl font-bold">{importResult.totalCount}</p>
                    <p className="text-sm text-gray-500">{language === "zh" ? "总记录数" : "Total"}</p>
                  </CardContent>
                </Card>
                <Card className="bg-green-50">
                  <CardContent className="pt-4 pb-4 text-center">
                    <p className="text-2xl font-bold text-green-600">{importResult.successCount}</p>
                    <p className="text-sm text-green-600">{language === "zh" ? "成功" : "Success"}</p>
                  </CardContent>
                </Card>
                <Card className="bg-red-50">
                  <CardContent className="pt-4 pb-4 text-center">
                    <p className="text-2xl font-bold text-red-600">{importResult.failedCount}</p>
                    <p className="text-sm text-red-600">{language === "zh" ? "失败" : "Failed"}</p>
                  </CardContent>
                </Card>
              </div>

              {/* 错误详情 */}
              {importResult.errors.length > 0 && (
                <div className="border rounded-lg overflow-hidden">
                  <div className="bg-red-50 px-4 py-2 border-b">
                    <p className="text-sm font-medium text-red-800">
                      {language === "zh" ? "失败详情" : "Error Details"}
                    </p>
                  </div>
                  <div className="max-h-[300px] overflow-y-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-16">{language === "zh" ? "行号" : "Row"}</TableHead>
                          <TableHead>{language === "zh" ? "学生" : "Student"}</TableHead>
                          <TableHead>{language === "zh" ? "学号" : "ID"}</TableHead>
                          <TableHead>{language === "zh" ? "失败原因" : "Reason"}</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {importResult.errors.map((err, i) => (
                          <TableRow key={i}>
                            <TableCell className="font-mono">{err.row}</TableCell>
                            <TableCell>{err.studentName}</TableCell>
                            <TableCell className="font-mono text-sm">{err.studentId}</TableCell>
                            <TableCell className="text-red-600 text-sm">{err.reason}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}

              <DialogFooter>
                <Button onClick={resetImportDialog}>
                  {language === "zh" ? "关闭" : "Close"}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 撤回确认对话框 */}
      <Dialog open={revokeDialogOpen} onOpenChange={setRevokeDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              {language === "zh" ? "确认撤回匹配" : "Confirm Revoke Match"}
            </DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? "此操作将撤回该学生与导师的匹配关系。"
                : "This will revoke the match between the student and supervisor."}
            </DialogDescription>
          </DialogHeader>
          
          {selectedMatch && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>{language === "zh" ? "警告" : "Warning"}</AlertTitle>
              <AlertDescription>
                <div className="mt-2 space-y-1 text-sm">
                  <p><strong>{language === "zh" ? "学生：" : "Student: "}</strong>{selectedMatch.student?.name}</p>
                  <p><strong>{language === "zh" ? "导师：" : "Supervisor: "}</strong>{selectedMatch.teacher?.name}</p>
                  <p><strong>{language === "zh" ? "课题：" : "Topic: "}</strong>{selectedMatch.topic?.title}</p>
                </div>
                <div className="mt-3 text-sm">
                  {language === "zh" 
                    ? "撤回后：课题将恢复为'已发布'状态，学生志愿将恢复为待审核状态。"
                    : "After revoke: Topic will be restored to 'published' status, student's wish will be restored to pending status."}
                </div>
              </AlertDescription>
            </Alert>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setRevokeDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              variant="destructive" 
              onClick={confirmRevoke}
              disabled={revokeMutation.isPending}
            >
              {revokeMutation.isPending 
                ? (language === "zh" ? "撤回中..." : "Revoking...") 
                : (language === "zh" ? "确认撤回" : "Confirm Revoke")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 导出对话框 */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "导出匹配结果" : "Export Match Results"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? "导出格式参考《导师和论文信息汇总表》模板，包含学生信息、论文题目、指导教师等完整字段。"
                : "Export format follows the thesis information summary template with complete fields."}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-medium mb-2">{language === "zh" ? "导出字段包括：" : "Export fields include:"}</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• {language === "zh" ? "序号、学院、专业、学生班级" : "No., Faculty, Major, Class"}</li>
                <li>• {language === "zh" ? "导师姓名、学生中方学号、英方学号、学生姓名" : "Supervisor, Student ID, Candidate No., Name"}</li>
                <li>• {language === "zh" ? "论文类型、论文题目、论文关键词" : "Thesis Type, Title, Keywords"}</li>
                <li>• {language === "zh" ? "论文选题来源、论文研究方向、论文撰写语种" : "Topic Source, Research Interests, Language"}</li>
                <li>• {language === "zh" ? "成绩、备注" : "Score, Remarks"}</li>
              </ul>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExportDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleExport} disabled={isExporting}>
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              {isExporting 
                ? (language === "zh" ? "导出中..." : "Exporting...") 
                : (language === "zh" ? "导出Excel" : "Export Excel")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
