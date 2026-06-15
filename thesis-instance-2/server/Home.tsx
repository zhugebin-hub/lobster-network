import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/contexts/LanguageContext";
import { useLocation } from "wouter";
import { BookOpen, Target, Users, Globe, GraduationCap, FileText, ClipboardCheck, UserCheck, Download } from "lucide-react";
import { useEffect } from "react";

// 操作手册PDF下载链接
const USER_MANUAL_URL = "/files/templates/user-manual.pdf";

export default function Home() {
  const { user, loading, isAuthenticated } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (!loading && isAuthenticated && user) {
      if (user.role === "admin") {
        setLocation("/admin");
      } else if (user.role === "teacher") {
        setLocation("/teacher");
      } else if (user.role === "student") {
        setLocation("/student");
      }
    }
  }, [loading, isAuthenticated, user, setLocation]);

  const features = [
    {
      icon: BookOpen,
      title: language === "zh" ? "题库管理" : "Topic Library",
      description: language === "zh" 
        ? "导师可随时录入课题，支持Excel批量导入，系统自动查重" 
        : "Supervisors can add topics anytime, with Excel import and auto-duplicate check",
    },
    {
      icon: Target,
      title: language === "zh" ? "志愿优先匹配" : "Priority Matching",
      description: language === "zh" 
        ? "所有学生填报3个志愿，系统按志愿优先级逐轮匹配" 
        : "All students submit 3 wishes, system matches by priority order",
    },
    {
      icon: Users,
      title: language === "zh" ? "双向选择" : "Two-way Selection",
      description: language === "zh" 
        ? "学生可查看导师信息并填报志愿，导师审核确认，实现双向选择" 
        : "Students view supervisor info and submit wishes, supervisors review and confirm",
    },
    {
      icon: FileText,
      title: language === "zh" ? "指导记录" : "Guidance Logs",
      description: language === "zh" 
        ? "分流学生可记录指导过程，支持附件上传和导师确认" 
        : "Single-Degree students can record guidance sessions with file uploads",
    },
    {
      icon: ClipboardCheck,
      title: language === "zh" ? "论文评审" : "Thesis Review",
      description: language === "zh" 
        ? "支持论文终稿上传、导师评分和成绩管理" 
        : "Support thesis upload, supervisor scoring and grade management",
    },
    {
      icon: UserCheck,
      title: language === "zh" ? "分流学生管理" : "Single-Degree Students",
      description: language === "zh" 
        ? "分流学生仅能选择中方导师题目，系统自动过滤" 
        : "Single-Degree students can only select ZJSU supervisor topics",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLanguage(language === "zh" ? "en" : "zh")}
              className="flex items-center gap-2"
            >
              <Globe className="w-4 h-4" />
              {language === "zh" ? "English" : "中文"}
            </Button>
            <Button onClick={() => setLocation("/login")}>
              {t.login}
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {language === "zh" ? "人工智能学院毕业设计管理系统" : "UG Individual Project System (Sussex AI Institute ZJSU)"}
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            {language === "zh" 
              ? "为规范毕业设计选题流程，提高师生匹配效率与公平性，实现选题流程的线上化、自动化与透明化" 
              : "Streamline graduation design topic selection with automated matching, ensuring efficiency, fairness, and transparency"}
          </p>
          <div className="flex justify-center gap-4">
            <Button size="lg" onClick={() => setLocation("/login")}>
              {language === "zh" ? "立即登录" : "Sign In Now"}
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-white">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            {language === "zh" ? "核心功能" : "Key Features"}
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            {language === "zh" ? "选题流程" : "Selection Process"}
          </h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: 1, title: language === "zh" ? "导师出题" : "Topic Submission", desc: language === "zh" ? "导师录入课题到题库，支持批量导入" : "Supervisors submit topics with batch import" },
              { step: 2, title: language === "zh" ? "学生选题" : "Student Selection", desc: language === "zh" ? "学生填报3个志愿并填写选题声明" : "Students submit 3 wishes with statements" },
              { step: 3, title: language === "zh" ? "导师确认" : "Teacher Confirmation", desc: language === "zh" ? "导师审核并确认学生志愿" : "Supervisors review and confirm wishes" },
              { step: 4, title: language === "zh" ? "结果公示" : "Results Publication", desc: language === "zh" ? "公布最终匹配结果" : "Final results announced" },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                  {item.step}
                </div>
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          {/* 操作手册下载区域 */}
          <div className="flex flex-col items-center mb-8 pb-8 border-b border-gray-700">
            <h3 className="text-lg font-semibold mb-4">
              {language === "zh" ? "系统操作手册" : "User Manual"}
            </h3>
            <p className="text-gray-400 text-sm mb-4 text-center max-w-md">
              {language === "zh" 
                ? "下载完整的系统操作手册，了解管理员、导师和学生的详细操作指南" 
                : "Download the complete user manual for detailed guides for administrators, supervisors, and students"}
            </p>
            <a
              href={USER_MANUAL_URL}
              target="_blank"
              rel="noopener noreferrer"
              download="人工智能学院毕业设计管理系统操作手册.pdf"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
            >
              <Download className="w-5 h-5" />
              {language === "zh" ? "下载操作手册 (PDF)" : "Download User Manual (PDF)"}
            </a>
          </div>
          
          {/* 版权信息 */}
          <p className="text-gray-400 text-center">
            © {new Date().getFullYear()} {t.appName}
          </p>
        </div>
      </footer>
    </div>
  );
}
