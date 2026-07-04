import { useState, useMemo } from "react";
import { trpc } from "@/lib/trpc";
import { useLanguage } from "@/contexts/LanguageContext";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Activity, 
  Search, 
  RefreshCw, 
  Eye,
  Calendar,
  User,
  FileText,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Users,
  Shield,
  GraduationCap,
  BookOpen,
  ArrowLeft,
} from "lucide-react";

export default function AdminUserActivityLogs() {
  const { language } = useLanguage();
  const isZh = language === "zh";
  const [filters, setFilters] = useState({
    userRole: "",
    action: "",
    module: "",
    keyword: "",
    startDate: "",
    endDate: "",
  });
  const [page, setPage] = useState(0);
  const [selectedLog, setSelectedLog] = useState<any>(null);
  const pageSize = 20;

  // 稳定化查询参数
  const queryInput = useMemo(() => ({
    userRole: filters.userRole || undefined,
    action: filters.action || undefined,
    module: filters.module || undefined,
    keyword: filters.keyword || undefined,
    startDate: filters.startDate || undefined,
    endDate: filters.endDate || undefined,
    limit: pageSize,
    offset: page * pageSize,
  }), [filters.userRole, filters.action, filters.module, filters.keyword, filters.startDate, filters.endDate, page]);

  // 获取日志列表
  const { data: logsData, isLoading, refetch } = trpc.admin.getUserActivityLogs.useQuery(queryInput);

  // 获取统计数据
  const { data: statsData } = trpc.admin.getUserActivityLogStats.useQuery();

  // 操作类型映射
  const actionLabels: Record<string, { zh: string; en: string; color: string }> = {
    login: { zh: "登录", en: "Login", color: "bg-blue-100 text-blue-800" },
    logout: { zh: "登出", en: "Logout", color: "bg-gray-100 text-gray-800" },
    submit_wish: { zh: "提交志愿", en: "Submit Wish", color: "bg-indigo-100 text-indigo-800" },
    approve_wish: { zh: "同意志愿", en: "Approve Wish", color: "bg-green-100 text-green-800" },
    reject_wish: { zh: "拒绝志愿", en: "Reject Wish", color: "bg-red-100 text-red-800" },
    score_thesis_first: { zh: "第一导师评分", en: "1st Advisor Score", color: "bg-amber-100 text-amber-800" },
    score_thesis_second: { zh: "第二导师评分", en: "2nd Advisor Score", color: "bg-orange-100 text-orange-800" },
    upload_thesis: { zh: "上传论文", en: "Upload Thesis", color: "bg-purple-100 text-purple-800" },
    update_config: { zh: "修改配置", en: "Update Config", color: "bg-yellow-100 text-yellow-800" },
    create_user: { zh: "创建用户", en: "Create User", color: "bg-teal-100 text-teal-800" },
    bulk_import: { zh: "批量导入", en: "Bulk Import", color: "bg-violet-100 text-violet-800" },
    assign_second_teacher: { zh: "指派第二导师", en: "Assign 2nd Advisor", color: "bg-cyan-100 text-cyan-800" },
    create_topic: { zh: "创建课题", en: "Create Topic", color: "bg-emerald-100 text-emerald-800" },
    update_topic: { zh: "更新课题", en: "Update Topic", color: "bg-sky-100 text-sky-800" },
    delete_topic: { zh: "删除课题", en: "Delete Topic", color: "bg-rose-100 text-rose-800" },
    change_password: { zh: "修改密码", en: "Change Password", color: "bg-slate-100 text-slate-800" },
  };

  // 模块映射
  const moduleLabels: Record<string, { zh: string; en: string }> = {
    auth: { zh: "认证", en: "Authentication" },
    wish: { zh: "志愿", en: "Wish" },
    topic: { zh: "课题", en: "Topic" },
    thesis: { zh: "论文", en: "Thesis" },
    config: { zh: "配置", en: "Config" },
    user: { zh: "用户", en: "User" },
    second_teacher: { zh: "第二导师", en: "2nd Advisor" },
    title_change: { zh: "题目变更", en: "Title Change" },
    purchase: { zh: "采购", en: "Purchase" },
    guidance: { zh: "指导记录", en: "Guidance" },
    matching: { zh: "匹配", en: "Matching" },
  };

  // 角色映射
  const roleLabels: Record<string, { zh: string; en: string; color: string; icon: any }> = {
    admin: { zh: "管理员", en: "Admin", color: "bg-red-100 text-red-800", icon: Shield },
    teacher: { zh: "导师", en: "Teacher", color: "bg-blue-100 text-blue-800", icon: BookOpen },
    student: { zh: "学生", en: "Student", color: "bg-green-100 text-green-800", icon: GraduationCap },
  };

  const getActionLabel = (action: string) => {
    const label = actionLabels[action];
    return label ? (isZh ? label.zh : label.en) : action;
  };

  const getActionColor = (action: string) => {
    return actionLabels[action]?.color || "bg-gray-100 text-gray-800";
  };

  const getModuleLabel = (module: string) => {
    const label = moduleLabels[module];
    return label ? (isZh ? label.zh : label.en) : module;
  };

  const getRoleLabel = (role: string) => {
    const label = roleLabels[role];
    return label ? (isZh ? label.zh : label.en) : role;
  };

  const getRoleColor = (role: string) => {
    return roleLabels[role]?.color || "bg-gray-100 text-gray-800";
  };

  const formatDateTime = (dateStr: string | Date) => {
    const date = new Date(dateStr);
    return date.toLocaleString(isZh ? "zh-CN" : "en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const totalPages = Math.ceil((logsData?.total || 0) / pageSize);

  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/admin")}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold">
            {isZh ? "用户活动日志" : "User Activity Logs"}
          </h1>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 mt-1">
              {isZh 
                ? "追踪所有用户（管理员、导师、学生）的关键操作记录" 
                : "Track key operations of all users (admins, teachers, students)"}
            </p>
          </div>
          <Button onClick={() => refetch()} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {isZh ? "刷新" : "Refresh"}
          </Button>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Activity className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">
                    {isZh ? "总活动数" : "Total Activities"}
                  </p>
                  <p className="text-2xl font-bold">{statsData?.totalLogs || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">
                    {isZh ? "今日活动" : "Today's Activities"}
                  </p>
                  <p className="text-2xl font-bold">{statsData?.todayLogs || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">
                    {isZh ? "近7天活动" : "Last 7 Days"}
                  </p>
                  <p className="text-2xl font-bold">{statsData?.last7DaysLogs || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Users className="h-6 w-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">
                    {isZh ? "角色分布" : "Role Distribution"}
                  </p>
                  <div className="flex gap-1 mt-1">
                    {statsData?.roleStats?.slice(0, 3).map((r: any) => (
                      <Badge key={r.role} variant="outline" className="text-xs">
                        {getRoleLabel(r.role)}: {r.count}
                      </Badge>
                    ))}
                    {(!statsData?.roleStats || statsData.roleStats.length === 0) && (
                      <span className="text-sm text-gray-400">-</span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 筛选区域 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Search className="h-5 w-5" />
              {isZh ? "筛选条件" : "Filters"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="space-y-2">
                <Label>{isZh ? "用户角色" : "User Role"}</Label>
                <Select
                  value={filters.userRole}
                  onValueChange={(value) => {
                    setFilters({ ...filters, userRole: value === "all" ? "" : value });
                    setPage(0);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={isZh ? "全部" : "All"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">{isZh ? "全部" : "All"}</SelectItem>
                    <SelectItem value="admin">{isZh ? "管理员" : "Admin"}</SelectItem>
                    <SelectItem value="teacher">{isZh ? "导师" : "Teacher"}</SelectItem>
                    <SelectItem value="student">{isZh ? "学生" : "Student"}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{isZh ? "操作类型" : "Action Type"}</Label>
                <Select
                  value={filters.action}
                  onValueChange={(value) => {
                    setFilters({ ...filters, action: value === "all" ? "" : value });
                    setPage(0);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={isZh ? "全部" : "All"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">{isZh ? "全部" : "All"}</SelectItem>
                    <SelectItem value="login">{isZh ? "登录" : "Login"}</SelectItem>
                    <SelectItem value="submit_wish">{isZh ? "提交志愿" : "Submit Wish"}</SelectItem>
                    <SelectItem value="approve_wish">{isZh ? "同意志愿" : "Approve Wish"}</SelectItem>
                    <SelectItem value="reject_wish">{isZh ? "拒绝志愿" : "Reject Wish"}</SelectItem>
                    <SelectItem value="upload_thesis">{isZh ? "上传论文" : "Upload Thesis"}</SelectItem>
                    <SelectItem value="score_thesis_first">{isZh ? "第一导师评分" : "1st Advisor Score"}</SelectItem>
                    <SelectItem value="score_thesis_second">{isZh ? "第二导师评分" : "2nd Advisor Score"}</SelectItem>
                    <SelectItem value="update_config">{isZh ? "修改配置" : "Update Config"}</SelectItem>
                    <SelectItem value="create_user">{isZh ? "创建用户" : "Create User"}</SelectItem>
                    <SelectItem value="bulk_import">{isZh ? "批量导入" : "Bulk Import"}</SelectItem>
                    <SelectItem value="assign_second_teacher">{isZh ? "指派第二导师" : "Assign 2nd Advisor"}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{isZh ? "操作模块" : "Module"}</Label>
                <Select
                  value={filters.module}
                  onValueChange={(value) => {
                    setFilters({ ...filters, module: value === "all" ? "" : value });
                    setPage(0);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={isZh ? "全部" : "All"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">{isZh ? "全部" : "All"}</SelectItem>
                    <SelectItem value="auth">{isZh ? "认证" : "Authentication"}</SelectItem>
                    <SelectItem value="wish">{isZh ? "志愿" : "Wish"}</SelectItem>
                    <SelectItem value="topic">{isZh ? "课题" : "Topic"}</SelectItem>
                    <SelectItem value="thesis">{isZh ? "论文" : "Thesis"}</SelectItem>
                    <SelectItem value="config">{isZh ? "配置" : "Config"}</SelectItem>
                    <SelectItem value="user">{isZh ? "用户" : "User"}</SelectItem>
                    <SelectItem value="second_teacher">{isZh ? "第二导师" : "2nd Advisor"}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{isZh ? "关键词搜索" : "Keyword"}</Label>
                <Input
                  placeholder={isZh ? "搜索用户名、描述..." : "Search name, description..."}
                  value={filters.keyword}
                  onChange={(e) => {
                    setFilters({ ...filters, keyword: e.target.value });
                    setPage(0);
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label>{isZh ? "开始日期" : "Start Date"}</Label>
                <Input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => {
                    setFilters({ ...filters, startDate: e.target.value });
                    setPage(0);
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label>{isZh ? "结束日期" : "End Date"}</Label>
                <Input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => {
                    setFilters({ ...filters, endDate: e.target.value });
                    setPage(0);
                  }}
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <Button
                variant="outline"
                onClick={() => {
                  setFilters({ userRole: "", action: "", module: "", keyword: "", startDate: "", endDate: "" });
                  setPage(0);
                }}
              >
                {isZh ? "重置筛选" : "Reset Filters"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 日志列表 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {isZh ? "活动记录" : "Activity Records"}
            </CardTitle>
            <CardDescription>
              {isZh 
                ? `共 ${logsData?.total || 0} 条记录`
                : `Total ${logsData?.total || 0} records`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[500px]">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[170px]">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {isZh ? "时间" : "Time"}
                      </div>
                    </TableHead>
                    <TableHead>
                      <div className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {isZh ? "用户" : "User"}
                      </div>
                    </TableHead>
                    <TableHead>{isZh ? "角色" : "Role"}</TableHead>
                    <TableHead>{isZh ? "操作" : "Action"}</TableHead>
                    <TableHead>{isZh ? "模块" : "Module"}</TableHead>
                    <TableHead>{isZh ? "描述" : "Description"}</TableHead>
                    <TableHead className="text-right">{isZh ? "详情" : "Details"}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                        {isZh ? "加载中..." : "Loading..."}
                      </TableCell>
                    </TableRow>
                  ) : logsData?.logs?.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                        <div className="flex flex-col items-center gap-2">
                          <FileText className="h-8 w-8 text-gray-300" />
                          <span>{isZh ? "暂无活动记录" : "No activity records"}</span>
                          <span className="text-xs text-gray-400">
                            {isZh ? "用户操作后将自动记录在此" : "User activities will be recorded here automatically"}
                          </span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    logsData?.logs?.map((log: any) => (
                      <TableRow key={log.id}>
                        <TableCell className="text-sm text-gray-600">
                          {formatDateTime(log.createdAt)}
                        </TableCell>
                        <TableCell className="font-medium">
                          {log.userName || "-"}
                        </TableCell>
                        <TableCell>
                          <Badge className={getRoleColor(log.userRole)}>
                            {getRoleLabel(log.userRole)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={getActionColor(log.action)}>
                            {getActionLabel(log.action)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-gray-600">
                            {getModuleLabel(log.module)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-gray-600 line-clamp-1 max-w-[300px]">
                            {log.description || "-"}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedLog(log)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </ScrollArea>

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t">
                <div className="text-sm text-gray-500">
                  {isZh 
                    ? `第 ${page + 1} 页，共 ${totalPages} 页`
                    : `Page ${page + 1} of ${totalPages}`}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.max(0, page - 1))}
                    disabled={page === 0}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    {isZh ? "上一页" : "Previous"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                    disabled={page >= totalPages - 1}
                  >
                    {isZh ? "下一页" : "Next"}
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 活动统计概览 */}
        {statsData && (statsData.moduleStats?.length > 0 || statsData.actionStats?.length > 0) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 模块统计 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  {isZh ? "模块活动统计" : "Module Activity Stats"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {statsData.moduleStats?.map((stat: any) => {
                    const maxCount = statsData.moduleStats?.[0]?.count || 1;
                    const percentage = Math.round((stat.count / maxCount) * 100);
                    return (
                      <div key={stat.module} className="flex items-center gap-3">
                        <span className="text-sm w-20 text-gray-600 shrink-0">
                          {getModuleLabel(stat.module)}
                        </span>
                        <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                          <div
                            className="bg-blue-500 h-2.5 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{stat.count}</span>
                      </div>
                    );
                  })}
                  {(!statsData.moduleStats || statsData.moduleStats.length === 0) && (
                    <p className="text-sm text-gray-400 text-center py-4">{isZh ? "暂无数据" : "No data"}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* 操作类型统计 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  {isZh ? "操作类型统计" : "Action Type Stats"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {statsData.actionStats?.map((stat: any) => {
                    const maxCount = statsData.actionStats?.[0]?.count || 1;
                    const percentage = Math.round((stat.count / maxCount) * 100);
                    return (
                      <div key={stat.action} className="flex items-center gap-3">
                        <span className="text-sm w-28 text-gray-600 shrink-0">
                          {getActionLabel(stat.action)}
                        </span>
                        <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                          <div
                            className="bg-green-500 h-2.5 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{stat.count}</span>
                      </div>
                    );
                  })}
                  {(!statsData.actionStats || statsData.actionStats.length === 0) && (
                    <p className="text-sm text-gray-400 text-center py-4">{isZh ? "暂无数据" : "No data"}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 日志详情对话框 */}
        <Dialog open={!!selectedLog} onOpenChange={() => setSelectedLog(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {isZh ? "活动日志详情" : "Activity Log Details"}
              </DialogTitle>
              <DialogDescription>
                {isZh ? "查看用户操作的完整信息" : "View complete user activity information"}
              </DialogDescription>
            </DialogHeader>
            {selectedLog && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-500">{isZh ? "操作时间" : "Time"}</Label>
                    <p className="font-medium">{formatDateTime(selectedLog.createdAt)}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{isZh ? "用户" : "User"}</Label>
                    <p className="font-medium">{selectedLog.userName || "-"}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{isZh ? "角色" : "Role"}</Label>
                    <Badge className={getRoleColor(selectedLog.userRole)}>
                      {getRoleLabel(selectedLog.userRole)}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-gray-500">{isZh ? "操作类型" : "Action"}</Label>
                    <Badge className={getActionColor(selectedLog.action)}>
                      {getActionLabel(selectedLog.action)}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-gray-500">{isZh ? "操作模块" : "Module"}</Label>
                    <p className="font-medium">{getModuleLabel(selectedLog.module)}</p>
                  </div>
                  <div>
                    <Label className="text-gray-500">{isZh ? "操作结果" : "Result"}</Label>
                    <Badge className={selectedLog.result === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                      {selectedLog.result === "success" ? (isZh ? "成功" : "Success") : (isZh ? "失败" : "Failed")}
                    </Badge>
                  </div>
                </div>
                {selectedLog.targetType && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-gray-500">{isZh ? "目标类型" : "Target Type"}</Label>
                      <p className="font-medium">{selectedLog.targetType}</p>
                    </div>
                    <div>
                      <Label className="text-gray-500">{isZh ? "目标名称" : "Target Name"}</Label>
                      <p className="font-medium">{selectedLog.targetName || "-"}</p>
                    </div>
                  </div>
                )}
                <div>
                  <Label className="text-gray-500">{isZh ? "操作描述" : "Description"}</Label>
                  <p className="font-medium mt-1">{selectedLog.description || "-"}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                  <div>
                    <Label className="text-gray-400">{isZh ? "用户ID" : "User ID"}</Label>
                    <p>{selectedLog.userId}</p>
                  </div>
                  {selectedLog.targetId && (
                    <div>
                      <Label className="text-gray-400">{isZh ? "目标ID" : "Target ID"}</Label>
                      <p>{selectedLog.targetId}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
      </main>
    </div>
  );
}
