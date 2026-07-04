import { useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";
import { GraduationCap, Globe, Loader2 } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const utils = trpc.useUtils();

  const loginMutation = trpc.auth.login.useMutation({
    onSuccess: async (data) => {
      toast.success(language === "zh" ? "登录成功" : "Login successful");
      // 先更新缓存，再跳转
      await utils.auth.me.invalidate();
      await utils.auth.me.refetch();
      const role = data.user?.role;
      if (role === "admin") {
        setLocation("/admin");
      } else if (role === "teacher") {
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
    loginMutation.mutate({ email, password });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setLocation("/")}>
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-gray-900">{t.appName}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLanguage(language === "zh" ? "en" : "zh")}
            className="flex items-center gap-2"
          >
            <Globe className="w-4 h-4" />
            {language === "zh" ? "English" : "中文"}
          </Button>
        </div>
      </header>

      {/* Login Form */}
      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">{t.login}</CardTitle>
            <CardDescription>
              {language === "zh" ? "请输入您的账号信息" : "Enter your credentials to sign in"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">{language === "zh" ? "账号" : "Account"}</Label>
                <Input
                  id="email"
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={language === "zh" ? "导师输入萨塞克斯邮箱，学生输入中方学号" : "Teacher: Sussex email, Student: Chinese ID"}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">{t.password}</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={language === "zh" ? "请输入密码" : "Enter password"}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
                {loginMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {t.login}
              </Button>
            </form>
            <div className="mt-6 text-center text-sm text-gray-500">
              {language === "zh" 
                ? "账号由管理员统一导入，初始密码为 zjsu@+账号前三位" 
                : "Accounts are imported by admin. Initial password: zjsu@ + first 3 chars of account"}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
