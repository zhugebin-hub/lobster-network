import { useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";
import { GraduationCap, Globe, Loader2 } from "lucide-react";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<"teacher" | "student">("student");
  const [teacherType, setTeacherType] = useState<"chinese" | "british">("chinese");
  const [studentType, setStudentType] = useState<"transfer" | "non_transfer">("non_transfer");
  const [studentMajor, setStudentMajor] = useState<"electronic_info" | "communication">("electronic_info");
  
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const utils = trpc.useUtils();

  const registerMutation = trpc.auth.register.useMutation({
    onSuccess: (data) => {
      toast.success(language === "zh" ? "注册成功" : "Registration successful");
      utils.auth.me.invalidate();
      const userRole = data.user?.role;
      if (userRole === "teacher") {
        setLocation("/teacher");
      } else {
        setLocation("/student");
      }
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error(language === "zh" ? "两次密码输入不一致" : "Passwords do not match");
      return;
    }
    registerMutation.mutate({
      email, password, name, role,
      teacherType: role === "teacher" ? teacherType : undefined,
      studentType: role === "student" ? studentType : undefined,
      studentMajor: role === "student" ? studentMajor : undefined,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setLocation("/")}>
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "zh" ? "en" : "zh")} className="flex items-center gap-2">
            <Globe className="w-4 h-4" />
            {language === "zh" ? "English" : "中文"}
          </Button>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center p-4 py-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">{t.register}</CardTitle>
            <CardDescription>{language === "zh" ? "创建您的账号" : "Create your account"}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">{t.email}</Label>
                <Input id="email" type="text" value={email} onChange={(e) => setEmail(e.target.value)} placeholder={language === "zh" ? "请输入邮箱或用户名" : "Enter email or username"} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">{t.name}</Label>
                <Input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder={language === "zh" ? "请输入姓名" : "Enter your name"} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">{t.role}</Label>
                <Select value={role} onValueChange={(v) => setRole(v as "teacher" | "student")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="student">{t.roles.student}</SelectItem>
                    <SelectItem value="teacher">{t.roles.teacher}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {role === "teacher" && (
                <div className="space-y-2">
                  <Label>{language === "zh" ? "导师类型" : "Supervisor Type"}</Label>
                  <Select value={teacherType} onValueChange={(v) => setTeacherType(v as "chinese" | "british")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="chinese">{t.teacherTypes.chinese}</SelectItem>
                      <SelectItem value="british">{t.teacherTypes.british}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              {role === "student" && (
                <>
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "学生类型" : "Student Type"}</Label>
                    <Select value={studentType} onValueChange={(v) => setStudentType(v as "transfer" | "non_transfer")}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="non_transfer">{t.studentTypes.non_transfer}</SelectItem>
                        <SelectItem value="transfer">{t.studentTypes.transfer}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>{language === "zh" ? "专业" : "Major"}</Label>
                    <Select value={studentMajor} onValueChange={(v) => setStudentMajor(v as "electronic_info" | "communication")}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="electronic_info">{t.majors.electronic_info}</SelectItem>
                        <SelectItem value="communication">{t.majors.communication}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}
              <div className="space-y-2">
                <Label htmlFor="password">{t.password}</Label>
                <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={language === "zh" ? "请输入密码（至少6位）" : "Enter password (min 6 chars)"} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">{t.confirmPassword}</Label>
                <Input id="confirmPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder={language === "zh" ? "请再次输入密码" : "Confirm your password"} required />
              </div>
              <Button type="submit" className="w-full" disabled={registerMutation.isPending}>
                {registerMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {t.register}
              </Button>
            </form>
            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600">{language === "zh" ? "已有账号？" : "Already have an account?"}</span>{" "}
              <Button variant="link" className="p-0" onClick={() => setLocation("/login")}>{t.login}</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
