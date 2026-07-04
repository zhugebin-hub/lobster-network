import { useState, useRef } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, Upload, Download, FileSpreadsheet, CheckCircle, AlertTriangle, XCircle, Users } from "lucide-react";
import * as XLSX from "xlsx";
import { useEffect } from "react";

export default function AdminProxyImport() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  
  const [importFile, setImportFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [autoPublish, setAutoPublish] = useState(false);
  const [importErrors, setImportErrors] = useState<{row: number; field: string; message: string}[]>([]);
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [importResult, setImportResult] = useState<{success: number; failed: number; total: number; errors?: string[]}>({success: 0, failed: 0, total: 0});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const utils = trpc.useUtils();
  const { data: teacherList } = trpc.admin.getTeacherList.useQuery(undefined, { enabled: isAuthenticated && user?.role === "admin" });

  useEffect(() => {
    if (!loading && (!isAuthenticated || (user && user.role !== "admin"))) {
      setLocation("/login");
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const proxyImportMutation = trpc.admin.proxyBulkImport.useMutation({
    onSuccess: (result) => {
      const total = (result.success || 0) + (result.failed || 0);
      setImportResult({ success: result.success, failed: result.failed, total, errors: result.errors });
      setIsImporting(false);
      
      if (result.failed > 0 && result.success > 0) {
        // 部分成功：展示错误弹窗（含成功摘要）
        const backendErrors = (result.errors || []).map((errStr: string) => {
          const match = errStr.match(/^第(\d+)行:\s*(.+)$/);
          if (match) {
            return { row: parseInt(match[1]), field: language === "zh" ? "导入验证" : "Import Validation", message: match[2] };
          }
          return { row: 0, field: language === "zh" ? "系统" : "System", message: errStr };
        });
        setImportErrors(backendErrors);
        setShowErrorDialog(true);
      } else if (result.failed > 0) {
        // 全部失败
        const backendErrors = (result.errors || []).map((errStr: string) => {
          const match = errStr.match(/^第(\d+)行:\s*(.+)$/);
          if (match) {
            return { row: parseInt(match[1]), field: language === "zh" ? "导入验证" : "Import Validation", message: match[2] };
          }
          return { row: 0, field: language === "zh" ? "系统" : "System", message: errStr };
        });
        setImportErrors(backendErrors);
        setShowErrorDialog(true);
      } else {
        // 全部成功
        setShowSuccessDialog(true);
      }
      
      setShowPreview(false);
      setPreviewData([]);
      setImportFile(null);
    },
    onError: (error) => {
      setIsImporting(false);
      const errMsg = error.message || "";
      let userFriendlyErrors: {row: number; field: string; message: string}[] = [];
      
      if (errMsg.includes("UNAUTHORIZED") || errMsg.includes("401")) {
        userFriendlyErrors = [{ row: 0, field: language === "zh" ? "权限" : "Permission", message: language === "zh" ? "登录已过期，请重新登录后再试" : "Session expired, please log in again" }];
      } else if (errMsg.includes("FORBIDDEN") || errMsg.includes("403")) {
        userFriendlyErrors = [{ row: 0, field: language === "zh" ? "权限" : "Permission", message: language === "zh" ? "您没有管理员权限执行此操作" : "You don't have admin permission" }];
      } else {
        userFriendlyErrors = [{ row: 0, field: language === "zh" ? "系统" : "System", message: errMsg || (language === "zh" ? "导入过程中发生未知错误" : "Unknown error during import") }];
      }
      
      setImportErrors(userFriendlyErrors);
      setShowErrorDialog(true);
    },
  });

  const handleLogout = async () => { await logout(); setLocation("/"); };

  // 选题来源完整列表（中英文对照）
  const topicSourceOptions = [
    { zh: "国家重点研发计划项目", en: "National Key R&D Program" },
    { zh: "国家社科规划、基金项目", en: "National Social Science Fund" },
    { zh: "国家自然科学基金项目", en: "National Natural Science Foundation" },
    { zh: "中央、国家各部门项目", en: "Central Government Projects" },
    { zh: "教育部人文、社会科学研究项目", en: "MOE Humanities & Social Science" },
    { zh: "省(自治区、直辖市)项目", en: "Provincial/Municipal Projects" },
    { zh: "国际合作研究项目", en: "International Cooperation" },
    { zh: "与港、澳、台合作研究项目", en: "HK/Macau/Taiwan Cooperation" },
    { zh: "企、事业单位委托项目", en: "Enterprise Commissioned" },
    { zh: "外资项目", en: "Foreign-funded Projects" },
    { zh: "国防项目", en: "National Defense Projects" },
    { zh: "学校自选项目", en: "University Self-selected" },
    { zh: "非立项", en: "Non-project" },
    { zh: "科研项目（萨塞克斯老师适用）", en: "Research Project (for Sussex only)" },
    { zh: "其他", en: "Others" },
  ];

  // 适合专业选项映射
  const majorMapping: Record<string, string> = {
    "All Courses": "both",
    "All Majors": "both",
    "不限专业": "both",
    "Robotics and Electrical Engineering": "electronic_info",
    "电子信息工程": "electronic_info",
    "Communications Engineering": "communication",
    "通信工程": "communication",
    "both": "both",
    "electronic_info": "electronic_info",
    "communication": "communication",
  };

  // 选题来源英文→中文映射
  const topicSourceEnToZh: Record<string, string> = {};
  topicSourceOptions.forEach(opt => {
    topicSourceEnToZh[opt.en] = opt.zh;
    topicSourceEnToZh[opt.zh] = opt.zh;
  });
  topicSourceEnToZh["Other"] = "其他";

  // 下载模板
  const TEMPLATE_URL = "/files/templates/批量导入.xlsx";
  const downloadTemplate = () => {
    const link = document.createElement("a");
    link.href = TEMPLATE_URL;
    link.download = "批量导入.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success(language === "zh" ? "模板下载成功" : "Template downloaded");
  };

  // 根据邮箱/登录名匹配导师
  const findTeacher = (identifier: string) => {
    if (!teacherList || !identifier) return null;
    const trimmed = identifier.trim().toLowerCase();
    return teacherList.find(t => 
      (t.email && t.email.toLowerCase() === trimmed) || 
      (t.name && t.name.toLowerCase() === trimmed)
    ) || null;
  };

  // 处理文件导入
  const handleFileImport = async () => {
    if (!importFile) {
      toast.error(language === "zh" ? "请先选择文件" : "Please select a file");
      return;
    }
    
    setIsImporting(true);
    
    try {
      const arrayBuffer = await importFile.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];
      
      if (jsonData.length < 2) {
        toast.error(language === "zh" ? "文件中没有有效数据" : "No valid data in file");
        setIsImporting(false);
        return;
      }
      
      let topics: any[] = [];
      
      // 检查第一列标题是否包含"导师"或"Teacher"来判断是否为代理导入模板
      const headerRow = jsonData[0] || [];
      const firstHeader = String(headerRow[0] || "").trim();
      const hasTeacherColumn = firstHeader.includes("导师") || firstHeader.toLowerCase().includes("teacher") || firstHeader.toLowerCase().includes("email") || firstHeader.includes("萨塞克斯邮箱") || firstHeader.toLowerCase().includes("sussex");
      
      if (hasTeacherColumn) {
        // 代理导入模板：第1列为导师邮箱/登录名，后续列与标准模板一致
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i];
          if (!row || row.length === 0) continue;
          
          const firstCell = String(row[0] || "").trim();
          if (!firstCell || firstCell.startsWith("说明") || firstCell.startsWith("Instructions") || /^\d+\./.test(firstCell)) continue;
          
          const rawTopicSource = String(row[5] || "").trim();
          const mappedTopicSource = topicSourceEnToZh[rawTopicSource] || rawTopicSource || "其他";
          const rawMajor = String(row[7] || "").trim();
          const mappedMajor = (majorMapping[rawMajor] || "both") as "electronic_info" | "communication" | "both";
          
          topics.push({
            teacherEmail: firstCell,
            titleEn: String(row[1] || "").trim(),
            title: "",
            descriptionEn: String(row[2] || "").trim(),
            description: "",
            keywords: String(row[3] || "").trim(),
            researchFocus: String(row[4] || "").trim(),
            topicSource: mappedTopicSource,
            researchProjectName: String(row[6] || "").trim(),
            suitableMajor: mappedMajor,
            requiredSkills: String(row[8] || "").trim(),
          });
        }
      } else {
        // 标准模板：没有导师列，需要在预览时手动指定
        // 但对于代理导入，我们要求必须有导师信息
        // 尝试按标准模板解析，但要求用户在模板中添加导师列
        toast.error(language === "zh" 
          ? "请使用代理导入专用模板（第1列为萨塞克斯邮箱）。请下载《批量导入》模板填写。" 
          : "Please use the proxy import template (Column 1 = Sussex Email). Download the import template to fill in.");
        setIsImporting(false);
        return;
      }
      
      if (topics.length === 0) {
        toast.error(language === "zh" ? "没有找到有效的课题数据" : "No valid topic data found");
        setIsImporting(false);
        return;
      }
      
      // 前端逐行验证
      const validationErrors = validateImportData(topics);
      if (validationErrors.length > 0) {
        setImportErrors(validationErrors);
        setShowErrorDialog(true);
        setIsImporting(false);
        return;
      }
      
      setPreviewData(topics);
      setShowPreview(true);
      setIsImporting(false);
      toast.success(language === "zh" ? `解析成功，共${topics.length}条课题，请确认后导入` : `Parsed ${topics.length} topics, please confirm before import`);
    } catch (error: any) {
      toast.error(language === "zh" ? `解析文件失败: ${error.message}` : `Failed to parse file: ${error.message}`);
      setIsImporting(false);
    }
  };

  // 确认导入
  const handleConfirmImport = () => {
    if (previewData.length === 0) return;
    setIsImporting(true);
    proxyImportMutation.mutate({ topics: previewData, autoPublish });
  };

  // 取消预览
  const handleCancelPreview = () => {
    setPreviewData([]);
    setShowPreview(false);
    setImportFile(null);
    setImportErrors([]);
  };

  // 逐行验证导入数据
  const validateImportData = (topics: any[]): {row: number; field: string; message: string}[] => {
    const errors: {row: number; field: string; message: string}[] = [];
    const isZh = language === "zh";
    
    topics.forEach((topic, index) => {
      const rowNum = index + 2;
      
      // 导师邮箱验证
      if (!topic.teacherEmail || !topic.teacherEmail.trim()) {
        errors.push({ row: rowNum, field: isZh ? "导师邮箱/登录名" : "Teacher Email", message: isZh ? "导师邮箱/登录名字段内容未填写" : "Teacher Email field content is not filled in" });
      } else {
        const teacher = findTeacher(topic.teacherEmail);
        if (!teacher) {
          errors.push({ row: rowNum, field: isZh ? "导师邮箱/登录名" : "Teacher Email", message: isZh ? `未找到导师账号"${topic.teacherEmail}"，请确认该导师已在系统中注册` : `Teacher account "${topic.teacherEmail}" not found, please confirm registration` });
        }
      }
      
      // 课题标题（英文）验证
      if (!topic.titleEn || !topic.titleEn.trim()) {
        errors.push({ row: rowNum, field: isZh ? "课题标题（英文）" : "Title (English)", message: isZh ? "课题标题（英文）字段内容未填写" : "Title (English) field content is not filled in" });
      }
      
      // 课题描述（英文）验证
      if (!topic.descriptionEn || !topic.descriptionEn.trim()) {
        errors.push({ row: rowNum, field: isZh ? "课题描述（英文）" : "Description (English)", message: isZh ? "课题描述（英文）字段内容未填写" : "Description (English) field content is not filled in" });
      }
      
      // 论文关键词验证
      if (!topic.keywords || !topic.keywords.trim()) {
        errors.push({ row: rowNum, field: isZh ? "论文关键词" : "Keywords", message: isZh ? "论文关键词字段内容未填写" : "Keywords field content is not filled in" });
      } else {
        const kwList = topic.keywords.split(/[,，]/).map((k: string) => k.trim()).filter((k: string) => k);
        if (kwList.length < 3 || kwList.length > 5) {
          errors.push({ row: rowNum, field: isZh ? "论文关键词" : "Keywords", message: isZh ? `论文关键词字段要求填写3-5个关键词，当前填写了${kwList.length}个` : `Keywords field requires 3-5 keywords, currently ${kwList.length} provided` });
        }
      }
      
      // 研究方向验证
      if (!topic.researchFocus || !topic.researchFocus.trim()) {
        errors.push({ row: rowNum, field: isZh ? "研究方向" : "Research Interests", message: isZh ? "研究方向字段内容未填写" : "Research Interests field content is not filled in" });
      } else {
        const rfList = topic.researchFocus.split(/[,，]/).map((r: string) => r.trim()).filter((r: string) => r);
        if (rfList.length > 2) {
          errors.push({ row: rowNum, field: isZh ? "研究方向" : "Research Interests", message: isZh ? `研究方向字段最多填写2个方向，当前填写了${rfList.length}个` : `Research Interests field allows max 2 directions, currently ${rfList.length} provided` });
        }
      }
      
      // 科研项目名称验证
      const source = topic.topicSource || "其他";
      if ((source === "其他" || source === "科研项目（萨塞克斯老师适用）") && topic.researchProjectName && topic.researchProjectName.trim()) {
        errors.push({ row: rowNum, field: isZh ? "科研项目名称" : "Research Project Name", message: isZh ? `选题来源为"${source}"时，科研项目名称字段必须为空` : `When Topic Source is "${source}", the Research Project Name field must be empty` });
      }
      if (source !== "其他" && source !== "科研项目（萨塞克斯老师适用）" && (!topic.researchProjectName || !topic.researchProjectName.trim())) {
        errors.push({ row: rowNum, field: isZh ? "科研项目名称" : "Research Project Name", message: isZh ? `科研项目名称字段内容未填写（选题来源为"${source}"时必须填写此字段）` : `Research Project Name field content is not filled in (required when Topic Source is "${source}")` });
      }
    });
    
    return errors;
  };

  // 获取导师匹配状态
  const getTeacherMatchStatus = (email: string) => {
    const teacher = findTeacher(email);
    if (!teacher) return { status: "error" as const, label: language === "zh" ? "未找到" : "Not Found" };
    return { status: "success" as const, label: teacher.name || email, teacher };
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  const isZh = language === "zh";

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => setLocation("/admin")}><ArrowLeft className="w-4 h-4 mr-2" />{isZh ? "返回" : "Back"}</Button>
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center"><GraduationCap className="w-6 h-6 text-white" /></div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.name} ({t.roles.admin})</span>
            <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}><Globe className="w-4 h-4 mr-2" />{language === "zh" ? "EN" : "中"}</Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}><LogOut className="w-4 h-4 mr-2" />{t.logout}</Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{isZh ? "代理导入课题" : "Proxy Import Topics"}</h1>
          <p className="text-gray-600 mt-1">{isZh ? "代替导师批量创建和发布课题，适用于多位导师共同提交课题的场景" : "Bulk create and publish topics on behalf of teachers"}</p>
        </div>

        {/* 导师统计 */}
        {teacherList && (
          <div className="grid grid-cols-3 gap-4 mb-6">
            <Card>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="text-sm text-gray-500">{isZh ? "系统导师总数" : "Total Teachers"}</div>
                    <div className="text-xl font-bold">{teacherList.length}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <div>
                    <div className="text-sm text-gray-500">{isZh ? "可发布导师" : "Can Publish"}</div>
                    <div className="text-xl font-bold text-green-600">{teacherList.filter(t => t.canPublish !== 0).length}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 pb-4">
                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 text-red-600" />
                  <div>
                    <div className="text-sm text-gray-500">{isZh ? "已禁止发布" : "Publish Disabled"}</div>
                    <div className="text-xl font-bold text-red-600">{teacherList.filter(t => t.canPublish === 0).length}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {!showPreview ? (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                {isZh ? "上传课题文件" : "Upload Topic File"}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* 步骤1：下载模板 */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-800 flex items-center gap-2 mb-2">
                  <FileSpreadsheet className="w-4 h-4" />
                  {isZh ? "步骤 1：下载模板" : "Step 1: Download Template"}
                </h3>
                <p className="text-sm text-blue-700 mb-3">
                  {isZh 
                    ? "下载《批量导入》模板，第1列为萨塞克斯邮箱，第2列起为课题信息，直接填写即可。" 
                    : "Download the import template. Column 1 is Sussex Email, followed by topic information."}
                </p>
                <div className="flex gap-3">
                  <Button variant="outline" size="sm" onClick={downloadTemplate}>
                    <Download className="w-4 h-4 mr-2" />{isZh ? "下载《批量导入》模板" : "Download Import Template"}
                  </Button>
                </div>
                <div className="mt-3 text-xs text-blue-600 bg-blue-100 rounded p-2">
                  {isZh 
                    ? "模板格式：第1列=萨塞克斯邮箱，第2列=课程标题(英文)，第3列=课题描述(英文)，第4列=关键词，第5列=研究方向，第6列=选题来源，第7列=科研项目名称，第8列=适合专业，第9列=技能要求" 
                    : "Format: Col1=Sussex Email, Col2=Title(EN), Col3=Description(EN), Col4=Keywords, Col5=Research Interests, Col6=Topic Source, Col7=Project Name, Col8=Major, Col9=Skills"}
                </div>
              </div>

              {/* 步骤2：上传文件 */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-medium text-gray-800 flex items-center gap-2 mb-2">
                  <Upload className="w-4 h-4" />
                  {isZh ? "步骤 2：上传文件" : "Step 2: Upload File"}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  {isZh ? "选择填写好的 Excel 文件进行导入" : "Select the filled Excel file to import"}
                </p>
                <div className="flex items-center gap-3">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls"
                    className="hidden"
                    onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    {isZh ? "选择文件" : "Choose File"}
                  </Button>
                  <span className="text-sm text-gray-500">
                    {importFile ? importFile.name : (isZh ? "未选择文件" : "No file chosen")}
                  </span>
                </div>
                {importFile && (
                  <p className="text-sm text-green-600 mt-2">
                    {isZh ? `已选择: ${importFile.name}` : `Selected: ${importFile.name}`}
                  </p>
                )}
              </div>

              {/* 步骤3：导入选项 */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h3 className="font-medium text-amber-800 flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4" />
                  {isZh ? "步骤 3：导入选项" : "Step 3: Import Options"}
                </h3>
                <div className="flex items-center gap-3 mt-3">
                  <Switch
                    id="auto-publish"
                    checked={autoPublish}
                    onCheckedChange={setAutoPublish}
                  />
                  <Label htmlFor="auto-publish" className="text-sm cursor-pointer">
                    {isZh ? "自动发布课题（创建后直接发布，无需导师手动操作）" : "Auto-publish topics (publish immediately after creation)"}
                  </Label>
                </div>
                {autoPublish && (
                  <p className="text-xs text-amber-700 mt-2 bg-amber-100 rounded p-2">
                    <AlertTriangle className="w-3 h-3 inline mr-1" />
                    {isZh 
                      ? "开启自动发布后，课题将直接进入已发布状态，学生可以看到并选择这些课题。中方导师的课题数量将受年度限额限制。" 
                      : "With auto-publish enabled, topics will be published immediately and visible to students. ZJSU teacher topics are subject to annual quota limits."}
                  </p>
                )}
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setLocation("/admin")}>{isZh ? "取消" : "Cancel"}</Button>
                <Button onClick={handleFileImport} disabled={!importFile || isImporting}>
                  {isImporting ? (isZh ? "解析中..." : "Parsing...") : (isZh ? "解析文件" : "Parse File")}
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          /* 预览区域 */
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{isZh ? `预览数据 (${previewData.length} 条)` : `Preview Data (${previewData.length} items)`}</span>
                <div className="flex items-center gap-2">
                  {autoPublish && (
                    <Badge variant="default" className="bg-green-600">
                      {isZh ? "自动发布" : "Auto Publish"}
                    </Badge>
                  )}
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                <table className="w-full text-sm border-collapse">
                  <thead className="sticky top-0 bg-gray-100">
                    <tr>
                      <th className="border p-2 text-left">#</th>
                      <th className="border p-2 text-left">{isZh ? "导师" : "Teacher"}</th>
                      <th className="border p-2 text-left">{isZh ? "匹配状态" : "Match Status"}</th>
                      <th className="border p-2 text-left">{isZh ? "课题标题（英文）" : "Title (EN)"}</th>
                      <th className="border p-2 text-left">{isZh ? "关键词" : "Keywords"}</th>
                      <th className="border p-2 text-left">{isZh ? "研究方向" : "Research Interests"}</th>
                      <th className="border p-2 text-left">{isZh ? "选题来源" : "Topic Source"}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.map((topic, i) => {
                      const matchStatus = getTeacherMatchStatus(topic.teacherEmail);
                      return (
                        <tr key={i} className={matchStatus.status === "error" ? "bg-red-50" : ""}>
                          <td className="border p-2">{i + 1}</td>
                          <td className="border p-2 font-mono text-xs">{topic.teacherEmail}</td>
                          <td className="border p-2">
                            {matchStatus.status === "success" ? (
                              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
                                <CheckCircle className="w-3 h-3 mr-1" />{matchStatus.label}
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="bg-red-50 text-red-700 border-red-300">
                                <XCircle className="w-3 h-3 mr-1" />{matchStatus.label}
                              </Badge>
                            )}
                          </td>
                          <td className="border p-2 max-w-[200px] truncate" title={topic.titleEn}>{topic.titleEn}</td>
                          <td className="border p-2 max-w-[150px] truncate" title={topic.keywords}>{topic.keywords}</td>
                          <td className="border p-2 max-w-[120px] truncate" title={topic.researchFocus}>{topic.researchFocus}</td>
                          <td className="border p-2 text-xs">{isZh ? topic.topicSource : (topicSourceOptions.find(o => o.zh === topic.topicSource)?.en || topic.topicSource)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              <div className="flex justify-end gap-3 mt-4">
                <Button variant="outline" onClick={handleCancelPreview}>{isZh ? "取消" : "Cancel"}</Button>
                <Button onClick={handleConfirmImport} disabled={isImporting} className="bg-blue-600 hover:bg-blue-700">
                  {isImporting ? (isZh ? "导入中..." : "Importing...") : (isZh ? `确认导入 (${previewData.length} 条)` : `Confirm Import (${previewData.length})`)}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      {/* 错误详情弹窗 */}
      <Dialog open={showErrorDialog} onOpenChange={setShowErrorDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              {isZh ? "导入错误详情" : "Import Error Details"}
            </DialogTitle>
          </DialogHeader>
          
          {importResult.success > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
              <div className="flex items-center gap-2 text-green-700">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium">
                  {isZh ? `${importResult.success} 条课题已成功导入` : `${importResult.success} topics imported successfully`}
                </span>
              </div>
            </div>
          )}
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-3">
            <div className="flex items-center gap-2 text-red-700">
              <XCircle className="w-4 h-4" />
              <span className="font-medium">
                {isZh ? `发现 ${importErrors.length} 个错误，请根据以下信息修改后重新导入。` : `Found ${importErrors.length} error(s), please fix and re-import.`}
              </span>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border p-2 text-left w-16">{isZh ? "行号" : "Row"}</th>
                  <th className="border p-2 text-left w-32">{isZh ? "字段" : "Field"}</th>
                  <th className="border p-2 text-left">{isZh ? "错误说明" : "Error Description"}</th>
                </tr>
              </thead>
              <tbody>
                {importErrors.map((err, i) => (
                  <tr key={i}>
                    <td className="border p-2">{err.row > 0 ? (isZh ? `第 ${err.row} 行` : `Row ${err.row}`) : "-"}</td>
                    <td className="border p-2 font-medium">{err.field}</td>
                    <td className="border p-2 text-red-600">{err.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="flex justify-end mt-4">
            <Button onClick={() => setShowErrorDialog(false)}>{isZh ? "关闭" : "Close"}</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* 成功弹窗 */}
      <Dialog open={showSuccessDialog} onOpenChange={setShowSuccessDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader className="sr-only"><DialogTitle>{isZh ? "导入成功" : "Import Successful"}</DialogTitle></DialogHeader>
          <div className="flex flex-col items-center py-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-green-700 mb-2">
              {isZh ? "导入成功" : "Import Successful"}
            </h2>
            <div className="text-center">
              <span className="text-4xl font-bold text-green-600">{importResult.success}</span>
              <p className="text-gray-600 mt-1">
                {isZh ? "条课题已成功导入系统" : "topics imported successfully"}
              </p>
              {autoPublish && (
                <p className="text-sm text-green-600 mt-2 bg-green-50 rounded px-3 py-1">
                  {isZh ? "所有课题已自动发布" : "All topics have been auto-published"}
                </p>
              )}
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4 w-full mt-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">{isZh ? "文件总数据" : "Total in file"}</span>
                <span className="font-medium">{importResult.total} {isZh ? "条" : "items"}</span>
              </div>
              <div className="flex justify-between text-sm mt-1">
                <span className="text-gray-500">{isZh ? "成功导入" : "Imported"}</span>
                <span className="font-medium text-green-600">{importResult.success} {isZh ? "条" : "items"}</span>
              </div>
            </div>
          </div>
          <div className="flex justify-end">
            <Button onClick={() => { setShowSuccessDialog(false); }}>{isZh ? "完成" : "Done"}</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
