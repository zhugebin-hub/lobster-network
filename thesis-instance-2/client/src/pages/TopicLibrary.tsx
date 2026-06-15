import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { Plus, Edit, Trash2, Send, ArrowLeft, GraduationCap, Globe, LogOut, Undo2, Users, Filter, Calendar, Upload, Download, FileSpreadsheet } from "lucide-react";
import * as XLSX from "xlsx";

export default function TopicLibrary() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTopic, setEditingTopic] = useState<any>(null);
  const [title, setTitle] = useState("");
  const [titleEn, setTitleEn] = useState("");
  const [description, setDescription] = useState("");
  const [descriptionEn, setDescriptionEn] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [suitableMajor, setSuitableMajor] = useState<"electronic_info" | "communication" | "both">("both");
  const [keywords, setKeywords] = useState("");
  const [researchFocus, setResearchFocus] = useState("");
  const [thesisType, setThesisType] = useState("毕业设计");
  const [topicSource, setTopicSource] = useState("其他");
  const [topicLanguage, setTopicLanguage] = useState("英语");
  const [researchProjectName, setResearchProjectName] = useState("");
  const [yearFilter, setYearFilter] = useState<string>("current");
  const [isBulkImportOpen, setIsBulkImportOpen] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [importErrors, setImportErrors] = useState<{row: number; field: string; message: string}[]>([]);
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [importResult, setImportResult] = useState<{success: number; failed: number; total: number}>({success: 0, failed: 0, total: 0});

  const utils = trpc.useUtils();
  const { data: topics, isLoading } = trpc.topic.myTopics.useQuery(undefined, { enabled: isAuthenticated });
  const { data: currentYear } = trpc.admin.getCurrentYear.useQuery(undefined, { enabled: isAuthenticated });
  const { data: timePhase } = trpc.admin.getCurrentPhase.useQuery(undefined, { enabled: isAuthenticated });

  const createMutation = trpc.topic.create.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "课题创建成功" : "Topic created"); utils.topic.myTopics.invalidate(); resetForm(); },
    onError: (e) => toast.error(e.message),
  });

  const updateMutation = trpc.topic.update.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "课题更新成功" : "Topic updated"); utils.topic.myTopics.invalidate(); resetForm(); },
    onError: (e) => toast.error(e.message),
  });

  const deleteMutation = trpc.topic.delete.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "课题已删除" : "Topic deleted"); utils.topic.myTopics.invalidate(); },
    onError: (e) => toast.error(e.message),
  });

  const publishMutation = trpc.topic.publish.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "课题已发布" : "Topic published"); utils.topic.myTopics.invalidate(); },
    onError: (e) => toast.error(e.message),
  });

  const unpublishMutation = trpc.topic.unpublish.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "课题已撤回" : "Topic unpublished"); utils.topic.myTopics.invalidate(); },
    onError: (e) => toast.error(e.message),
  });

  const bulkImportMutation = trpc.topic.bulkImport.useMutation({
    onSuccess: (result) => {
      const total = (result.success || 0) + (result.failed || 0);
      setImportResult({ success: result.success || 0, failed: result.failed || 0, total });
      
      if (result.failed > 0) {
        // 部分失败：解析后端错误字符串，提取行号和具体原因
        const backendErrors = (result.errors || []).map((errStr: any, idx: number) => {
          const errText = typeof errStr === "string" ? errStr : (errStr?.error || errStr?.message || "");
          // 后端返回格式为 "第X行: 具体错误信息"
          const rowMatch = errText.match(/第(\d+)行[:\uff1a]\s*(.*)/);
          let rowNum = idx + 1;
          let reason = errText;
          if (rowMatch) {
            rowNum = parseInt(rowMatch[1]);
            reason = rowMatch[2];
          }
          
          // 将后端错误信息转换为用户可理解的描述
          let field = "";
          let message = reason;
          
          if (reason.includes("英文标题不能为空") || reason.includes("标题已存在")) {
            field = language === "zh" ? "课题标题" : "Topic Title";
            if (reason.includes("标题已存在于题库中")) {
              message = language === "zh" ? `该课题标题已存在于题库中，${reason.match(/\uff08.*?\uff09/)?.[0] || ""}` : `This topic title already exists in the library`;
            } else {
              message = language === "zh" ? "课题标题（英文）字段内容未填写" : "Title (English) field content is not filled in";
            }
          } else if (reason.includes("英文描述不能为空")) {
            field = language === "zh" ? "课题描述" : "Description";
            message = language === "zh" ? "课题描述（英文）字段内容未填写" : "Description (English) field content is not filled in";
          } else if (reason.includes("关键词不能为空")) {
            field = language === "zh" ? "论文关键词" : "Keywords";
            message = language === "zh" ? "论文关键词字段内容未填写" : "Keywords field content is not filled in";
          } else if (reason.includes("研究方向不能为空")) {
            field = language === "zh" ? "研究方向" : "Research Interests";
            message = language === "zh" ? "研究方向字段内容未填写" : "Research Interests field content is not filled in";
          } else if (reason.includes("科研项目名称必填")) {
            field = language === "zh" ? "科研项目名称" : "Research Project Name";
            message = language === "zh" ? "科研项目名称字段内容未填写（选题来源非“其他”时必须填写）" : "Research Project Name field is not filled in (required when source is not 'Other')";
          } else if (reason.includes("发布权限")) {
            field = language === "zh" ? "权限" : "Permission";
            message = language === "zh" ? "您的发布权限已被禁止，无法导入课题，请联系管理员" : "Your publishing permission is disabled, please contact admin";
          } else {
            // 其他未识别的错误，直接展示原始信息
            field = language === "zh" ? "数据验证" : "Data Validation";
          }
          
          return { row: rowNum + 1, field, message }; // +1 因为 Excel 第1行是标题
        });
        setImportErrors(backendErrors);
        setShowErrorDialog(true);
      } else {
        // 全部成功：展示成功弹窗
        setShowSuccessDialog(true);
        setIsBulkImportOpen(false);
        setImportFile(null);
        setPreviewData([]);
        setShowPreview(false);
      }
      utils.topic.myTopics.invalidate();
      setIsImporting(false);
    },
    onError: (e) => {
      let userMessage = e.message;
      // 将常见的技术错误转换为用户可理解的描述
      if (e.message.includes("FORBIDDEN") || e.message.includes("发布权限")) {
        userMessage = language === "zh" ? "您的发布权限已被禁止，无法导入课题，请联系管理员" : "Your publishing permission is disabled, please contact admin";
      } else if (e.message.includes("UNAUTHORIZED")) {
        userMessage = language === "zh" ? "登录已过期，请重新登录后再试" : "Session expired, please login again";
      } else if (e.message.includes("network") || e.message.includes("timeout")) {
        userMessage = language === "zh" ? "网络连接异常，请检查网络后重试" : "Network error, please check connection and retry";
      }
      setImportErrors([{ row: 0, field: language === "zh" ? "导入失败" : "Import Failed", message: userMessage }]);
      setShowErrorDialog(true);
      setIsImporting(false);
    },
  });

  const resetForm = () => {
    setEditingTopic(null); setTitle(""); setTitleEn(""); setDescription(""); setDescriptionEn(""); setRequiredSkills(""); setSuitableMajor("both"); setKeywords(""); setResearchFocus(""); setThesisType("毕业设计"); setTopicSource("其他"); setTopicLanguage("英语"); setResearchProjectName(""); setIsDialogOpen(false);
  };

  const handleEdit = (topic: any) => {
    setEditingTopic(topic); setTitle(topic.title); setTitleEn(topic.titleEn || ""); setDescription(topic.description); setDescriptionEn(topic.descriptionEn || ""); setRequiredSkills(topic.requiredSkills || ""); setSuitableMajor(topic.suitableMajor || "both"); setKeywords(topic.keywords || ""); setResearchFocus(topic.researchFocus || ""); setThesisType(topic.thesisType || "毕业设计"); setTopicSource(topic.topicSource || "其他"); setTopicLanguage(topic.topicLanguage || "英语"); setResearchProjectName(topic.researchProjectName || ""); setIsDialogOpen(true);
  };

  // 验证关键词（3-5个，不能与题目完全相同，必填）
  const validateKeywords = (kw: string): boolean => {
    if (!kw.trim()) {
      toast.error(language === "zh" ? "论文关键词为必填项" : "Keywords are required");
      return false;
    }
    const kwList = kw.split(/[,，]/).map(k => k.trim()).filter(k => k);
    if (kwList.length < 3 || kwList.length > 5) {
      toast.error(language === "zh" ? "论文关键词需要3-5个" : "Keywords must be 3-5");
      return false;
    }
    if (kwList.some(k => k === titleEn.trim())) {
      toast.error(language === "zh" ? "关键词不能与题目完全相同" : "Keywords cannot be identical to title");
      return false;
    }
    return true;
  };

  // 验证研究方向（最多2个，不能与专业名称完全相同，必填）
  const validateResearchFocus = (rf: string): boolean => {
    if (!rf.trim()) {
      toast.error(language === "zh" ? "研究方向为必填项" : "Research interests is required");
      return false;
    }
    const rfList = rf.split(/[,，]/).map(r => r.trim()).filter(r => r);
    if (rfList.length > 2) {
      toast.error(language === "zh" ? "研究方向最多2个" : "Research interests max 2");
      return false;
    }
    const majorNames = ["电子信息工程", "通信工程", "Electronic Information Engineering", "Communication Engineering"];
    if (rfList.some(r => majorNames.includes(r))) {
      toast.error(language === "zh" ? "研究方向不能与专业名称完全相同" : "Research interests cannot be identical to major name");
      return false;
    }
    return true;
  };

  const handleSubmit = () => {
    // 英文标题和英文描述必填
    if (!titleEn || !descriptionEn) { toast.error(language === "zh" ? "请填写课题标题和课题描述" : "Please fill title and description"); return; }
    // 验证：如果选题来源不是"其他"且不是"科研项目（萨塞克斯老师适用）"，则researchProjectName必填
    if (topicSource !== "其他" && topicSource !== "科研项目（萨塞克斯老师适用）" && (!researchProjectName || !researchProjectName.trim())) { toast.error(language === "zh" ? "请填写科研项目名称" : "Research project name is required"); return; }
    if (!validateKeywords(keywords)) return;
    if (!validateResearchFocus(researchFocus)) return;
    if (editingTopic) {
      updateMutation.mutate({ id: editingTopic.id, title, titleEn, description, descriptionEn, requiredSkills, suitableMajor, keywords, researchFocus, thesisType, topicSource, topicLanguage, researchProjectName });
    } else {
      createMutation.mutate({ title, titleEn, description, descriptionEn, requiredSkills, suitableMajor, keywords, researchFocus, thesisType, topicSource, topicLanguage, researchProjectName });
    }
  };

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

  // 选题来源英文→中文映射（用于导入时转换）
  const topicSourceEnToZh: Record<string, string> = {};
  topicSourceOptions.forEach(opt => {
    topicSourceEnToZh[opt.en] = opt.zh;
    topicSourceEnToZh[opt.zh] = opt.zh; // 中文也映射到自身
  });
  // 兼容映射：旧模板中 "Other" 也能正确识别为“其他”
  topicSourceEnToZh["Other"] = "其他";

  // 下载Excel模板（直接下载原始模板文件）
  const TEMPLATE_URL = "/files/templates/导师课题导入.xlsx";
  const downloadTemplate = () => {
    const link = document.createElement("a");
    link.href = TEMPLATE_URL;
    link.download = "导师课题导入.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success(language === "zh" ? "模板下载成功" : "Template downloaded");
  };

  // 处理文件导入
  const handleFileImport = async () => {
    if (!importFile) {
      toast.error(language === "zh" ? "请先选择文件" : "Please select a file");
      return;
    }
    
    setIsImporting(true);
    
    try {
      const fileName = importFile.name.toLowerCase();
      const isExcel = fileName.endsWith('.xlsx') || fileName.endsWith('.xls');
      
      let topics: any[] = [];
      
      if (isExcel) {
        // 解析Excel文件
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
        
        // 第1行是标题行，第2行是示例行，从第2行开始解析数据（包含示例）
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i];
          if (!row || row.length === 0) continue; // 跳过完全空的行
          
          // 跳过说明行、空行、Instructions 行
          const firstCell = String(row[0] || "").trim();
          if (!firstCell || firstCell.startsWith("说明") || firstCell.startsWith("Instructions") || /^\d+\./.test(firstCell)) continue;
          
          // 选题来源转换：英文→中文
          const rawTopicSource = String(row[4] || "").trim();
          const mappedTopicSource = topicSourceEnToZh[rawTopicSource] || rawTopicSource || "其他";
          
          // 适合专业转换：英文名称/中文名称 → 系统内部值
          const rawMajor = String(row[6] || "").trim();
          const mappedMajor = (majorMapping[rawMajor] || "both") as "electronic_info" | "communication" | "both";
          
          topics.push({
            titleEn: String(row[0] || "").trim(),
            title: "", // 中文标题留空
            descriptionEn: String(row[1] || "").trim(),
            description: "", // 中文描述留空
            keywords: String(row[2] || "").trim(),
            researchFocus: String(row[3] || "").trim(),
            topicSource: mappedTopicSource,
            researchProjectName: String(row[5] || "").trim(),
            suitableMajor: mappedMajor,
            requiredSkills: String(row[7] || "").trim(),
          });
        }
      } else {
        // 解析CSV文件
        const text = await importFile.text();
        const lines = text.split("\n").filter(line => line.trim() && !line.startsWith("说明"));
        
        if (lines.length < 2) {
          toast.error(language === "zh" ? "文件中没有有效数据" : "No valid data in file");
          setIsImporting(false);
          return;
        }
        
        // 解析CSV
        const parseCSVLine = (line: string): string[] => {
          const result: string[] = [];
          let current = "";
          let inQuotes = false;
          
          for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"') {
              inQuotes = !inQuotes;
            } else if (char === "," && !inQuotes) {
              result.push(current.trim());
              current = "";
            } else {
              current += char;
            }
          }
          result.push(current.trim());
          return result;
        };
        
        // 跳过标题行和示例行，从第3行开始
        const dataLines = lines.slice(2);
        
        for (const line of dataLines) {
          if (!line.trim()) continue;
          const cells = parseCSVLine(line);
          
          if (cells.length < 4 || !cells[0]) continue; // 跳过空行或无效行
          
          // 选题来源转换：英文→中文
          const rawCsvSource = (cells[4] || "").trim();
          const mappedCsvSource = topicSourceEnToZh[rawCsvSource] || rawCsvSource || "其他";
          // 适合专业转换
          const rawCsvMajor = (cells[6] || "").trim();
          const mappedCsvMajor = (majorMapping[rawCsvMajor] || "both") as "electronic_info" | "communication" | "both";
          
          topics.push({
            titleEn: cells[0] || "",
            title: "", // 中文标题留空
            descriptionEn: cells[1] || "",
            description: "", // 中文描述留空
            keywords: cells[2] || "",
            researchFocus: cells[3] || "",
            topicSource: mappedCsvSource,
            researchProjectName: cells[5] || "",
            suitableMajor: mappedCsvMajor,
            requiredSkills: cells[7] || "",
          });
        }
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
      
      // 设置预览数据而不是直接导入
      setPreviewData(topics);
      setShowPreview(true);
      setIsImporting(false);
      toast.success(language === "zh" ? `解析成功，共${topics.length}条课题，请确认后导入` : `Parsed ${topics.length} topics, please confirm before import`);
    } catch (error: any) {
      toast.error(language === "zh" ? `解析文件失败: ${error.message}` : `Failed to parse file: ${error.message}`);
      setIsImporting(false);
    }
  };

  // 确认导入预览数据
  const handleConfirmImport = () => {
    if (previewData.length === 0) return;
    setIsImporting(true);
    bulkImportMutation.mutate({ topics: previewData });
  };

  // 取消预览
  const handleCancelPreview = () => {
    setPreviewData([]);
    setShowPreview(false);
    setImportFile(null);
    setImportErrors([]);
  };

  // 逐行验证导入数据，返回错误列表
  const validateImportData = (topics: any[]): {row: number; field: string; message: string}[] => {
    const errors: {row: number; field: string; message: string}[] = [];
    const isZh = language === "zh";
    
    topics.forEach((topic, index) => {
      const rowNum = index + 2; // Excel 中第2行开始是数据（第1行是标题）
      
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
        if (topic.titleEn && kwList.some((k: string) => k === topic.titleEn.trim())) {
          errors.push({ row: rowNum, field: isZh ? "论文关键词" : "Keywords", message: isZh ? "论文关键词字段内容不能与课题标题完全相同" : "Keywords field content cannot be identical to the topic title" });
        }
      }
      
      // 研究方向验证
      if (!topic.researchFocus || !topic.researchFocus.trim()) {
        errors.push({ row: rowNum, field: isZh ? "研究方向" : "Research Interests", message: isZh ? "研究方向字段内容未填写" : "Research Interests field content is not filled in" });
      } else {
        const rfList = topic.researchFocus.split(/[,，]/).map((r: string) => r.trim()).filter((r: string) => r);
        if (rfList.length > 2) {
          errors.push({ row: rowNum, field: isZh ? "研究方向" : "Research Interests", message: isZh ? `研究方向字段最多填写2个方向，当前填写了${rfList.length}个` : "Research Interests field allows max 2 directions, currently ${rfList.length} provided" });
        }
        const majorNames = ["电子信息工程", "通信工程", "Electronic Information Engineering", "Communication Engineering"];
        const matchedMajor = rfList.find((r: string) => majorNames.includes(r));
        if (matchedMajor) {
          errors.push({ row: rowNum, field: isZh ? "研究方向" : "Research Interests", message: isZh ? `研究方向字段内容不能与专业名称相同，当前填写了“${matchedMajor}”` : `Research Interests field content cannot be the same as a major name, "${matchedMajor}" was entered` });
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

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  // 按学年筛选课题
  const currentYearName = currentYear?.yearName || "";
  const currentYearTopics = topics?.filter(t => t.academicYear === currentYearName) || [];
  const otherYearTopics = topics?.filter(t => t.academicYear !== currentYearName) || [];
  
  // 获取所有历史学年
  const historicalYears = Array.from(new Set(otherYearTopics.map(t => t.academicYear))).filter(Boolean) as string[];
  
  // 当前学年的发布数量和限额
  const publishedCount = currentYearTopics.filter(t => t.status === "published").length;
  const quota = user?.annualQuota || 5;
  const isChineseTeacher = user?.teacherType === "chinese";
  
  // 是否可以撤回发布（不在选题和确认时间段）
  const canUnpublish = timePhase?.phase !== "student_selection" && timePhase?.phase !== "teacher_confirm";

  // 判断课题是否属于当前学年
  const isCurrentYearTopic = (topic: any) => topic.academicYear === currentYearName;

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
            <Button variant="ghost" onClick={() => setLocation("/teacher")}><ArrowLeft className="w-4 h-4 mr-2" />{t.back}</Button>
            <h1 className="text-2xl font-bold">{language === "zh" ? "课题管理" : "Topic Management"}</h1>
          </div>
          <div className="flex gap-2">
            {/* 批量导入按钮 */}
            <Dialog open={isBulkImportOpen} onOpenChange={setIsBulkImportOpen}>
              <DialogTrigger asChild>
                <Button variant="outline"><Upload className="w-4 h-4 mr-2" />{language === "zh" ? "批量导入" : "Bulk Import"}</Button>
              </DialogTrigger>
              <DialogContent className={showPreview ? "max-w-5xl max-h-[90vh] overflow-hidden flex flex-col" : "max-w-lg"}>
                <DialogHeader><DialogTitle>{language === "zh" ? "批量导入课题" : "Bulk Import Topics"}</DialogTitle></DialogHeader>
                
                {!showPreview ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <FileSpreadsheet className="w-5 h-5 text-blue-600" />
                        <span className="font-medium text-blue-800">{language === "zh" ? "第一步：下载模板" : "Step 1: Download Template"}</span>
                      </div>
                      <p className="text-sm text-blue-700 mb-3">{language === "zh" ? "请先下载Excel模板，按照模板格式填写课题信息" : "Download the Excel template and fill in topic information"}</p>
                      <Button variant="outline" size="sm" onClick={downloadTemplate}>
                        <Download className="w-4 h-4 mr-2" />{language === "zh" ? "下载模板" : "Download Template"}
                      </Button>
                    </div>
                    
                    <div className="p-4 bg-gray-50 rounded-lg border">
                      <div className="flex items-center gap-2 mb-2">
                        <Upload className="w-5 h-5 text-gray-600" />
                        <span className="font-medium">{language === "zh" ? "第二步：上传文件" : "Step 2: Upload File"}</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{language === "zh" ? "选择填写好的Excel或CSV文件进行导入" : "Select the filled Excel or CSV file to import"}</p>
                      <div className="flex items-center gap-3 mb-2">
                        <input
                          type="file"
                          id="bulk-import-file"
                          accept=".xlsx,.xls,.csv,.txt"
                          onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                          className="hidden"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => document.getElementById('bulk-import-file')?.click()}
                        >
                          {language === "zh" ? "选择文件" : "Choose File"}
                        </Button>
                        <span className="text-sm text-gray-500">
                          {importFile ? importFile.name : (language === "zh" ? "未选择文件" : "No file chosen")}
                        </span>
                      </div>
                      {importFile && (
                        <p className="text-sm text-green-600">{language === "zh" ? `已选择: ${importFile.name}` : `Selected: ${importFile.name}`}</p>
                      )}
                    </div>
                    
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => { setIsBulkImportOpen(false); setImportFile(null); }}>{t.cancel}</Button>
                      <Button onClick={handleFileImport} disabled={!importFile || isImporting}>
                        {isImporting ? (language === "zh" ? "解析中..." : "Parsing...") : (language === "zh" ? "解析文件" : "Parse File")}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col flex-1 overflow-hidden">
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200 mb-4">
                      <p className="text-sm text-green-800">
                        {language === "zh" 
                          ? `解析成功！共找到 ${previewData.length} 条课题数据，请确认无误后点击"确认导入"。` 
                          : `Parsed successfully! Found ${previewData.length} topics. Please confirm and click "Confirm Import".`}
                      </p>
                    </div>
                    
                    <div className="flex-1 overflow-auto border rounded-lg">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-100 sticky top-0">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-700 border-b">#</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700 border-b min-w-[200px]">{language === "zh" ? "英文标题" : "English Title"}</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700 border-b min-w-[150px]">{language === "zh" ? "关键词" : "Keywords"}</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700 border-b min-w-[120px]">{language === "zh" ? "研究方向" : "Research Interests"}</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700 border-b min-w-[100px]">{language === "zh" ? "选题来源" : "Topic Source"}</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700 border-b min-w-[80px]">{language === "zh" ? "适合专业" : "Major"}</th>
                          </tr>
                        </thead>
                        <tbody>
                          {previewData.map((topic, index) => (
                            <tr key={index} className="hover:bg-gray-50 border-b">
                              <td className="px-3 py-2 text-gray-500">{index + 1}</td>
                              <td className="px-3 py-2">
                                <div className="max-w-[300px] truncate" title={topic.titleEn}>{topic.titleEn}</div>
                              </td>
                              <td className="px-3 py-2">
                                <div className="max-w-[150px] truncate" title={topic.keywords}>{topic.keywords}</div>
                              </td>
                              <td className="px-3 py-2">
                                <div className="max-w-[120px] truncate" title={topic.researchFocus}>{topic.researchFocus}</div>
                              </td>
                              <td className="px-3 py-2">{topic.topicSource}</td>
                              <td className="px-3 py-2">
                                <Badge variant="outline">
                                  {topic.suitableMajor === "both" ? (language === "zh" ? "两个专业" : "Both") 
                                    : topic.suitableMajor === "electronic_info" ? (language === "zh" ? "电子信息" : "EI") 
                                    : (language === "zh" ? "通信" : "Comm")}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    
                    <div className="flex justify-end gap-2 pt-4 border-t mt-4">
                      <Button variant="outline" onClick={handleCancelPreview}>{language === "zh" ? "返回修改" : "Go Back"}</Button>
                      <Button onClick={handleConfirmImport} disabled={isImporting}>
                        {isImporting ? (language === "zh" ? "导入中..." : "Importing...") : (language === "zh" ? "确认导入" : "Confirm Import")}
                      </Button>
                    </div>
                  </div>
                )}
              </DialogContent>
            </Dialog>
            
            {/* 导入错误详情弹窗 */}
            <Dialog open={showErrorDialog} onOpenChange={setShowErrorDialog}>
              <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2 text-red-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    {language === "zh" ? "导入错误详情" : "Import Error Details"}
                  </DialogTitle>
                </DialogHeader>
                
                {importResult.success > 0 && (
                  <div className="p-3 bg-green-50 rounded-lg border border-green-200 mb-3">
                    <p className="text-sm text-green-800 font-medium">
                      {language === "zh" 
                        ? `✅ 已成功导入 ${importResult.success} 条课题数据` 
                        : `✅ Successfully imported ${importResult.success} topic(s)`}
                    </p>
                  </div>
                )}
                <div className="p-3 bg-red-50 rounded-lg border border-red-200 mb-3">
                  <p className="text-sm text-red-800">
                    {language === "zh" 
                      ? `❌ 发现 ${importErrors.length} 个错误，请根据以下信息修改后重新导入。` 
                      : `❌ Found ${importErrors.length} error(s). Please fix the issues below and re-import.`}
                  </p>
                </div>
                
                <div className="flex-1 overflow-auto border rounded-lg">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-700 border-b w-[80px]">{language === "zh" ? "行号" : "Row"}</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-700 border-b w-[150px]">{language === "zh" ? "字段" : "Field"}</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-700 border-b">{language === "zh" ? "错误说明" : "Error Description"}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {importErrors.map((err, idx) => (
                        <tr key={idx} className="hover:bg-red-50 border-b">
                          <td className="px-3 py-2 text-gray-600 font-mono">
                            {err.row > 0 ? (language === "zh" ? `第 ${err.row} 行` : `Row ${err.row}`) : "-"}
                          </td>
                          <td className="px-3 py-2 font-medium text-gray-800">{err.field}</td>
                          <td className="px-3 py-2 text-red-700">{err.message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="flex justify-end gap-2 pt-4 border-t mt-3">
                  <Button variant="outline" onClick={() => { setShowErrorDialog(false); setImportErrors([]); }}>
                    {language === "zh" ? "关闭" : "Close"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            
            {/* 导入成功弹窗 */}
            <Dialog open={showSuccessDialog} onOpenChange={setShowSuccessDialog}>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2 text-green-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    {language === "zh" ? "导入成功" : "Import Successful"}
                  </DialogTitle>
                </DialogHeader>
                
                <div className="py-6 text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                  <p className="text-3xl font-bold text-green-600 mb-1">
                    {importResult.success}
                  </p>
                  <p className="text-base text-gray-700 mb-4">
                    {language === "zh" 
                      ? `条课题已成功导入系统` 
                      : `topic(s) successfully imported`}
                  </p>
                  <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600 space-y-1">
                    <div className="flex justify-between">
                      <span>{language === "zh" ? "文件总数据条数" : "Total rows in file"}</span>
                      <span className="font-medium text-gray-800">{importResult.total}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>{language === "zh" ? "成功导入" : "Successfully imported"}</span>
                      <span className="font-medium text-green-600">{importResult.success}</span>
                    </div>
                    {importResult.failed > 0 && (
                      <div className="flex justify-between">
                        <span>{language === "zh" ? "导入失败" : "Failed"}</span>
                        <span className="font-medium text-red-600">{importResult.failed}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex justify-center">
                  <Button onClick={() => setShowSuccessDialog(false)}>
                    {language === "zh" ? "确定" : "OK"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            
            {/* 添加课题按钮 */}
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => resetForm()}><Plus className="w-4 h-4 mr-2" />{language === "zh" ? "添加课题" : "Add Topic"}</Button>
              </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader><DialogTitle>{editingTopic ? (language === "zh" ? "编辑课题" : "Edit Topic") : (language === "zh" ? "添加课题" : "Add Topic")}</DialogTitle></DialogHeader>
              <div className="space-y-4">
                <div><Label>{language === "zh" ? "课题标题（英文） *" : "Title (English) *"}</Label><Input value={titleEn} onChange={(e) => setTitleEn(e.target.value)} placeholder={language === "zh" ? "请输入课题标题（必填）" : "Required"} /></div>
                <div><Label>{language === "zh" ? "课题描述（英文） *" : "Description (English) *"}</Label><Textarea value={descriptionEn} onChange={(e) => setDescriptionEn(e.target.value)} rows={4} placeholder={language === "zh" ? "请输入课题描述（必填）" : "Required"} /></div>
                <div><Label>{language === "zh" ? "论文关键词 *" : "Keywords *"}</Label><Input value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder={language === "zh" ? "3-5个关键词，用逗号分隔，不能与题目完全相同" : "3-5 keywords, comma separated"} /></div>
                <div><Label>{language === "zh" ? "研究方向 *" : "Research Interests *"}</Label><Input value={researchFocus} onChange={(e) => setResearchFocus(e.target.value)} placeholder={language === "zh" ? "最多2个，用逗号分隔，不能与专业名称相同" : "Max 2, comma separated"} /></div>
                <div className="grid grid-cols-2 gap-4">
                  <div><Label>{language === "zh" ? "论文类型" : "Thesis Type"}</Label>
                    <Input value={language === "zh" ? "毕业设计" : "Graduation Design"} disabled className="bg-gray-100" />
                  </div>
                  <div><Label>{language === "zh" ? "选题来源 *" : "Topic Source *"}</Label>
                    <Select value={topicSource} onValueChange={setTopicSource}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="国家重点研发计划项目">{language === "zh" ? "国家重点研发计划项目" : "National Key R&D Program"}</SelectItem>
                        <SelectItem value="国家社科规划、基金项目">{language === "zh" ? "国家社科规划、基金项目" : "National Social Science Fund"}</SelectItem>
                        <SelectItem value="国家自然科学基金项目">{language === "zh" ? "国家自然科学基金项目" : "National Natural Science Foundation"}</SelectItem>
                        <SelectItem value="中央、国家各部门项目">{language === "zh" ? "中央、国家各部门项目" : "Central Government Projects"}</SelectItem>
                        <SelectItem value="教育部人文、社会科学研究项目">{language === "zh" ? "教育部人文、社会科学研究项目" : "MOE Humanities & Social Science"}</SelectItem>
                        <SelectItem value="省(自治区、直辖市)项目">{language === "zh" ? "省(自治区、直辖市)项目" : "Provincial/Municipal Projects"}</SelectItem>
                        <SelectItem value="国际合作研究项目">{language === "zh" ? "国际合作研究项目" : "International Cooperation"}</SelectItem>
                        <SelectItem value="与港、澳、台合作研究项目">{language === "zh" ? "与港、澳、台合作研究项目" : "HK/Macau/Taiwan Cooperation"}</SelectItem>
                        <SelectItem value="企、事业单位委托项目">{language === "zh" ? "企、事业单位委托项目" : "Enterprise Commissioned"}</SelectItem>
                        <SelectItem value="外资项目">{language === "zh" ? "外资项目" : "Foreign-funded Projects"}</SelectItem>
                        <SelectItem value="国防项目">{language === "zh" ? "国防项目" : "National Defense Projects"}</SelectItem>
                        <SelectItem value="学校自选项目">{language === "zh" ? "学校自选项目" : "University Self-selected"}</SelectItem>
                        <SelectItem value="非立项">{language === "zh" ? "非立项" : "Non-project"}</SelectItem>
                        <SelectItem value="科研项目（萨塞克斯老师适用）">{language === "zh" ? "科研项目（萨塞克斯老师适用）" : "Research Project (for Sussex only)"}</SelectItem>
                        <SelectItem value="其他">{language === "zh" ? "其他" : "Other"}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><Label>{language === "zh" ? "撰写语种" : "Writing Language"}</Label>
                    <Input value={language === "zh" ? "英语" : "English"} disabled className="bg-gray-100" />
                  </div>
                  <div><Label>{language === "zh" ? "适合专业" : "Applicable Course"}</Label>
                    <Select value={suitableMajor} onValueChange={(v) => setSuitableMajor(v as any)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="both">{t.majors.both}</SelectItem>
                        <SelectItem value="electronic_info">{t.majors.electronic_info}</SelectItem>
                        <SelectItem value="communication">{t.majors.communication}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                {topicSource !== "其他" && topicSource !== "科研项目（萨塞克斯老师适用）" && (
                  <div><Label>{language === "zh" ? "科研项目名称 *" : "Research Project Name *"}</Label><Input value={researchProjectName} onChange={(e) => setResearchProjectName(e.target.value)} placeholder={language === "zh" ? "请输入科研项目名称" : "Enter project name"} /></div>
                )}
                <div><Label>{language === "zh" ? "技能要求" : "Required Skills"}</Label><Input value={requiredSkills} onChange={(e) => setRequiredSkills(e.target.value)} placeholder={language === "zh" ? "可选" : "Optional"} /></div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={resetForm}>{t.cancel}</Button>
                  <Button onClick={handleSubmit}>{t.save}</Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          </div>
        </div>

        {/* 年度限额提示（仅中方导师显示） */}
        {isChineseTeacher && (
          <Card className="mb-6 bg-blue-50 border-blue-200">
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <span className="font-medium">{language === "zh" ? "当前学年" : "Current Academic Year"}: {language === "zh" ? currentYearName : currentYearName?.replace("学年", "")}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm">
                    {language === "zh" ? "已发布" : "Published"}: <span className="font-bold text-blue-600">{publishedCount}</span> / {quota}
                  </span>
                  {publishedCount >= quota && (
                    <Badge variant="destructive">{language === "zh" ? "已达限额" : "Quota Reached"}</Badge>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 学年筛选标签 */}
        <Tabs value={yearFilter} onValueChange={setYearFilter} className="mb-6">
          <TabsList>
            <TabsTrigger value="current">
              <Calendar className="w-4 h-4 mr-2" />
              {language === "zh" ? `当前学年 (${currentYearName})` : `Current (${currentYearName?.replace("学年", "")})`}
              <Badge variant="secondary" className="ml-2">{currentYearTopics.length}</Badge>
            </TabsTrigger>
            {historicalYears.length > 0 && (
              <TabsTrigger value="history">
                <Filter className="w-4 h-4 mr-2" />
                {language === "zh" ? "历史学年" : "Historical"}
                <Badge variant="secondary" className="ml-2">{otherYearTopics.length}</Badge>
              </TabsTrigger>
            )}
          </TabsList>

          {/* 当前学年课题 */}
          <TabsContent value="current">
            {isLoading ? <div>Loading...</div> : (
              <div className="grid gap-4">
                {currentYearTopics.map((topic) => (
                  <Card key={topic.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{topic.titleEn || topic.title}</CardTitle>
                        </div>
                        <div className="flex items-center gap-2">
                          {/* 热度显示 */}
                          {topic.status === "published" && (topic as any).heat !== undefined && (topic as any).heat > 0 && (
                            <Badge variant="secondary" className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {(topic as any).heat} {language === "zh" ? "人选择" : "selected"}
                            </Badge>
                          )}
                          <Badge variant={topic.status === "published" ? "default" : topic.status === "used" ? "secondary" : "outline"}>
                            {t.topicStatus[topic.status as keyof typeof t.topicStatus]}
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 mb-3">{topic.descriptionEn || topic.description}</p>
                      {/* 关键词和研究方向 */}
                      <div className="flex flex-wrap gap-4 mb-3 text-sm">
                        {topic.keywords && (
                          <div>
                            <span className="text-gray-500">{language === "zh" ? "关键词：" : "Keywords: "}</span>
                            <span className="text-gray-700">{topic.keywords}</span>
                          </div>
                        )}
                        {topic.researchFocus && (
                          <div>
                            <span className="text-gray-500">{language === "zh" ? "研究方向：" : "Research Interests: "}</span>
                            <span className="text-gray-700">{topic.researchFocus}</span>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-500">
                          {topic.suitableMajor && <span>{t.majors[topic.suitableMajor as keyof typeof t.majors]}</span>}
                        </div>
                        <div className="flex gap-2">
                          {topic.status === "draft" && (
                            <>
                              <Button size="sm" variant="outline" onClick={() => handleEdit(topic)}><Edit className="w-4 h-4" /></Button>
                              <Button size="sm" variant="outline" onClick={() => deleteMutation.mutate({ id: topic.id })}><Trash2 className="w-4 h-4" /></Button>
                              <Button size="sm" onClick={() => publishMutation.mutate({ id: topic.id })} disabled={isChineseTeacher && publishedCount >= quota}>
                                <Send className="w-4 h-4 mr-1" />{language === "zh" ? "发布" : "Publish"}
                              </Button>
                            </>
                          )}
                          {topic.status === "published" && canUnpublish && (
                            <Button size="sm" variant="outline" onClick={() => {
                              if (confirm(language === "zh" ? "确定要撤回发布吗？撤回后课题将变为草稿状态" : "Are you sure you want to unpublish this topic?")) {
                                unpublishMutation.mutate({ id: topic.id });
                              }
                            }}>
                              <Undo2 className="w-4 h-4 mr-1" />{language === "zh" ? "撤回" : "Unpublish"}
                            </Button>
                          )}
                          {topic.status === "published" && !canUnpublish && (
                            <span className="text-xs text-gray-400">
                              {language === "zh" ? "选题/确认期间无法撤回" : "Cannot unpublish during selection/confirmation"}
                            </span>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                {currentYearTopics.length === 0 && <div className="text-center py-12 text-gray-500">{language === "zh" ? "当前学年暂无课题，点击上方按钮添加" : "No topics for current year"}</div>}
              </div>
            )}
          </TabsContent>

          {/* 历史学年课题（只读） */}
          <TabsContent value="history">
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
              {language === "zh" ? "历史学年的课题仅供查看，无法进行编辑、删除或撤回操作" : "Historical topics are read-only and cannot be edited, deleted, or unpublished"}
            </div>
            {historicalYears.map(year => {
              const yearTopics = otherYearTopics.filter(t => t.academicYear === year);
              return (
                <div key={year} className="mb-6">
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    {year}
                    <Badge variant="outline">{yearTopics.length} {language === "zh" ? "个课题" : "topics"}</Badge>
                  </h3>
                  <div className="grid gap-4">
                    {yearTopics.map((topic) => (
                      <Card key={topic.id} className="opacity-75">
                        <CardHeader className="pb-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-lg">{topic.titleEn || topic.title}</CardTitle>
                            </div>
                            <Badge variant={topic.status === "published" ? "default" : topic.status === "used" ? "secondary" : "outline"}>
                              {t.topicStatus[topic.status as keyof typeof t.topicStatus]}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-gray-600 mb-3">{topic.descriptionEn || topic.description}</p>
                          <div className="flex flex-wrap gap-4 mb-2 text-sm">
                            {topic.keywords && (
                              <div>
                                <span className="text-gray-500">{language === "zh" ? "关键词：" : "Keywords: "}</span>
                                <span className="text-gray-700">{topic.keywords}</span>
                              </div>
                            )}
                            {topic.researchFocus && (
                              <div>
                                <span className="text-gray-500">{language === "zh" ? "研究方向：" : "Research Interests: "}</span>
                                <span className="text-gray-700">{topic.researchFocus}</span>
                              </div>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">
                            {topic.suitableMajor && <span>{t.majors[topic.suitableMajor as keyof typeof t.majors]}</span>}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              );
            })}
            {historicalYears.length === 0 && <div className="text-center py-12 text-gray-500">{language === "zh" ? "暂无历史学年课题" : "No historical topics"}</div>}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
