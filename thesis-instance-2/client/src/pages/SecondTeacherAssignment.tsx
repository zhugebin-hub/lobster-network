import { useState, useMemo } from "react";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Search, UserPlus, History, X, Upload, Download, ArrowLeft, FileSpreadsheet } from "lucide-react";
import * as XLSX from "xlsx";
import { Link } from "wouter";

export default function SecondTeacherAssignment() {
  const { user } = useAuth();
  const [search, setSearch] = useState("");
  const [firstTeacherFilter, setFirstTeacherFilter] = useState<string>("all");
  const [selectedMatch, setSelectedMatch] = useState<number | null>(null);
  const [selectedSecondTeacher, setSelectedSecondTeacher] = useState<string>("");
  const [showAssignDialog, setShowAssignDialog] = useState(false);
  const [showHistoryDialog, setShowHistoryDialog] = useState(false);
  const [historyMatchId, setHistoryMatchId] = useState<number | null>(null);
  const [showBatchDialog, setShowBatchDialog] = useState(false);
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [batchPreviewData, setBatchPreviewData] = useState<Array<{ studentName: string; secondTeacherName: string }>>([]);
  const [batchParseError, setBatchParseError] = useState("");

  const { data: currentYear } = trpc.admin.getCurrentYear.useQuery();

  const { data: students, isLoading, refetch } = trpc.secondTeacher.getStudents.useQuery({
    search: search || undefined,
    firstTeacherId: firstTeacherFilter !== "all" ? parseInt(firstTeacherFilter) : undefined,
    academicYear: currentYear?.yearName,
  });

  const { data: teachers } = trpc.secondTeacher.getTeachers.useQuery({});

  const { data: history } = trpc.secondTeacher.getHistory.useQuery(
    { matchId: historyMatchId! },
    { enabled: !!historyMatchId }
  );

  const assignMutation = trpc.secondTeacher.assign.useMutation({
    onSuccess: () => {
      toast.success("指派成功");
      setShowAssignDialog(false);
      setSelectedMatch(null);
      setSelectedSecondTeacher("");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const revokeMutation = trpc.secondTeacher.revoke.useMutation({
    onSuccess: () => {
      toast.success("撤销成功");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const batchAssignMutation = trpc.secondTeacher.batchAssign.useMutation({
    onSuccess: (result) => {
      if (result.success > 0) {
        toast.success(`成功指派 ${result.success} 条记录`);
      }
      if (result.failed.length > 0) {
        toast.error(`失败 ${result.failed.length} 条: ${result.failed.map(f => `${f.studentName}: ${f.error}`).join("; ")}`);
      }
      setShowBatchDialog(false);
      setBatchFile(null);
      setBatchPreviewData([]);
      setBatchParseError("");
      refetch();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const firstTeachers = useMemo(() => {
    if (!students) return [];
    const teacherMap = new Map<number, string>();
    students.forEach(s => {
      if (s.firstTeacherId && s.firstTeacherName) {
        teacherMap.set(s.firstTeacherId, s.firstTeacherName);
      }
    });
    return Array.from(teacherMap.entries()).map(([id, name]) => ({ id, name }));
  }, [students]);

  const handleAssign = () => {
    if (!selectedMatch || !selectedSecondTeacher) return;
    assignMutation.mutate({
      matchId: selectedMatch,
      secondTeacherId: parseInt(selectedSecondTeacher),
    });
  };

  const handleRevoke = (matchId: number) => {
    if (confirm("确定要撤销该学生的第二导师指派吗？")) {
      revokeMutation.mutate({ matchId });
    }
  };

  const handleBatchFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBatchFile(file);
    setBatchParseError("");
    setBatchPreviewData([]);

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const data = new Uint8Array(evt.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: "array" });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet);

        if (rows.length === 0) {
          setBatchParseError("文件中没有数据");
          return;
        }

        const headers = Object.keys(rows[0]);
        const studentNameCol = headers.find(h => /学生姓名|姓名/.test(String(h)));
        const secondTeacherCol = headers.find(h => /第二导师/.test(String(h)));

        if (!studentNameCol) {
          setBatchParseError("未找到“学生姓名”列，请确保 Excel 中包含该列");
          return;
        }
        if (!secondTeacherCol) {
          setBatchParseError("未找到“第二导师”列，请确保 Excel 中包含该列并已填写");
          return;
        }

        const assignments = rows
          .map(row => ({
            studentName: String(row[studentNameCol] || "").trim(),
            secondTeacherName: String(row[secondTeacherCol] || "").trim(),
          }))
          .filter(a => a.studentName && a.secondTeacherName);

        if (assignments.length === 0) {
          setBatchParseError("文件中没有有效的指派数据（学生姓名和第二导师姓名均不能为空）");
          return;
        }

        setBatchPreviewData(assignments);
      } catch {
        setBatchParseError("文件解析失败，请确保上传的是有效的 Excel 文件");
      }
    };
    reader.readAsArrayBuffer(file);
  };

  const handleBatchAssign = () => {
    if (batchPreviewData.length === 0 || !currentYear?.yearName) return;
    batchAssignMutation.mutate({
      assignments: batchPreviewData,
      academicYear: currentYear.yearName,
    });
  };

  const downloadTemplate = () => {
    const template = "学生姓名,第二导师姓名\n张三,李四\n王五,赵六";
    const blob = new Blob([template], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "第二导师指派模板.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportUnassignedStudents = () => {
    const unassigned = students?.filter(s => !s.secondTeacherId);
    if (!unassigned || unassigned.length === 0) {
      toast.error("没有未指派的学生可导出");
      return;
    }

    const data = unassigned.map((s, index) => ({
      "序号": index + 1,
      "学生姓名": s.studentName || "",
      "中方学号": s.chineseStudentId || "",
      "英方学号": s.britishStudentId || "",
      "第一导师": s.firstTeacherName || "",
      "论文题目": s.topicTitle || "",
      "第二导师姓名": "",
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    // 设置列宽
    ws["!cols"] = [
      { wch: 6 },   // 序号
      { wch: 12 },  // 学生姓名
      { wch: 16 },  // 中方学号
      { wch: 16 },  // 英方学号
      { wch: 14 },  // 第一导师
      { wch: 40 },  // 论文题目
      { wch: 14 },  // 第二导师姓名
    ];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "未指派学生");
    XLSX.writeFile(wb, `未指派第二导师学生列表_${currentYear?.yearName || ""}.xlsx`);
    toast.success(`已导出 ${unassigned.length} 名未指派学生`);
  };

  const handleViewHistory = (matchId: number) => {
    setHistoryMatchId(matchId);
    setShowHistoryDialog(true);
  };

  const openAssignDialog = (matchId: number) => {
    setSelectedMatch(matchId);
    setSelectedSecondTeacher("");
    setShowAssignDialog(true);
  };

  const getAvailableTeachers = (firstTeacherId: number) => {
    return teachers?.filter(t => t.id !== firstTeacherId) || [];
  };

  const selectedStudent = students?.find(s => s.matchId === selectedMatch);

  if (user?.role !== "admin") {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            您没有权限访问此页面
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">第二导师管理</h1>
          <p className="text-muted-foreground">为已匹配的学生指派第二导师</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">总学生数</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{students?.length || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">已指派</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {students?.filter(s => s.secondTeacherId).length || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">待指派</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {students?.filter(s => !s.secondTeacherId).length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索学生姓名或学号..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 w-64"
                />
              </div>
              <Select value={firstTeacherFilter} onValueChange={setFirstTeacherFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="筛选第一导师" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部第一导师</SelectItem>
                  {firstTeachers.map(t => (
                    <SelectItem key={t.id} value={t.id.toString()}>{t.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={exportUnassignedStudents}>
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                导出未指派学生
              </Button>
              <Button variant="outline" onClick={downloadTemplate}>
                <Download className="h-4 w-4 mr-2" />
                下载模板
              </Button>
              <Button variant="outline" onClick={() => setShowBatchDialog(true)}>
                <Upload className="h-4 w-4 mr-2" />
                批量导入
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">加载中...</div>
          ) : students?.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">暂无数据</div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>学生姓名</TableHead>
                    <TableHead>中方学号</TableHead>
                    <TableHead>英方学号</TableHead>
                    <TableHead>第一导师</TableHead>
                    <TableHead>论文题目</TableHead>
                    <TableHead>第二导师</TableHead>
                    <TableHead className="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {students?.map((student) => (
                    <TableRow key={student.matchId}>
                      <TableCell className="font-medium">{student.studentName || "-"}</TableCell>
                      <TableCell>{student.chineseStudentId || "-"}</TableCell>
                      <TableCell>{student.britishStudentId || "-"}</TableCell>
                      <TableCell>{student.firstTeacherName || "-"}</TableCell>
                      <TableCell className="max-w-xs truncate" title={student.topicTitle || "-"}>
                        {student.topicTitle || "-"}
                      </TableCell>
                      <TableCell>
                        {student.secondTeacherName ? (
                          <Badge variant="default">{student.secondTeacherName}</Badge>
                        ) : (
                          <Badge variant="secondary">未指派</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {student.secondTeacherId ? (
                            <>
                              <Button variant="ghost" size="sm" onClick={() => handleViewHistory(student.matchId)}>
                                <History className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="sm" onClick={() => handleRevoke(student.matchId)}>
                                <X className="h-4 w-4" />
                              </Button>
                            </>
                          ) : (
                            <Button variant="ghost" size="sm" onClick={() => openAssignDialog(student.matchId)}>
                              <UserPlus className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showAssignDialog} onOpenChange={setShowAssignDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>指派第二导师</DialogTitle>
            <DialogDescription>
              为学生 {selectedStudent?.studentName} 选择第二导师
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={selectedSecondTeacher} onValueChange={setSelectedSecondTeacher}>
              <SelectTrigger>
                <SelectValue placeholder="选择第二导师" />
              </SelectTrigger>
              <SelectContent>
                {selectedStudent && getAvailableTeachers(selectedStudent.firstTeacherId).map(t => (
                  <SelectItem key={t.id} value={t.id.toString()}>
                    {t.name} ({t.teacherType === "chinese" ? "中方" : t.teacherType === "british" ? "英方" : "未知"})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAssignDialog(false)}>取消</Button>
            <Button onClick={handleAssign} disabled={!selectedSecondTeacher || assignMutation.isPending}>
              {assignMutation.isPending ? "指派中..." : "确认指派"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showHistoryDialog} onOpenChange={setShowHistoryDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>指派历史</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            {history?.length === 0 ? (
              <div className="text-center text-muted-foreground py-4">暂无历史记录</div>
            ) : (
              <div className="space-y-3">
                {history?.map((record, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                    <div className="flex-1">
                      <div className="text-sm">
                        {record.action === "revoke" ? (
                          <span className="text-red-600">撤销指派</span>
                        ) : record.oldSecondTeacherId ? (
                          <span>变更: {record.oldSecondTeacherName || "未知"} → {record.newSecondTeacherName || "未知"}</span>
                        ) : (
                          <span className="text-green-600">指派: {record.newSecondTeacherName || "未知"}</span>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        操作人: {record.operatorName || "未知"} | 时间: {new Date(record.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowHistoryDialog(false)}>关闭</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showBatchDialog} onOpenChange={(open) => {
        setShowBatchDialog(open);
        if (!open) {
          setBatchFile(null);
          setBatchPreviewData([]);
          setBatchParseError("");
        }
      }}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>批量导入第二导师</DialogTitle>
            <DialogDescription>
              请上传 Excel 文件（可使用“导出未指派学生”功能导出的文件，填写“第二导师姓名”列后回导）
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="flex items-center gap-4">
              <Input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleBatchFileChange}
                className="flex-1"
              />
              {batchFile && (
                <span className="text-sm text-muted-foreground whitespace-nowrap">
                  {batchFile.name}
                </span>
              )}
            </div>

            {batchParseError && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                {batchParseError}
              </div>
            )}

            {batchPreviewData.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  解析成功，共 {batchPreviewData.length} 条有效指派记录：
                </p>
                <div className="max-h-64 overflow-y-auto rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">序号</TableHead>
                        <TableHead>学生姓名</TableHead>
                        <TableHead>第二导师姓名</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {batchPreviewData.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>{index + 1}</TableCell>
                          <TableCell>{item.studentName}</TableCell>
                          <TableCell>{item.secondTeacherName}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBatchDialog(false)}>取消</Button>
            <Button onClick={handleBatchAssign} disabled={batchPreviewData.length === 0 || batchAssignMutation.isPending}>
              {batchAssignMutation.isPending ? "导入中..." : `确认导入 (${batchPreviewData.length} 条)`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
