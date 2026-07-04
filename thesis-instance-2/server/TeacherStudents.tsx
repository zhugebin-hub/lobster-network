import React, { useState, useMemo } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { ArrowLeft, GraduationCap, Globe, LogOut, Calendar, Users, ChevronDown, ChevronUp, FileText, Download, AlertCircle } from "lucide-react";
import { toast } from "sonner";

export default function TeacherStudents() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [yearFilter, setYearFilter] = useState<string>("all");
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  // 获取该导师的学生列表（包含论文终稿信息）
  const { data: students, isLoading } = trpc.match.myStudents.useQuery(undefined, { 
    enabled: isAuthenticated && (user?.role === "teacher" || user?.role === "admin")
  });

  // 下载论文
  const handleDownloadThesis = async (fileUrl: string | undefined, studentName: string) => {
    if (!fileUrl) {
      toast.error(language === "zh" ? "该学生尚未上传论文" : "No thesis uploaded");
      return;
    }
    try {
      window.open(fileUrl, "_blank");
      toast.success(language === "zh" ? "开始下载" : "Download started");
    } catch (err) {
      toast.error(language === "zh" ? "下载失败" : "Download failed");
    }
  };
  
  const handleLogout = async () => { 
    await logout(); 
    setLocation("/"); 
  };

  // 按年度筛选学生
  const filteredStudents = useMemo(() => {
    if (!students) return [];
    if (yearFilter === "all") return students;
    return students.filter(s => s.topic?.academicYear === yearFilter);
  }, [students, yearFilter]);

  // 获取所有学年选项
  const yearOptions = useMemo(() => {
    if (!students) return [];
    const yearsSet = new Set(students.map(s => s.topic?.academicYear).filter(Boolean));
    return Array.from(yearsSet) as string[];
  }, [students]);

  const toggleRow = (id: number) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  if (loading || isLoading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

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
            <h1 className="text-2xl font-bold">{language === "zh" ? "我的学生" : "My Students"}</h1>
          </div>
          
          {/* 年度筛选 */}
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <Select value={yearFilter} onValueChange={setYearFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder={language === "zh" ? "选择学年" : "Select Year"} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{language === "zh" ? "全部学年" : "All Years"}</SelectItem>
                {yearOptions.map(year => (
                  <SelectItem key={year} value={year}>
                    {language === "zh" ? year : year?.replace("学年", "")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>


        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-green-600" />
              <CardTitle>{language === "zh" ? "学生列表" : "Student List"}</CardTitle>
            </div>
            <CardDescription>
              {language === "zh" 
                ? `共 ${filteredStudents.length} 名学生`
                : `Total ${filteredStudents.length} students`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">{language === "zh" ? "序号" : "No."}</TableHead>
                  <TableHead>{language === "zh" ? "学生姓名" : "Name"}</TableHead>
                  <TableHead>{language === "zh" ? "中方学号" : "CN ID"}</TableHead>
                  <TableHead>{language === "zh" ? "萨塞克斯学号" : "Sussex ID"}</TableHead>
                  <TableHead>{language === "zh" ? "专业" : "Major"}</TableHead>
                  <TableHead>{language === "zh" ? "班级" : "Class"}</TableHead>
                  <TableHead>{language === "zh" ? "课题标题（英文）" : "Topic Title (EN)"}</TableHead>
                  <TableHead>{language === "zh" ? "学年" : "Year"}</TableHead>
                  <TableHead>{language === "zh" ? "志愿" : "Pref"}</TableHead>
                  <TableHead>{language === "zh" ? "论文终稿" : "Thesis"}</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredStudents.map((m, index) => {
                  const thesisDraft = (m as any).thesisDraft;
                  
                  return (
                    <React.Fragment key={m.id}>
                      <TableRow key={m.id} className="cursor-pointer hover:bg-gray-50" onClick={() => toggleRow(m.id)}>
                        <TableCell>{index + 1}</TableCell>
                        <TableCell className="font-medium">{m.student?.name}</TableCell>
                        <TableCell>{(m.student as any)?.studentId || "-"}</TableCell>
                        <TableCell>{(m.student as any)?.sussexId || "-"}</TableCell>
                        <TableCell>
                          {m.student?.studentMajor === "electronic_info" 
                            ? (language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering")
                            : (language === "zh" ? "通信工程" : "Communications Engineering")}
                        </TableCell>
                        <TableCell>{(m.student as any)?.studentClass || "-"}</TableCell>
                        <TableCell className="max-w-xs truncate" title={m.topic?.titleEn || m.topic?.title}>
                          {m.topic?.titleEn || m.topic?.title}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs">
                            {language === "zh" ? m.topic?.academicYear : m.topic?.academicYear?.replace("学年", "")}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={m.isAdjustment ? "secondary" : "default"} className="text-xs">
                            {m.isAdjustment 
                              ? (language === "zh" ? "调剂" : "Adj")
                              : (language === "zh" ? `第${m.matchRound}志愿` : `#${m.matchRound}`)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {m.student?.studentType === "transfer" ? (
                            thesisDraft ? (
                              <div className="flex items-center gap-2">
                                <Badge variant="default" className="text-xs bg-green-100 text-green-700">
                                  <FileText className="w-3 h-3 mr-1" />
                                  {language === "zh" ? "已上传" : "Uploaded"}
                                </Badge>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDownloadThesis(thesisDraft?.fileUrl, m.student?.name || "");
                                  }}
                                >
                                  <Download className="w-4 h-4" />
                                </Button>
                              </div>
                            ) : (
                              <Badge variant="secondary" className="text-xs">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                {language === "zh" ? "未上传" : "Not uploaded"}
                              </Badge>
                            )
                          ) : (
                            <span className="text-gray-400 text-xs">{language === "zh" ? "不适用" : "N/A"}</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {expandedRow === m.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </TableCell>
                      </TableRow>
                      {expandedRow === m.id && (
                        <TableRow key={`${m.id}-detail`} className="bg-gray-50">
                          <TableCell colSpan={11}>
                            <div className="p-4 space-y-3">
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-500">{language === "zh" ? "论文类型" : "Thesis Type"}:</span>
                                  <span className="ml-2 font-medium">
                                    {m.topic?.thesisType === "毕业设计" ? (language === "zh" ? "毕业设计" : "Graduation Design") :
                                     m.topic?.thesisType === "毕业论文" ? (language === "zh" ? "毕业论文" : "Graduation Thesis") :
                                     m.topic?.thesisType === "design" ? (language === "zh" ? "设计型" : "Design") :
                                     m.topic?.thesisType === "research" ? (language === "zh" ? "研究型" : "Research") :
                                     m.topic?.thesisType === "application" ? (language === "zh" ? "应用型" : "Application") :
                                     m.topic?.thesisType || "-"}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-gray-500">{language === "zh" ? "选题来源" : "Topic Source"}:</span>
                                  <span className="ml-2 font-medium">
                                    {m.topic?.topicSource === "国家重点研发计划项目" ? (language === "zh" ? "国家重点研发计划项目" : "National Key R&D Program") :
                                     m.topic?.topicSource === "国家社科规划、基金项目" ? (language === "zh" ? "国家社科规划、基金项目" : "National Social Science Fund") :
                                     m.topic?.topicSource === "国家自然科学基金项目" ? (language === "zh" ? "国家自然科学基金项目" : "National Natural Science Foundation") :
                                     m.topic?.topicSource === "中央、国家各部门项目" ? (language === "zh" ? "中央、国家各部门项目" : "Central Government Projects") :
                                     m.topic?.topicSource === "教育部人文、社会科学研究项目" ? (language === "zh" ? "教育部人文、社会科学研究项目" : "MOE Humanities & Social Science") :
                                     m.topic?.topicSource === "省(自治区、直辖市)项目" ? (language === "zh" ? "省(自治区、直辖市)项目" : "Provincial/Municipal Projects") :
                                     m.topic?.topicSource === "国际合作研究项目" ? (language === "zh" ? "国际合作研究项目" : "International Cooperation") :
                                     m.topic?.topicSource === "与港、澳、台合作研究项目" ? (language === "zh" ? "与港、澳、台合作研究项目" : "HK/Macau/Taiwan Cooperation") :
                                     m.topic?.topicSource === "企、事业单位委托项目" ? (language === "zh" ? "企、事业单位委托项目" : "Enterprise Commissioned") :
                                     m.topic?.topicSource === "外资项目" ? (language === "zh" ? "外资项目" : "Foreign-funded Projects") :
                                     m.topic?.topicSource === "国防项目" ? (language === "zh" ? "国防项目" : "National Defense Projects") :
                                     m.topic?.topicSource === "学校自选项目" ? (language === "zh" ? "学校自选项目" : "University Self-selected") :
                                     m.topic?.topicSource === "非立项" ? (language === "zh" ? "非立项" : "Non-project") :
                                     m.topic?.topicSource === "科研项目（萨塞克斯老师适用）" ? (language === "zh" ? "科研项目（萨塞克斯老师适用）" : "Research Project (for Sussex only)") :
                                     m.topic?.topicSource === "其他" ? (language === "zh" ? "其他" : "Other") :
                                     m.topic?.topicSource || "-"}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-gray-500">{language === "zh" ? "撰写语种" : "Writing Language"}:</span>
                                  <span className="ml-2 font-medium">
                                    {m.topic?.topicLanguage === "英语" ? (language === "zh" ? "英语" : "English") :
                                     m.topic?.topicLanguage === "english" ? (language === "zh" ? "英文" : "English") :
                                     m.topic?.topicLanguage === "chinese" ? (language === "zh" ? "中文" : "Chinese") :
                                     m.topic?.topicLanguage === "bilingual" ? (language === "zh" ? "中英双语" : "Bilingual") :
                                     m.topic?.topicLanguage || "-"}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-gray-500">{language === "zh" ? "适合专业" : "Applicable Course"}:</span>
                                  <span className="ml-2 font-medium">
                                    {m.topic?.suitableMajor === "both" 
                                      ? (language === "zh" ? "两者皆可" : "Both")
                                      : m.topic?.suitableMajor === "electronic_info"
                                        ? (language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering")
                                        : (language === "zh" ? "通信工程" : "Communications Engineering")}
                                  </span>
                                </div>
                              </div>
                              <div>
                                <span className="text-gray-500 text-sm">{language === "zh" ? "论文关键词" : "Keywords"}:</span>
                                <div className="mt-1 flex flex-wrap gap-1">
                                  {m.topic?.keywords ? m.topic.keywords.split(/[,，、]/).map((kw: string, i: number) => (
                                    <Badge key={i} variant="secondary" className="text-xs">{kw.trim()}</Badge>
                                  )) : <span className="text-gray-400 text-sm">-</span>}
                                </div>
                              </div>
                              <div>
                                <span className="text-gray-500 text-sm">{language === "zh" ? "研究方向" : "Research Interests"}:</span>
                                <div className="mt-1 flex flex-wrap gap-1">
                                  {m.topic?.researchFocus ? m.topic.researchFocus.split(/[,，、]/).map((rf: string, i: number) => (
                                    <Badge key={i} variant="outline" className="text-xs">{rf.trim()}</Badge>
                                  )) : <span className="text-gray-400 text-sm">-</span>}
                                </div>
                              </div>
                              <div>
                                <span className="text-gray-500 text-sm">{language === "zh" ? "课题描述（英文）" : "Description (EN)"}:</span>
                                <p className="mt-1 text-sm text-gray-700">{m.topic?.descriptionEn || m.topic?.description || "-"}</p>
                              </div>
                              {/* 论文终稿详情 */}
                              {thesisDraft && (
                                <div className="border-t pt-3 mt-3">
                                  <span className="text-gray-500 text-sm font-medium">{language === "zh" ? "论文终稿信息" : "Thesis Details"}:</span>
                                  <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                    <div>
                                      <span className="text-gray-500">{language === "zh" ? "文件名" : "File Name"}:</span>
                                      <span className="ml-2 font-medium">{thesisDraft.fileName}</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-500">{language === "zh" ? "文件大小" : "File Size"}:</span>
                                      <span className="ml-2 font-medium">{(thesisDraft.fileSize / 1024 / 1024).toFixed(2)} MB</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-500">{language === "zh" ? "版本" : "Version"}:</span>
                                      <span className="ml-2 font-medium">v{thesisDraft.version}</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-500">{language === "zh" ? "提交时间" : "Submitted"}:</span>
                                      <span className="ml-2 font-medium">
                                        {new Date(thesisDraft.submittedAt).toLocaleString(language === "zh" ? "zh-CN" : "en-US")}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  );
                })}
                {filteredStudents.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={11} className="text-center py-8 text-gray-500">
                      {language === "zh" ? "暂无学生记录" : "No student records"}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
