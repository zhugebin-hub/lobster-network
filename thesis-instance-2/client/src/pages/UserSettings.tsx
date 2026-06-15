import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, KeyRound, User, Loader2 } from "lucide-react";

export default function UserSettings() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const changePasswordMutation = trpc.auth.changePassword.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "密码修改成功" : "Password changed successfully");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    },
    onError: (e: any) => toast.error(e.message),
  });

  const handleChangePassword = () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error(language === "zh" ? "请填写所有密码字段" : "Please fill all password fields");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error(language === "zh" ? "两次输入的新密码不一致" : "New passwords do not match");
      return;
    }
    if (newPassword.length < 6) {
      toast.error(language === "zh" ? "新密码至少6位" : "New password must be at least 6 characters");
      return;
    }
    changePasswordMutation.mutate({ currentPassword, newPassword });
  };

  const handleLogout = async () => { await logout(); setLocation("/"); };

  const goBack = () => {
    if (user?.role === "admin") setLocation("/admin");
    else if (user?.role === "teacher") setLocation("/teacher");
    else setLocation("/student");
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;

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

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={goBack}>
            <ArrowLeft className="w-4 h-4 mr-2" />{t.back}
          </Button>
          <h1 className="text-2xl font-bold">{language === "zh" ? "账户设置" : "Account Settings"}</h1>
        </div>

        {/* 用户信息卡片 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              {language === "zh" ? "账户信息" : "Account Information"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-500">{language === "zh" ? "姓名" : "Name"}</Label>
                <p className="font-medium">{user?.name || "-"}</p>
              </div>
              <div>
                <Label className="text-gray-500">{language === "zh" ? "角色" : "Role"}</Label>
                <p className="font-medium">{user?.role === "admin" ? t.roles.admin : user?.role === "teacher" ? t.roles.teacher : t.roles.student}</p>
              </div>
              {user?.role === "teacher" && (
                <>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "萨塞克斯邮箱" : "Sussex Email"}</Label>
                    <p className="font-medium font-mono text-sm">{user?.email || "-"}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "工号" : "Teacher No"}</Label>
                    <p className="font-medium font-mono">{user?.teacherNo || "0000000"}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "类型" : "Type"}</Label>
                    <p className="font-medium">{user?.teacherType === "chinese" ? (language === "zh" ? "中方导师" : "ZJSU") : (language === "zh" ? "英方导师" : "Sussex")}</p>
                  </div>
                </>
              )}
              {user?.role === "student" && (
                <>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "中方学号" : "Chinese ID"}</Label>
                    <p className="font-medium font-mono">{user?.studentId || user?.email || "-"}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "萨塞克斯学号" : "Sussex ID"}</Label>
                    <p className="font-medium font-mono">{user?.sussexId || "-"}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "类型" : "Type"}</Label>
                    <p className="font-medium">{user?.studentType === "transfer" ? (language === "zh" ? "分流" : "Single-Degree") : (language === "zh" ? "非分流" : "Dual-Degree")}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{language === "zh" ? "专业" : "Major"}</Label>
                    <p className="font-medium">{user?.studentMajor === "electronic_info" ? t.majors.electronic_info : user?.studentMajor === "communication" ? t.majors.communication : "-"}</p>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 修改密码卡片 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <KeyRound className="w-5 h-5" />
              {language === "zh" ? "修改密码" : "Change Password"}
            </CardTitle>
            <CardDescription>
              {language === "zh" ? "修改您的登录密码" : "Update your login password"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>{language === "zh" ? "当前密码" : "Current Password"}</Label>
              <Input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder={language === "zh" ? "请输入当前密码" : "Enter current password"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "新密码" : "New Password"}</Label>
              <Input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder={language === "zh" ? "请输入新密码（至少6位）" : "Enter new password (min 6 chars)"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "确认新密码" : "Confirm New Password"}</Label>
              <Input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder={language === "zh" ? "请再次输入新密码" : "Confirm new password"}
              />
            </div>
            <Button onClick={handleChangePassword} disabled={changePasswordMutation.isPending}>
              {changePasswordMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {language === "zh" ? "保存密码" : "Save Password"}
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
