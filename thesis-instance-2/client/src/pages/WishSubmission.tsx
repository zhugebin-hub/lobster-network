import { useState, useEffect, useMemo } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, Plus, X, GripVertical, ChevronDown, ChevronUp, Info, Flame, Clock, AlertTriangle, Ban, User, Mail, Building, FileText, Search, Download } from "lucide-react";
import { Input } from "@/components/ui/input";

// 学院名称中英文翻译映射
const facultyTranslations: Record<string, string> = {
  "萨塞克斯人工智能学院": "ZJSU-Sussex AI Institute",
  "信息工程学院": "School of Information Engineering",
  "电子信息工程学院": "School of Electronic Information Engineering",
  "计算机科学与技术学院": "School of Computer Science and Technology",
  "计算机学院": "School of Computer Science",
  "理学院": "School of Science",
  "经济学院": "School of Economics",
  "管理学院": "School of Management",
  "外国语学院": "School of Foreign Languages",
  "人文学院": "School of Humanities",
  "法学院": "School of Law",
  "艺术学院": "School of Art",
  "数学学院": "School of Mathematics",
  "统计学院": "School of Statistics",
  "金融学院": "School of Finance",
  "会计学院": "School of Accounting",
  "工商管理学院": "School of Business Administration",
  "马克思主义学院": "School of Marxism",
  "体育部": "Department of Physical Education",
  "国际学院": "International College",
  "研究生院": "Graduate School",
};

function translateFaculty(faculty: string): string {
  if (facultyTranslations[faculty]) return facultyTranslations[faculty];
  // 尝试模糊匹配：如果包含关键字则返回对应翻译
  for (const [zh, en] of Object.entries(facultyTranslations)) {
    if (faculty.includes(zh) || zh.includes(faculty)) return en;
  }
  return faculty; // 如果没有匹配到，返回原文
}

export default function WishSubmission() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [selectedWishes, setSelectedWishes] = useState<Array<{ topicId: number; statement: string }>>([]);
  const [expandedStatements, setExpandedStatements] = useState<Set<number>>(new Set());
  const [expandedTopicDetails, setExpandedTopicDetails] = useState<Set<number>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");

  const utils = trpc.useUtils();
  const { data: topics } = trpc.topic.listPublished.useQuery(undefined, { enabled: isAuthenticated });
  const { data: existingWishes } = trpc.wish.myWishes.useQuery(undefined, { enabled: isAuthenticated });
  const { data: config } = trpc.admin.getConfig.useQuery(undefined, { enabled: isAuthenticated });
  const { data: currentPhase } = trpc.admin.getCurrentPhase.useQuery(undefined, { enabled: isAuthenticated });
  const { data: currentYear } = trpc.admin.getCurrentYear.useQuery(undefined, { enabled: isAuthenticated });

  const submitMutation = trpc.wish.submit.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "志愿提交成功" : "Wishes submitted"); utils.wish.myWishes.invalidate(); },
    onError: (e: any) => toast.error(e.message),
  });

  useEffect(() => {
    if (existingWishes && existingWishes.length > 0) {
      setSelectedWishes(existingWishes.map(w => ({ topicId: w.topicId, statement: w.statement || "" })));
    }
  }, [existingWishes]);

  // 新规则：所有学生都只能选3个志愿
  const isTransfer = user?.studentType === "transfer";
  const maxWishes = 3; // 所有学生都只能选3个志愿
  const minWishes = 3; // 必须填报3个志愿
  const statementRequired = true; // 必须填写选题声明

  // 检查学生是否属于当前学年
  const currentAcademicYear = currentYear?.yearName || (config as any)?.currentAcademicYear;
  const studentAcademicYear = user?.academicYear;
  const isCurrentYearStudent = !studentAcademicYear || studentAcademicYear === currentAcademicYear;

  // 检查是否在学生选题时间段
  const canSubmit = isCurrentYearStudent && (currentPhase?.phase === "student_selection" || currentPhase?.phase === "none");
  
  const phaseMessage = !isCurrentYearStudent
    ? (language === "zh" ? `您属于${studentAcademicYear}学年，当前学年为${currentAcademicYear}，无法进行选题操作` : `You belong to ${studentAcademicYear}, current year is ${currentAcademicYear}`)
    : currentPhase?.phase === "teacher_confirm" 
    ? (language === "zh" ? "当前为导师确认阶段，无法修改志愿" : "Teacher confirmation phase, cannot modify wishes")
    : currentPhase?.phase === "closed"
    ? (language === "zh" ? "选题已结束" : "Selection period ended")
    : null;

  // 分流学生只能看到中方导师的题目
  const baseFilteredTopics = useMemo(() => {
    if (!topics) return [];
    if (!isTransfer) return topics;
    // 分流学生过滤：只显示中方导师的题目
    return topics.filter(t => (t as any).teacherType === "chinese");
  }, [topics, isTransfer]);

  // 搜索过滤：按课题标题、关键词、导师姓名搜索
  const filteredTopics = useMemo(() => {
    if (!searchQuery.trim()) return baseFilteredTopics;
    const query = searchQuery.toLowerCase().trim();
    return baseFilteredTopics.filter(t => {
      const titleMatch = (t.titleEn || t.title || "").toLowerCase().includes(query);
      const keywordsMatch = (t.keywords || "").toLowerCase().includes(query);
      const teacherMatch = ((t as any).teacherName || "").toLowerCase().includes(query);
      const descMatch = (t.descriptionEn || t.description || "").toLowerCase().includes(query);
      const researchMatch = (t.researchFocus || "").toLowerCase().includes(query);
      return titleMatch || keywordsMatch || teacherMatch || descMatch || researchMatch;
    });
  }, [baseFilteredTopics, searchQuery]);

  const addWish = (topicId: number) => {
    if (!canSubmit) { toast.error(phaseMessage || "Cannot submit now"); return; }
    if (selectedWishes.length >= maxWishes) { toast.error(language === "zh" ? `最多选择${maxWishes}个志愿` : `Max ${maxWishes} wishes`); return; }
    if (selectedWishes.some(w => w.topicId === topicId)) { toast.error(language === "zh" ? "已选择该课题" : "Already selected"); return; }
    setSelectedWishes([...selectedWishes, { topicId, statement: "" }]);
  };

  const removeWish = (topicId: number) => {
    if (!canSubmit) { toast.error(phaseMessage || "Cannot modify now"); return; }
    setSelectedWishes(selectedWishes.filter(w => w.topicId !== topicId));
  };

  const updateStatement = (topicId: number, statement: string) => {
    setSelectedWishes(selectedWishes.map(w => w.topicId === topicId ? { ...w, statement } : w));
  };

  const toggleStatement = (topicId: number) => {
    const newSet = new Set(expandedStatements);
    if (newSet.has(topicId)) {
      newSet.delete(topicId);
    } else {
      newSet.add(topicId);
    }
    setExpandedStatements(newSet);
  };

  const toggleTopicDetails = (topicId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    const newSet = new Set(expandedTopicDetails);
    if (newSet.has(topicId)) {
      newSet.delete(topicId);
    } else {
      newSet.add(topicId);
    }
    setExpandedTopicDetails(newSet);
  };

  const countWords = (text: string) => text.trim().split(/\s+/).filter(w => w.length > 0).length;

  const handleSubmit = () => {
    if (!canSubmit) { toast.error(phaseMessage || "Cannot submit now"); return; }
    
    // 检查最少志愿数
    if (selectedWishes.length < minWishes) {
      toast.error(language === "zh" ? `至少需要填报${minWishes}个志愿` : `At least ${minWishes} wishes required`);
      return;
    }
    
    // 只有当statementRequired为true时才验证是否填写（不验证字数）
    if (statementRequired) {
      for (let i = 0; i < selectedWishes.length; i++) {
        const w = selectedWishes[i];
        if (!w.statement || w.statement.trim().length === 0) {
          toast.error(language === "zh" ? `第${i + 1}志愿需要填写选题声明` : `Wish ${i + 1} requires a statement`);
          return;
        }
      }
    }
    submitMutation.mutate({ wishes: selectedWishes.map((w, i) => ({ topicId: w.topicId, priority: i + 1, statement: w.statement || undefined })) });
  };

  // 导出当前可选课题为 CSV 文件
  const handleExportTopics = () => {
    const topicsToExport = baseFilteredTopics || [];
    if (topicsToExport.length === 0) {
      toast.error(language === "zh" ? "没有可导出的课题" : "No topics to export");
      return;
    }

    const isZh = language === "zh";
    const headers = isZh
      ? ["序号", "课题标题", "课题描述", "关键词", "研究方向", "导师姓名", "导师类型", "导师邮箱", "院系", "适合专业", "论文类型", "选题来源", "技能要求", "热度"]
      : ["No.", "Title", "Description", "Keywords", "Research Interests", "Supervisor", "Supervisor Type", "Email", "Faculty", "Applicable Course", "Thesis Type", "Topic Source", "Required Skills", "Heat"];

    const getMajorText = (major: string) => {
      if (major === "both") return isZh ? "两个专业均可" : "Both Courses";
      if (major === "electronic_info") return isZh ? "电子信息工程" : "Robotics and Electrical Engineering";
      if (major === "communication") return isZh ? "通信工程" : "Communications Engineering";
      return major || "-";
    };

    const getTeacherTypeText = (type: string) => {
      if (type === "chinese") return isZh ? "中方导师" : "ZJSU Supervisor";
      if (type === "british") return isZh ? "英方导师" : "Sussex Supervisor";
      return type || "-";
    };

    const escapeCsvField = (field: string) => {
      if (!field) return "";
      // 如果包含逗号、双引号或换行符，需要用双引号包裹
      if (field.includes(",") || field.includes('"') || field.includes("\n")) {
        return '"' + field.replace(/"/g, '""') + '"';
      }
      return field;
    };

    const rows = topicsToExport.map((topic, index) => [
      String(index + 1),
      escapeCsvField(topic.titleEn || topic.title || ""),
      escapeCsvField(topic.descriptionEn || topic.description || ""),
      escapeCsvField(topic.keywords || ""),
      escapeCsvField(topic.researchFocus || ""),
      escapeCsvField((topic as any).teacherName || ""),
      escapeCsvField(getTeacherTypeText((topic as any).teacherType || "")),
      escapeCsvField((topic as any).teacherEmail || ""),
      escapeCsvField(isZh ? ((topic as any).teacherFaculty || "") : translateFaculty((topic as any).teacherFaculty || "")),
      escapeCsvField(getMajorText(topic.suitableMajor || "")),
      escapeCsvField((topic as any).thesisType || ""),
      escapeCsvField((topic as any).topicSource || ""),
      escapeCsvField(topic.requiredSkills || ""),
      String((topic as any).heat || 0),
    ]);

    // 添加 BOM 以确保 Excel 正确识别中文
    const BOM = "\uFEFF";
    const csvContent = BOM + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = isZh ? `可选课题列表_${new Date().toISOString().slice(0, 10)}.csv` : `available_topics_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success(isZh ? `已导出 ${topicsToExport.length} 个课题` : `Exported ${topicsToExport.length} topics`);
  };

  const handleLogout = async () => { await logout(); setLocation("/"); };
  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  const getTopicById = (id: number) => filteredTopics?.find(t => t.id === id) || topics?.find(t => t.id === id);

  // 获取热度颜色
  const getHeatColor = (heat: number) => {
    if (heat >= 5) return "text-red-500";
    if (heat >= 3) return "text-orange-500";
    if (heat >= 1) return "text-yellow-500";
    return "text-gray-400";
  };

  // 格式化时间显示
  const formatDateTime = (isoString: string | null) => {
    if (!isoString) return "-";
    return new Date(isoString).toLocaleString(language === "zh" ? "zh-CN" : "en-US");
  };

  // 获取志愿名称（所有学生统一使用第一、第二、第三志愿）
  const getWishLabel = (index: number) => {
    const labels = language === "zh" 
      ? ["第一志愿", "第二志愿", "第三志愿"]
      : ["1st Choice", "2nd Choice", "3rd Choice"];
    return labels[index] || `#${index + 1}`;
  };

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
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => setLocation("/student")}><ArrowLeft className="w-4 h-4 mr-2" />{t.back}</Button>
          <h1 className="text-2xl font-bold">{language === "zh" ? "志愿填报" : "Submit Wishes"}</h1>
        </div>

        {/* 学年不匹配警告 */}
        {!isCurrentYearStudent && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <Ban className="w-5 h-5 text-red-600 mt-0.5" />
                <div className="text-sm text-red-700">
                  <p className="font-medium mb-1">{language === "zh" ? "无法进行选题操作" : "Cannot Submit Wishes"}</p>
                  <p>{language === "zh" 
                    ? `您属于${studentAcademicYear}学年，当前活跃学年为${currentAcademicYear}。只有当前学年的学生才能进行选题操作。`
                    : `You belong to ${studentAcademicYear}, but current active year is ${currentAcademicYear}. Only students of current year can submit wishes.`}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 时间阶段提示 */}
        {isCurrentYearStudent && currentPhase && currentPhase.phase !== "none" && (
          <Card className={`mb-6 ${canSubmit ? "border-green-200 bg-green-50" : "border-yellow-200 bg-yellow-50"}`}>
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <Clock className={`w-5 h-5 mt-0.5 ${canSubmit ? "text-green-600" : "text-yellow-600"}`} />
                <div className={`text-sm ${canSubmit ? "text-green-700" : "text-yellow-700"}`}>
                  <p className="font-medium mb-1">
                    {currentPhase.phase === "student_selection" && (language === "zh" ? "当前为学生选题阶段" : "Student Selection Phase")}
                    {currentPhase.phase === "teacher_confirm" && (language === "zh" ? "当前为导师确认阶段" : "Teacher Confirmation Phase")}
                    {currentPhase.phase === "closed" && (language === "zh" ? "选题已结束" : "Selection Ended")}
                  </p>
                  {currentPhase.phase === "student_selection" && currentPhase.studentSelectionEnd && (
                    <p>{language === "zh" ? "截止时间：" : "Deadline: "}{formatDateTime(currentPhase.studentSelectionEnd)}</p>
                  )}
                  {!canSubmit && (
                    <p className="flex items-center gap-1 mt-1">
                      <AlertTriangle className="w-4 h-4" />
                      {phaseMessage}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 说明卡片 */}
        <Card className="mb-6 border-blue-200 bg-blue-50">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">{language === "zh" ? "志愿填报规则" : "Wish Submission Rules"}</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>{language === "zh" ? "所有学生可填报3个志愿（第一、第二、第三志愿）" : "All students can submit 3 wishes (1st, 2nd, 3rd choice)"}</li>
                  <li>{language === "zh" ? "必须填报3个志愿才能提交" : "Must submit 3 wishes to proceed"}</li>
                  <li>{language === "zh" ? "每个志愿必须填写选题声明" : "Each wish requires a statement"}</li>
                </ul>
                <p className="mt-2 flex items-center gap-1">
                  <Flame className="w-4 h-4 text-orange-500" />
                  {language === "zh" 
                    ? "热度数字表示当前选择该课题的学生人数，仅供参考"
                    : "Heat number shows current applicants for each topic, for reference only"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-2 gap-8">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                {language === "zh" ? "可选课题" : "Available Topics"}
                <span className="text-sm font-normal text-gray-500 ml-2">({filteredTopics?.filter(t => !selectedWishes.some(w => w.topicId === t.id)).length || 0})</span>
              </h2>
              <Button variant="outline" size="sm" onClick={handleExportTopics}>
                <Download className="w-4 h-4 mr-1" />
                {language === "zh" ? "导出课题" : "Export"}
              </Button>
            </div>
            {/* 搜索框 */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="text"
                placeholder={language === "zh" ? "搜索课题标题、关键词或导师姓名..." : "Search by title, keywords or supervisor..."}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-10"
              />
              {searchQuery && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
                  onClick={() => setSearchQuery("")}
                >
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {filteredTopics?.filter(t => !selectedWishes.some(w => w.topicId === t.id)).map(topic => {
                const isExpanded = expandedTopicDetails.has(topic.id);
                return (
                  <Card 
                    key={topic.id} 
                    className={`hover:shadow-md transition-shadow ${!canSubmit ? "opacity-60" : ""}`}
                  >
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base flex items-center justify-between">
                        <span className="flex-1 cursor-pointer" onClick={() => addWish(topic.id)}>{topic.titleEn || topic.title}</span>
                        <div className="flex items-center gap-2">
                          {/* 课题热度显示 */}
                          <div className={`flex items-center gap-1 ${getHeatColor((topic as any).heat || 0)}`}>
                            <Flame className="w-4 h-4" />
                            <span className="text-sm font-medium">{(topic as any).heat || 0}</span>
                          </div>
                          <Button size="sm" variant="ghost" onClick={(e) => toggleTopicDetails(topic.id, e)}>
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </Button>
                          <Button size="sm" variant="ghost" disabled={!canSubmit} onClick={() => addWish(topic.id)}><Plus className="w-4 h-4" /></Button>
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {/* 导师信息 */}
                      <div className="flex flex-wrap items-center gap-4 mb-3 text-sm">
                        <div className="flex items-center gap-1 text-blue-600">
                          <User className="w-4 h-4" />
                          <span className="font-medium">{(topic as any).teacherName || (language === "zh" ? "未知导师" : "Unknown")}</span>
                          <Badge variant="secondary" className="ml-1 text-xs">
                            {(topic as any).teacherType === "chinese" ? (language === "zh" ? "中方" : "ZJSU") : (language === "zh" ? "英方" : "Sussex")}
                          </Badge>
                        </div>
                        {(topic as any).teacherEmail && (
                          <div className="flex items-center gap-1 text-gray-500">
                            <Mail className="w-3 h-3" />
                            <span className="text-xs">{(topic as any).teacherEmail}</span>
                          </div>
                        )}
                      </div>
                      
                      {/* 课题描述 */}
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">{topic.descriptionEn || topic.description || (language === "zh" ? "暂无描述" : "No description")}</p>
                      
                      {/* 关键词和研究方向 */}
                      <div className="flex flex-wrap gap-3 mb-2 text-xs">
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
                      
                      {/* 适合专业 */}
                      {topic.suitableMajor && <Badge variant="outline" className="mt-1">{t.majors[topic.suitableMajor as keyof typeof t.majors]}</Badge>}
                      
                      {/* 展开的详细信息 */}
                      {isExpanded && (
                        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                          {/* 课题完整描述 */}
                          {(topic.descriptionEn || topic.description) && (
                            <div>
                              <p className="text-xs font-medium text-gray-500 mb-1">{language === "zh" ? "课题描述" : "Description"}</p>
                              <p className="text-sm text-gray-700">{topic.descriptionEn || topic.description}</p>
                            </div>
                          )}
                          
                          {/* 论文类型、选题来源、撰写语种 */}
                          <div className="grid grid-cols-3 gap-2 text-xs">
                            {(topic as any).thesisType && (
                              <div>
                                <span className="text-gray-500">{language === "zh" ? "论文类型：" : "Type: "}</span>
                                <span className="text-gray-700">
                                  {(topic as any).thesisType === "design" ? (language === "zh" ? "设计型" : "Design") :
                                   (topic as any).thesisType === "research" ? (language === "zh" ? "研究型" : "Research") :
                                   (topic as any).thesisType === "application" ? (language === "zh" ? "应用型" : "Application") :
                                   (topic as any).thesisType === "other" ? (language === "zh" ? "其他" : "Other") :
                                   (topic as any).thesisType === "毕业设计" ? (language === "zh" ? "毕业设计" : "Graduation Design") :
                                   (topic as any).thesisType === "毕业论文" ? (language === "zh" ? "毕业论文" : "Graduation Thesis") : (topic as any).thesisType}
                                </span>
                              </div>
                            )}
                            {(topic as any).topicSource && (
                              <div>
                                <span className="text-gray-500">{language === "zh" ? "选题来源：" : "Source: "}</span>
                                <span className="text-gray-700">
                                  {(topic as any).topicSource === "teacher_research" ? (language === "zh" ? "导师科研项目" : "Teacher Research") :
                                   (topic as any).topicSource === "enterprise" ? (language === "zh" ? "企业实际项目" : "Enterprise") :
                                   (topic as any).topicSource === "student_proposal" ? (language === "zh" ? "学生自拟" : "Student Proposal") :
                                   (topic as any).topicSource === "other" ? (language === "zh" ? "其他" : "Other") :
                                   (topic as any).topicSource === "国家重点研发计划项目" ? (language === "zh" ? "国家重点研发计划项目" : "National Key R&D Program") :
                                   (topic as any).topicSource === "国家社科规划、基金项目" ? (language === "zh" ? "国家社科规划、基金项目" : "National Social Science Fund") :
                                   (topic as any).topicSource === "国家自然科学基金项目" ? (language === "zh" ? "国家自然科学基金项目" : "National Natural Science Foundation") :
                                   (topic as any).topicSource === "中央、国家各部门项目" ? (language === "zh" ? "中央、国家各部门项目" : "Central Government Projects") :
                                   (topic as any).topicSource === "教育部人文、社会科学研究项目" ? (language === "zh" ? "教育部人文、社会科学研究项目" : "MOE Humanities & Social Science") :
                                   (topic as any).topicSource === "省(自治区、直辖市)项目" ? (language === "zh" ? "省(自治区、直辖市)项目" : "Provincial/Municipal Projects") :
                                   (topic as any).topicSource === "国际合作研究项目" ? (language === "zh" ? "国际合作研究项目" : "International Cooperation") :
                                   (topic as any).topicSource === "与港、澳、台合作研究项目" ? (language === "zh" ? "与港、澳、台合作研究项目" : "HK/Macau/Taiwan Cooperation") :
                                   (topic as any).topicSource === "企、事业单位委托项目" ? (language === "zh" ? "企、事业单位委托项目" : "Enterprise Commissioned") :
                                   (topic as any).topicSource === "外资项目" ? (language === "zh" ? "外资项目" : "Foreign-funded Projects") :
                                   (topic as any).topicSource === "国防项目" ? (language === "zh" ? "国防项目" : "National Defense Projects") :
                                   (topic as any).topicSource === "学校自选项目" ? (language === "zh" ? "学校自选项目" : "University Self-selected") :
                                   (topic as any).topicSource === "非立项" ? (language === "zh" ? "非立项" : "Non-project") :
                                   (topic as any).topicSource === "科研项目（萨塞克斯老师适用）" ? (language === "zh" ? "科研项目（萨塞克斯老师适用）" : "Research Project (for Sussex only)") :
                                   (topic as any).topicSource === "其他" ? (language === "zh" ? "其他" : "Other") : (topic as any).topicSource}
                                </span>
                              </div>
                            )}
                            {(topic as any).topicLanguage && (
                              <div>
                                <span className="text-gray-500">{language === "zh" ? "撰写语种：" : "Language: "}</span>
                                <span className="text-gray-700">
                                  {(topic as any).topicLanguage === "english" ? (language === "zh" ? "英文" : "English") :
                                   (topic as any).topicLanguage === "chinese" ? (language === "zh" ? "中文" : "Chinese") :
                                   (topic as any).topicLanguage === "bilingual" ? (language === "zh" ? "中英双语" : "Bilingual") :
                                   (topic as any).topicLanguage === "英语" ? (language === "zh" ? "英语" : "English") : (topic as any).topicLanguage}
                                </span>
                              </div>
                            )}
                          </div>
                          
                          {/* 导师详细信息 */}
                          <div className="bg-gray-50 rounded-lg p-3">
                            <p className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                              <User className="w-3 h-3" />
                              {language === "zh" ? "导师信息" : "Supervisor Info"}
                            </p>
                            <div className="space-y-1 text-sm">
                              <p><span className="text-gray-500">{language === "zh" ? "姓名：" : "Name: "}</span>{(topic as any).teacherName || "-"}</p>
                              <p><span className="text-gray-500">{language === "zh" ? "邮箱：" : "Email: "}</span>{(topic as any).teacherEmail || "-"}</p>
                              {(topic as any).teacherFaculty && <p><span className="text-gray-500">{language === "zh" ? "院系：" : "Faculty: "}</span>{language === "zh" ? (topic as any).teacherFaculty : translateFaculty((topic as any).teacherFaculty)}</p>}
                              <p><span className="text-gray-500">{language === "zh" ? "类型：" : "Type: "}</span>
                                {(topic as any).teacherType === "chinese" ? (language === "zh" ? "中方导师" : "ZJSU Supervisor") : (language === "zh" ? "英方导师" : "Sussex Supervisor")}
                              </p>
                            </div>
                          </div>
                          
                          {/* 技能要求 */}
                          {topic.requiredSkills && (
                            <div>
                              <p className="text-xs font-medium text-gray-500 mb-1">{language === "zh" ? "技能要求" : "Required Skills"}</p>
                              <p className="text-sm text-gray-700">{topic.requiredSkills}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
              {filteredTopics?.filter(t => !selectedWishes.some(w => w.topicId === t.id)).length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  {searchQuery ? (
                    <>
                      <Search className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                      <p>{language === "zh" ? `未找到与"${searchQuery}"相关的课题` : `No topics found for "${searchQuery}"`}</p>
                      <Button variant="link" size="sm" onClick={() => setSearchQuery("")} className="mt-2">
                        {language === "zh" ? "清除搜索" : "Clear search"}
                      </Button>
                    </>
                  ) : (
                    <p>{language === "zh" ? "暂无可选课题" : "No available topics"}</p>
                  )}
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">{language === "zh" ? "我的志愿" : "My Wishes"} ({selectedWishes.length}/{maxWishes})</h2>
              <Button onClick={handleSubmit} disabled={selectedWishes.length < minWishes || !canSubmit}>
                {language === "zh" ? "提交志愿" : "Submit"}
              </Button>
            </div>
            {selectedWishes.length < minWishes && selectedWishes.length > 0 && (
              <p className="text-sm text-orange-600 mb-4">
                {language === "zh" ? `还需填报${minWishes - selectedWishes.length}个志愿才能提交` : `Need ${minWishes - selectedWishes.length} more wish(es) to submit`}
              </p>
            )}
            <div className="space-y-4">
              {selectedWishes.map((wish, index) => {
                const topic = getTopicById(wish.topicId);
                const wordCount = countWords(wish.statement);
                const isExpanded = expandedStatements.has(wish.topicId);
                return (
                  <Card key={wish.topicId}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center gap-2">
                        <GripVertical className="w-4 h-4 text-gray-400" />
                        <Badge variant="default">{getWishLabel(index)}</Badge>
                        <span className="flex-1 font-medium">{topic?.titleEn || topic?.title}</span>
                        {/* 显示该课题的热度 */}
                        <div className={`flex items-center gap-1 ${getHeatColor((topic as any)?.heat || 0)}`}>
                          <Flame className="w-4 h-4" />
                          <span className="text-sm">{(topic as any)?.heat || 0}</span>
                        </div>
                        <Button size="sm" variant="ghost" onClick={() => removeWish(wish.topicId)} disabled={!canSubmit}><X className="w-4 h-4" /></Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {/* 导师信息 */}
                      <div className="flex flex-wrap items-center gap-3 text-sm">
                        <div className="flex items-center gap-1 text-blue-600">
                          <User className="w-4 h-4" />
                          <span className="font-medium">{(topic as any)?.teacherName || (language === "zh" ? "未知导师" : "Unknown")}</span>
                          <Badge variant="secondary" className="ml-1 text-xs">
                            {(topic as any)?.teacherType === "chinese" ? (language === "zh" ? "中方" : "ZJSU") : (language === "zh" ? "英方" : "Sussex")}
                          </Badge>
                        </div>
                        {(topic as any)?.teacherEmail && (
                          <div className="flex items-center gap-1 text-gray-500">
                            <Mail className="w-3 h-3" />
                            <span className="text-xs">{(topic as any).teacherEmail}</span>
                          </div>
                        )}
                      </div>
                      
                      {/* 课题描述 */}
                      <p className="text-sm text-gray-600 line-clamp-2">{topic?.descriptionEn || topic?.description || (language === "zh" ? "暂无描述" : "No description")}</p>
                      
                      {/* 关键词和研究方向 */}
                      <div className="flex flex-wrap gap-3 text-xs">
                        {topic?.keywords && (
                          <div>
                            <span className="text-gray-500">{language === "zh" ? "关键词：" : "Keywords: "}</span>
                            <span className="text-gray-700">{topic.keywords}</span>
                          </div>
                        )}
                        {topic?.researchFocus && (
                          <div>
                            <span className="text-gray-500">{language === "zh" ? "研究方向：" : "Research Interests: "}</span>
                            <span className="text-gray-700">{topic.researchFocus}</span>
                          </div>
                        )}
                      </div>
                      
                      {/* 适合专业和论文类型 */}
                      <div className="flex flex-wrap gap-2">
                        {topic?.suitableMajor && <Badge variant="outline">{t.majors[topic.suitableMajor as keyof typeof t.majors]}</Badge>}
                        {(topic as any)?.thesisType && (
                          <Badge variant="outline" className="bg-blue-50">
                            {(topic as any).thesisType === "design" ? (language === "zh" ? "设计型" : "Design") :
                             (topic as any).thesisType === "research" ? (language === "zh" ? "研究型" : "Research") :
                             (topic as any).thesisType === "application" ? (language === "zh" ? "应用型" : "Application") :
                             (topic as any).thesisType === "毕业设计" ? (language === "zh" ? "毕业设计" : "Graduation Design") :
                             (topic as any).thesisType === "毕业论文" ? (language === "zh" ? "毕业论文" : "Graduation Thesis") : (topic as any).thesisType}
                           </Badge>
                        )}
                        {(topic as any)?.topicLanguage && (
                          <Badge variant="outline" className="bg-green-50">
                            {(topic as any).topicLanguage === "english" ? (language === "zh" ? "英文" : "English") :
                             (topic as any).topicLanguage === "chinese" ? (language === "zh" ? "中文" : "Chinese") :
                             (topic as any).topicLanguage === "bilingual" ? (language === "zh" ? "中英双语" : "Bilingual") :
                             (topic as any).topicLanguage === "英语" ? (language === "zh" ? "英语" : "English") : (topic as any).topicLanguage}
                          </Badge>
                        )}
                      </div>
                      
                      {/* 选题声明折叠区 */}
                      <Collapsible open={isExpanded} onOpenChange={() => toggleStatement(wish.topicId)}>
                        <CollapsibleTrigger asChild>
                          <Button variant="ghost" size="sm" className="w-full justify-between text-gray-600">
                            <span>
                              {language === "zh" 
                                ? (statementRequired ? "选题声明（必填）" : "选题声明（可选）") 
                                : (statementRequired ? "Statement (Required)" : "Statement (Optional)")}
                              {wish.statement && ` - ${wordCount} ${language === "zh" ? "词" : "words"}`}
                            </span>
                            <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                          </Button>
                        </CollapsibleTrigger>
                        <CollapsibleContent className="pt-2">
                          <Textarea
                            placeholder={language === "zh" 
                              ? (statementRequired ? "请输入英文选题声明..." : "可选：输入英文选题声明，有助于导师了解您的选题动机") 
                              : (statementRequired ? "Enter your statement..." : "Optional: Enter a statement to help the supervisor understand your motivation")}
                            value={wish.statement}
                            onChange={(e) => updateStatement(wish.topicId, e.target.value)}
                            rows={4}
                            disabled={!canSubmit}
                          />
                          <p className={`text-sm mt-1 ${!statementRequired ? "text-gray-500" : (wish.statement.trim().length > 0 ? "text-green-600" : "text-orange-600")}`}>
                            {language === "zh" ? `当前${wordCount}词` : `${wordCount} words`}
                            {statementRequired && (wish.statement.trim().length === 0 ? ` (${language === "zh" ? "必填" : "required"})` : "")}
                          </p>
                        </CollapsibleContent>
                      </Collapsible>
                    </CardContent>
                  </Card>
                );
              })}
              {selectedWishes.length === 0 && <p className="text-center py-8 text-gray-500">{language === "zh" ? "点击左侧课题添加志愿" : "Click topics to add wishes"}</p>}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
