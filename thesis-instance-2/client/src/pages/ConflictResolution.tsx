import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/contexts/LanguageContext";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { ArrowLeft, GraduationCap, Globe, LogOut, Clock, CheckCircle } from "lucide-react";

export default function ConflictResolution() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [, setLocation] = useLocation();

  const utils = trpc.useUtils();
  const { data: conflicts } = trpc.match.myConflicts.useQuery(undefined, { enabled: isAuthenticated });

  const resolveMutation = trpc.match.resolveConflict.useMutation({
    onSuccess: () => { toast.success(language === "zh" ? "已选择学生" : "Student selected"); utils.match.myConflicts.invalidate(); },
    onError: (e) => toast.error(e.message),
  });

  const handleLogout = async () => { await logout(); setLocation("/"); };
  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  const pendingConflicts = conflicts?.filter(c => !c.resolved) || [];
  const resolvedConflicts = conflicts?.filter(c => c.resolved) || [];

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
          <Button variant="ghost" onClick={() => setLocation("/teacher")}><ArrowLeft className="w-4 h-4 mr-2" />{t.back}</Button>
          <h1 className="text-2xl font-bold">{language === "zh" ? "冲突处理" : "Conflict Resolution"}</h1>
        </div>

        {pendingConflicts.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Clock className="w-5 h-5 text-orange-500" />{language === "zh" ? "待处理冲突" : "Pending Conflicts"}</h2>
            <div className="space-y-4">
              {pendingConflicts.map(conflict => (
                <Card key={conflict.id} className="border-orange-200">
                  <CardHeader>
                    <CardTitle>{conflict.topic?.title}</CardTitle>
                    <CardDescription>{language === "zh" ? `截止时间: ${conflict.deadline ? new Date(conflict.deadline).toLocaleString() : "未设置"}` : `Deadline: ${conflict.deadline ? new Date(conflict.deadline).toLocaleString() : "Not set"}`}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 mb-4">{language === "zh" ? "以下学生同时选择了此课题，请选择一位：" : "Multiple students selected this topic:"}</p>
                    <div className="space-y-3">
                      {conflict.students?.map((s: any) => (
                        <div key={s.id} className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{s.name}</span>
                            <Button size="sm" onClick={() => resolveMutation.mutate({ conflictId: conflict.id, selectedStudentId: s.id })}>{language === "zh" ? "选择" : "Select"}</Button>
                          </div>
                          <p className="text-sm text-gray-600">{s.statement}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {resolvedConflicts.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><CheckCircle className="w-5 h-5 text-green-500" />{language === "zh" ? "已处理" : "Resolved"}</h2>
            <div className="space-y-2">
              {resolvedConflicts.map(c => (
                <Card key={c.id} className="bg-gray-50">
                  <CardHeader className="py-3">
                    <div className="flex items-center justify-between">
                      <span>{c.topic?.title}</span>
                      <Badge variant="secondary">{language === "zh" ? "已处理" : "Resolved"}</Badge>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        )}

        {conflicts?.length === 0 && <p className="text-center py-12 text-gray-500">{language === "zh" ? "暂无冲突需要处理" : "No conflicts"}</p>}
      </main>
    </div>
  );
}
