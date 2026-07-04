import { useState } from "react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { 
  ArrowLeft, 
  Search, 
  Trash2, 
  RefreshCw, 
  BookOpen,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
  Download,
  Plus,
  Upload
} from "lucide-react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { DialogTrigger } from "@/components/ui/dialog";
import * as XLSX from "xlsx";

export default function TopicLibraryManagement() {
  const [, navigate] = useLocation();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "published" | "used" | "withdrawn">("all");
  const [yearFilter, setYearFilter] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [cleanupDialogOpen, setCleanupDialogOpen] = useState(false);
  
  // 添加课题相关状态
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showBulkImportDialog, setShowBulkImportDialog] = useState(false);
  const [addForm, setAddForm] = useState({
    title: "",
    titleEn: "",
    teacherName: "",
    description: "",
    academicYear: "",
    publishedAt: "",
  });
  const [importFile, setImportFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);

  // 获取题库列表
  const { data: libraryData, isLoading, refetch } = trpc.admin.getTopicLibrary.useQuery({
    status: statusFilter,
    academicYear: yearFilter === "all" ? undefined : yearFilter,
    searchTerm: searchTerm || undefined,
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
    page,
    pageSize,
  });

  // 获取统计信息
  const { data: stats } = trpc.admin.getTopicLibraryStats.useQuery();

  // 获取所有学年
  const { data: years } = trpc.admin.getAllYears.useQuery();

  // 删除单个记录
  const deleteMutation = trpc.admin.deleteTopicLibraryItem.useMutation({
    onSuccess: () => {
      toast.success("删除成功");
      refetch();
      setSelectedIds([]);
    },
    onError: (error) => {
      toast.error(error.message || "删除失败");
    },
  });

  // 批量删除
  const batchDeleteMutation = trpc.admin.batchDeleteTopicLibrary.useMutation({
    onSuccess: () => {
      toast.success("批量删除成功");
      refetch();
      setSelectedIds([]);
      setDeleteDialogOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "批量删除失败");
    },
  });

  // 清理旧记录
  const cleanupMutation = trpc.admin.cleanupOldTopicLibrary.useMutation({
    onSuccess: (data) => {
      toast.success(`清理完成，共删除 ${data.deletedCount} 条记录`);
      refetch();
      setCleanupDialogOpen(false);
    },
    onError: (error) => {
      toast.error(error.message || "清理失败");
    },
  });

  // 添加单个课题
  const addMutation = trpc.admin.adminAddTopicLibraryItem.useMutation({
    onSuccess: (data) => {
      if (data.success) {
        toast.success(data.message);
        refetch();
        setShowAddDialog(false);
        resetAddForm();
      } else {
        toast.error(data.message);
      }
    },
    onError: (error) => {
      toast.error("添加失败：" + error.message);
    }
  });

  // 批量导入课题
  const bulkImportMutation = trpc.admin.adminBulkImportTopicLibrary.useMutation({
    onSuccess: (result) => {
      if (result.success > 0) {
        toast.success(`成功导入 ${result.success} 个课题`);
      }
      if (result.failed > 0) {
        // 显示具体的错误信息
        const errorDetails = result.errors.map((e: { index: number; title: string; error: string }) => 
          `第${e.index}行 "${e.title}": ${e.error}`
        ).join("\n");
        toast.error(`${result.failed} 个课题导入失败\n${errorDetails}`, { duration: 8000 });
        console.error("导入错误详情:", JSON.stringify(result.errors, null, 2));
      }
      refetch();
      setShowBulkImportDialog(false);
      setImportFile(null);
      setIsImporting(false);
      setPreviewData([]);
      setShowPreview(false);
    },
    onError: (error) => {
      toast.error("导入失败：" + error.message);
      setIsImporting(false);
    }
  });

  const resetAddForm = () => {
    setAddForm({
      title: "",
      titleEn: "",
      teacherName: "",
      description: "",
      academicYear: "",
      publishedAt: "",
    });
  };

  const handleAddTopic = () => {
    if (!addForm.title) {
      toast.error("请填写课题标题");
      return;
    }
    addMutation.mutate(addForm);
  };

  // 下载导入模板
  const downloadTemplate = () => {
    const headers = [
      "课题标题(title)*",
      "导师姓名(teacherName)",
      "课题描述(description)",
      "学年(academicYear)",
      "发布时间(publishedAt)",
    ];
    const exampleRow = [
      "基于深度学习的图像识别系统研究",
      "张三",
      "本课题研究...",
      "2024-2025",
      "2024-09-01",
    ];
    const notes = [
      "说明：",
      "1. *标记的字段为必填项",
      "2. 发布时间格式：YYYY-MM-DD，不填则默认为当前时间",
      "3. 学年不填则默认为当前学年",
      "4. 课题标题必须唯一，重复的标题将导入失败",
      "5. 英文标题默认与课题标题一致，无需填写",
    ];

    const wb = XLSX.utils.book_new();
    const wsData = [headers, exampleRow, [], ...notes.map(n => [n])];
    const ws = XLSX.utils.aoa_to_sheet(wsData);
    ws["!cols"] = headers.map(() => ({ wch: 30 }));
    XLSX.utils.book_append_sheet(wb, ws, "题库导入模板");
    XLSX.writeFile(wb, "题库批量导入模板.xlsx");
  };

  // 解析Excel日期值（序列号或字符串）
  const parseExcelDate = (value: any): string => {
    if (!value) return "";
    
    // 如果是数字（Excel日期序列号）
    if (typeof value === "number") {
      // Excel日期序列号从1900-01-01开始，但有一个闰年bug需要减2
      const excelEpoch = new Date(1899, 11, 30); // 1899-12-30
      const date = new Date(excelEpoch.getTime() + value * 24 * 60 * 60 * 1000);
      return date.toISOString().split("T")[0]; // 返回 YYYY-MM-DD 格式
    }
    
    // 如果是 Date 对象
    if (value instanceof Date) {
      return value.toISOString().split("T")[0];
    }
    
    // 如果是字符串，直接返回
    return String(value).trim();
  };

  // 解析导入文件
  const handleFileImport = async () => {
    if (!importFile) {
      toast.error("请先选择文件");
      return;
    }
    setIsImporting(true);

    try {
      const arrayBuffer = await importFile.arrayBuffer();
      // 使用 cellDates: true 让xlsx库自动解析日期
      const workbook = XLSX.read(arrayBuffer, { type: "array", cellDates: true });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      // 使用 raw: false 获取格式化后的值，但日期会被转为Date对象
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, raw: false, dateNF: "yyyy-mm-dd" }) as any[][];

      if (jsonData.length < 2) {
        toast.error("文件中没有有效数据");
        setIsImporting(false);
        return;
      }

      const items: any[] = [];
      for (let i = 1; i < jsonData.length; i++) {
        const row = jsonData[i];
        if (!row || row.length === 0) continue;
        const firstCell = String(row[0] || "").trim();
        if (!firstCell || firstCell.startsWith("说明") || /^\d+\./.test(firstCell)) continue;

        // 解析发布时间（现在是第5列，索引为4）
        let publishedAt = "";
        const dateValue = row[4];
        if (dateValue) {
          if (dateValue instanceof Date) {
            // Date对象，转换为 YYYY-MM-DD 格式
            const year = dateValue.getFullYear();
            const month = String(dateValue.getMonth() + 1).padStart(2, "0");
            const day = String(dateValue.getDate()).padStart(2, "0");
            publishedAt = `${year}-${month}-${day}`;
          } else if (typeof dateValue === "number") {
            // Excel日期序列号
            publishedAt = parseExcelDate(dateValue);
          } else {
            // 字符串
            publishedAt = String(dateValue).trim();
          }
        }

        // 英文标题默认与课题标题一致
        const title = String(row[0] || "").trim();
        items.push({
          title,
          titleEn: title, // 英文标题默认与课题标题一致
          teacherName: String(row[1] || "").trim(),
          description: String(row[2] || "").trim(),
          academicYear: String(row[3] || "").trim(),
          publishedAt,
        });
      }

      if (items.length === 0) {
        toast.error("没有找到有效的课题数据");
        setIsImporting(false);
        return;
      }

      setPreviewData(items);
      setShowPreview(true);
      setIsImporting(false);
      toast.success(`解析成功，共${items.length}条课题，请确认后导入`);
    } catch (error: any) {
      toast.error(`解析文件失败: ${error.message}`);
      setIsImporting(false);
    }
  };

  const handleConfirmImport = () => {
    if (previewData.length === 0) return;
    setIsImporting(true);
    bulkImportMutation.mutate({ items: previewData });
  };

  const handleCancelPreview = () => {
    setPreviewData([]);
    setShowPreview(false);
    setImportFile(null);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "published":
        return <Badge variant="default" className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" />已发布</Badge>;
      case "used":
        return <Badge variant="default" className="bg-blue-500"><BookOpen className="h-3 w-3 mr-1" />已使用</Badge>;
      case "withdrawn":
        return <Badge variant="secondary"><XCircle className="h-3 w-3 mr-1" />已撤回</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked && libraryData?.items) {
      setSelectedIds(libraryData.items.map(item => item.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectItem = (id: number, checked: boolean) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter(i => i !== id));
    }
  };

  const handleBatchDelete = () => {
    if (selectedIds.length === 0) {
      toast.error("请先选择要删除的记录");
      return;
    }
    setDeleteDialogOpen(true);
  };

  const confirmBatchDelete = () => {
    batchDeleteMutation.mutate({ ids: selectedIds });
  };

  const handleExport = () => {
    if (!libraryData?.items) return;
    
    const headers = ["ID", "课题标题", "导师姓名", "学年", "选题来源", "科研项目名称", "状态", "发布时间"];
    const rows = libraryData.items.map(item => [
      item.id,
      item.title,
      item.teacherName || "",
      item.academicYear || "",
      item.topicSource || "",
      item.researchProjectName || "",
      item.status === "published" ? "已发布" : item.status === "used" ? "已使用" : "已撤回",
      item.publishedAt ? new Date(item.publishedAt).toLocaleString() : ""
    ]);
    
    const csvContent = [
      headers.join(","),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
    ].join("\n");
    
    const blob = new Blob(["\ufeff" + csvContent], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `题库导出_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white border-b">
        <div className="container py-4">
          <Button variant="ghost" onClick={() => navigate("/admin")} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回控制台
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">题库管理</h1>
          <p className="text-gray-600 mt-2">管理已发布的课题信息，支持筛选、删除和自动清理三年前的记录</p>
        </div>
      </div>

      <div className="container py-8">
        {/* 统计卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>题库总数</CardDescription>
              <CardTitle className="text-2xl">{stats?.total || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-green-200 bg-green-50">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-500" />
                已发布
              </CardDescription>
              <CardTitle className="text-2xl text-green-700">{stats?.published || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <BookOpen className="h-4 w-4 text-blue-500" />
                已使用
              </CardDescription>
              <CardTitle className="text-2xl text-blue-700">{stats?.used || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <XCircle className="h-4 w-4 text-gray-500" />
                已撤回
              </CardDescription>
              <CardTitle className="text-2xl">{stats?.withdrawn || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1">
                <Clock className="h-4 w-4 text-orange-500" />
                保留期限
              </CardDescription>
              <CardTitle className="text-xl">3年</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* 按学年统计 */}
        {stats?.byYear && stats.byYear.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">按学年统计</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                {stats.byYear.map(item => (
                  <div key={item.year} className="flex items-center gap-2 bg-gray-100 px-3 py-2 rounded-lg">
                    <span className="font-medium">{item.year}</span>
                    <Badge variant="secondary">{item.count} 个课题</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 筛选和操作 */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="搜索课题标题或导师姓名..."
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setPage(1);
                    }}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={statusFilter} onValueChange={(v: any) => { setStatusFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[140px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="状态筛选" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部状态</SelectItem>
                  <SelectItem value="published">已发布</SelectItem>
                  <SelectItem value="used">已使用</SelectItem>
                  <SelectItem value="withdrawn">已撤回</SelectItem>
                </SelectContent>
              </Select>

              <Select value={yearFilter} onValueChange={(v) => { setYearFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="学年筛选" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部学年</SelectItem>
                  {years?.map(year => (
                    <SelectItem key={year.id} value={year.yearName}>{year.displayName || year.yearName}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500 whitespace-nowrap">发布时间:</span>
                <Input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
                  className="w-[140px]"
                  placeholder="开始日期"
                />
                <span className="text-gray-400">-</span>
                <Input
                  type="date"
                  value={dateTo}
                  onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
                  className="w-[140px]"
                  placeholder="结束日期"
                />
                {(dateFrom || dateTo) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => { setDateFrom(""); setDateTo(""); setPage(1); }}
                    className="px-2"
                  >
                    清除
                  </Button>
                )}
              </div>

              <Button variant="outline" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                刷新
              </Button>

              <Button variant="outline" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                导出CSV
              </Button>

              <Button onClick={() => setShowAddDialog(true)}>
                <Plus className="h-4 w-4 mr-2" />
                添加课题
              </Button>

              <Button variant="outline" onClick={() => setShowBulkImportDialog(true)}>
                <Upload className="h-4 w-4 mr-2" />
                批量导入
              </Button>

              {selectedIds.length > 0 && (
                <Button variant="destructive" onClick={handleBatchDelete}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  删除选中 ({selectedIds.length})
                </Button>
              )}

              <Button variant="outline" onClick={() => setCleanupDialogOpen(true)}>
                <Clock className="h-4 w-4 mr-2" />
                清理旧记录
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 题库列表 */}
        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <div className="text-center py-8 text-gray-500">加载中...</div>
            ) : !libraryData?.items || libraryData.items.length === 0 ? (
              <div className="text-center py-8 text-gray-500">暂无数据</div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[50px]">
                          <Checkbox
                            checked={selectedIds.length === libraryData.items.length && libraryData.items.length > 0}
                            onCheckedChange={handleSelectAll}
                          />
                        </TableHead>
                        <TableHead>课题标题</TableHead>
                        <TableHead>导师</TableHead>
                        <TableHead>学年</TableHead>
                        <TableHead>选题来源</TableHead>
                        <TableHead>科研项目名称</TableHead>
                        <TableHead className="text-center">状态</TableHead>
                        <TableHead>发布时间</TableHead>
                        <TableHead className="text-center">操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {libraryData.items.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>
                            <Checkbox
                              checked={selectedIds.includes(item.id)}
                              onCheckedChange={(checked) => handleSelectItem(item.id, checked as boolean)}
                            />
                          </TableCell>
                          <TableCell>
                            <div className="max-w-[400px]">
                              <div className="font-medium truncate" title={item.title}>
                                {item.title}
                              </div>
                              {item.titleEn && (
                                <div className="text-xs text-gray-500 truncate" title={item.titleEn}>
                                  {item.titleEn}
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{item.teacherName || "-"}</TableCell>
                          <TableCell>{item.academicYear || "-"}</TableCell>
                          <TableCell>
                            <div className="max-w-[150px] truncate" title={item.topicSource || ""}>
                              {item.topicSource || "-"}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="max-w-[150px] truncate" title={item.researchProjectName || ""}>
                              {item.researchProjectName || "-"}
                            </div>
                          </TableCell>
                          <TableCell className="text-center">
                            {getStatusBadge(item.status)}
                          </TableCell>
                          <TableCell>
                            {item.publishedAt ? new Date(item.publishedAt).toLocaleString() : "-"}
                          </TableCell>
                          <TableCell className="text-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700"
                              onClick={() => {
                                if (confirm("确定要删除这条记录吗？")) {
                                  deleteMutation.mutate({ id: item.id });
                                }
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* 分页 */}
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-500">
                    共 {libraryData.total} 条记录，第 {page} 页
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page <= 1}
                      onClick={() => setPage(p => p - 1)}
                    >
                      上一页
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page * pageSize >= libraryData.total}
                      onClick={() => setPage(p => p + 1)}
                    >
                      下一页
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 批量删除确认对话框 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除选中的 {selectedIds.length} 条记录吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button 
              variant="destructive" 
              onClick={confirmBatchDelete}
              disabled={batchDeleteMutation.isPending}
            >
              {batchDeleteMutation.isPending ? "删除中..." : "确认删除"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 清理旧记录确认对话框 */}
      <Dialog open={cleanupDialogOpen} onOpenChange={setCleanupDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>清理旧记录</DialogTitle>
            <DialogDescription>
              此操作将删除三年前发布的所有课题记录。确定要继续吗？
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCleanupDialogOpen(false)}>
              取消
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => cleanupMutation.mutate()}
              disabled={cleanupMutation.isPending}
            >
              {cleanupMutation.isPending ? "清理中..." : "确认清理"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 添加课题对话框 */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>添加课题到题库</DialogTitle>
            <DialogDescription>
              手动添加以前已发布但系统未登记的课题，防止其他导师发布相同标题的课题
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">课题标题 *</Label>
              <Input
                id="title"
                value={addForm.title}
                onChange={(e) => setAddForm({ ...addForm, title: e.target.value })}
                placeholder="请输入课题标题（必填）"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="titleEn">英文标题</Label>
              <Input
                id="titleEn"
                value={addForm.titleEn}
                onChange={(e) => setAddForm({ ...addForm, titleEn: e.target.value })}
                placeholder="请输入英文标题（选填）"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="teacherName">导师姓名</Label>
                <Input
                  id="teacherName"
                  value={addForm.teacherName}
                  onChange={(e) => setAddForm({ ...addForm, teacherName: e.target.value })}
                  placeholder="请输入导师姓名"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="academicYear">学年</Label>
                <Select
                  value={addForm.academicYear}
                  onValueChange={(v) => setAddForm({ ...addForm, academicYear: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择学年（默认当前学年）" />
                  </SelectTrigger>
                  <SelectContent>
                    {years?.map(year => (
                      <SelectItem key={year.id} value={year.yearName}>
                        {year.displayName || year.yearName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="publishedAt">发布时间</Label>
              <Input
                id="publishedAt"
                type="date"
                value={addForm.publishedAt}
                onChange={(e) => setAddForm({ ...addForm, publishedAt: e.target.value })}
              />
              <p className="text-sm text-gray-500">不填则默认为当前时间</p>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">课题描述</Label>
              <Textarea
                id="description"
                value={addForm.description}
                onChange={(e) => setAddForm({ ...addForm, description: e.target.value })}
                placeholder="请输入课题描述（选填）"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowAddDialog(false); resetAddForm(); }}>
              取消
            </Button>
            <Button onClick={handleAddTopic} disabled={addMutation.isPending}>
              {addMutation.isPending ? "添加中..." : "确认添加"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 批量导入对话框 */}
      <Dialog open={showBulkImportDialog} onOpenChange={(open) => {
        setShowBulkImportDialog(open);
        if (!open) {
          setImportFile(null);
          setPreviewData([]);
          setShowPreview(false);
        }
      }}>
        <DialogContent className={showPreview ? "max-w-4xl max-h-[80vh] overflow-y-auto" : "max-w-lg"}>
          <DialogHeader>
            <DialogTitle>批量导入课题到题库</DialogTitle>
            <DialogDescription>
              下载Excel模板，填写课题信息后上传导入
            </DialogDescription>
          </DialogHeader>
          
          {!showPreview ? (
            <div className="space-y-4 py-4">
              <div className="flex gap-4">
                <Button variant="outline" onClick={downloadTemplate}>
                  <Download className="h-4 w-4 mr-2" />
                  下载导入模板
                </Button>
              </div>
              <div className="grid gap-2">
                <Label>选择文件</Label>
                <Input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                />
                <p className="text-sm text-gray-500">支持 .xlsx, .xls, .csv 格式</p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowBulkImportDialog(false)}>
                  取消
                </Button>
                <Button onClick={handleFileImport} disabled={!importFile || isImporting}>
                  {isImporting ? "解析中..." : "解析文件"}
                </Button>
              </DialogFooter>
            </div>
          ) : (
            <div className="space-y-4 py-4">
              <div className="text-sm text-gray-600">
                共解析到 <span className="font-bold text-blue-600">{previewData.length}</span> 条课题，请确认后导入
              </div>
              <div className="border rounded-lg overflow-x-auto max-h-[400px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">序号</TableHead>
                      <TableHead>课题标题</TableHead>
                      <TableHead>导师姓名</TableHead>
                      <TableHead>学年</TableHead>
                      <TableHead>发布时间</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {previewData.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{index + 1}</TableCell>
                        <TableCell className="max-w-[300px] truncate" title={item.title}>
                          {item.title}
                        </TableCell>
                        <TableCell>{item.teacherName || "-"}</TableCell>
                        <TableCell>{item.academicYear || "当前学年"}</TableCell>
                        <TableCell>{item.publishedAt || "当前时间"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={handleCancelPreview}>
                  返回修改
                </Button>
                <Button onClick={handleConfirmImport} disabled={isImporting}>
                  {isImporting ? "导入中..." : `确认导入 (${previewData.length} 条)`}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
