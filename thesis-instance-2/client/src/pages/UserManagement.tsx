import { useState, useRef } from "react";
import { trpc } from "@/lib/trpc";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { useLocation } from "wouter";
import { ArrowLeft, Users, Upload, Download, FileSpreadsheet, Trash2, AlertCircle, CheckCircle2, XCircle, Loader2, GraduationCap, Globe, LogOut, KeyRound, Ban, Plus, UserPlus, Settings, Copy } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import * as XLSX from "xlsx";

export default function UserManagement() {
  const { language, setLanguage, t } = useLanguage();
  const { user, loading, isAuthenticated, logout } = useAuth();
  const [, setLocation] = useLocation();
  const [searchTerm, setSearchTerm] = useState("");
  // 筛选状态
  const [teacherTypeFilter, setTeacherTypeFilter] = useState<string>("all");
  const [studentTypeFilter, setStudentTypeFilter] = useState<string>("all");
  const [studentMajorFilter, setStudentMajorFilter] = useState<string>("all");
  const [studentYearFilter, setStudentYearFilter] = useState<string>("all");
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importType, setImportType] = useState<"teacher" | "student">("teacher");
  const [importData, setImportData] = useState<any[]>([]);
  const [importErrors, setImportErrors] = useState<string[]>([]);
  const [importStep, setImportStep] = useState<"upload" | "preview" | "result">("upload");
  const [importResult, setImportResult] = useState<{ success: number; failed: number; errors: string[] } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // 批量删除状态
  const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set());
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false);
  
  // 单项创建用户状态
  const [showCreateTeacherDialog, setShowCreateTeacherDialog] = useState(false);
  const [showCreateStudentDialog, setShowCreateStudentDialog] = useState(false);

  // 批量修改状态
  const [showBatchPermissionDialog, setShowBatchPermissionDialog] = useState(false);
  const [showBatchQuotaDialog, setShowBatchQuotaDialog] = useState(false);
  // 管理员管理状态
  const [showCreateAdminDialog, setShowCreateAdminDialog] = useState(false);
  const [adminImportDialogOpen, setAdminImportDialogOpen] = useState(false);
  const [adminImportData, setAdminImportData] = useState<any[]>([]);
  const [adminImportStep, setAdminImportStep] = useState<"upload" | "preview" | "result">("upload");
  const [adminImportResult, setAdminImportResult] = useState<{ success: number; failed: number; errors: string[] } | null>(null);
  const adminFileInputRef = useRef<HTMLInputElement>(null);
  const [adminForm, setAdminForm] = useState({
    email: "",
    name: "",
    password: "",
  });
  // 修改初始密码状态
  const [showEditPasswordDialog, setShowEditPasswordDialog] = useState(false);
  const [editPasswordAdmin, setEditPasswordAdmin] = useState<{ id: number; name: string; email: string } | null>(null);
  const [newInitialPassword, setNewInitialPassword] = useState("");
  const [batchPermissionValue, setBatchPermissionValue] = useState(true);
  const [batchQuotaValue, setBatchQuotaValue] = useState(5);
  const [teacherForm, setTeacherForm] = useState({
    email: "",
    name: "",
    teacherType: "chinese" as "chinese" | "british",
    teacherNo: "",
    sussexEmail: "",
    annualQuota: 5,
    faculty: "萨塞克斯人工智能学院",
  });
  const [studentForm, setStudentForm] = useState({
    email: "",
    name: "",
    studentType: "non_transfer" as "transfer" | "non_transfer",
    studentMajor: "electronic_info" as "electronic_info" | "communication",
    studentId: "",
    sussexId: "",
    sussexEmail: "",
    studentClass: "",
    academicYear: "",
    namePinyin: "",
  });

  const utils = trpc.useUtils();
  const { data: users, isLoading, refetch } = trpc.admin.getUsers.useQuery(undefined, { 
    enabled: isAuthenticated && user?.role === "admin" 
  });
  const { data: currentYear } = trpc.admin.getCurrentYear.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin"
  });
  // 管理员列表查询
  const { data: admins, isLoading: adminsLoading } = trpc.admin.getAdmins.useQuery(undefined, {
    enabled: isAuthenticated && user?.role === "admin"
  });
  
  const deleteMutation = trpc.admin.deleteUser.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "用户已删除" : "User deleted");
      setSelectedUsers(new Set());
      utils.admin.getUsers.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const updateQuotaMutation = trpc.admin.updateTeacherQuota.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "限额已更新" : "Quota updated");
      utils.admin.getUsers.invalidate();
    },
    onError: (e) => toast.error(e.message),
  });

  const [resetPasswordResult, setResetPasswordResult] = useState<{ userName: string; newPassword: string } | null>(null);
  const [showResetResultDialog, setShowResetResultDialog] = useState(false);

  const resetPasswordMutation = trpc.admin.resetUserPassword.useMutation({
    onSuccess: (data) => {
      setResetPasswordResult({ userName: data.userName || "", newPassword: data.newPassword || "" });
      setShowResetResultDialog(true);
    },
    onError: (e) => toast.error(e.message),
  });

  const togglePublishMutation = trpc.admin.toggleTeacherPublish.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "发布权限已更新" : "Publish permission updated");
      utils.admin.getUsers.invalidate();
    },
    onError: (e) => toast.error(e.message),
  });

  const bulkImportMutation = trpc.admin.bulkImportUsers.useMutation({
    onSuccess: (result) => {
      setImportResult(result);
      setImportStep("result");
      if (result.success > 0) {
        utils.admin.getUsers.invalidate();
      }
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  // 单项创建管理员
  const createAdminMutation = trpc.admin.createAdmin.useMutation({
    onSuccess: (result) => {
      if (result.success) {
        toast.success(language === "zh" ? "管理员创建成功" : "Admin created successfully");
        setShowCreateAdminDialog(false);
        setAdminForm({ email: "", name: "", password: "" });
        utils.admin.getAdmins.invalidate();
      } else {
        toast.error(result.message);
      }
    },
    onError: (error) => toast.error(error.message),
  });

  // 删除管理员
  const deleteAdminMutation = trpc.admin.deleteAdmin.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "管理员已删除" : "Admin deleted");
      utils.admin.getAdmins.invalidate();
    },
    onError: (error) => toast.error(error.message),
  });

  // 修改管理员初始密码
  const updateAdminPasswordMutation = trpc.admin.updateAdminPassword.useMutation({
    onSuccess: () => {
      toast.success(language === "zh" ? "初始密码已修改" : "Initial password updated");
      utils.admin.getAdmins.invalidate();
      setShowEditPasswordDialog(false);
      setEditPasswordAdmin(null);
      setNewInitialPassword("");
    },
    onError: (error) => toast.error(error.message),
  });

  // 批量导入管理员
  const bulkImportAdminsMutation = trpc.admin.bulkImportAdmins.useMutation({
    onSuccess: (result) => {
      setAdminImportResult(result);
      setAdminImportStep("result");
      if (result.success > 0) {
        utils.admin.getAdmins.invalidate();
      }
    },
    onError: (error) => toast.error(error.message),
  });

  // 单项创建导师
  const createTeacherMutation = trpc.admin.createTeacher.useMutation({
    onSuccess: (result) => {
      if (result.success) {
        toast.success(language === "zh" ? "导师创建成功" : "Teacher created successfully");
        setShowCreateTeacherDialog(false);
        setTeacherForm({
          email: "",
          name: "",
          teacherType: "chinese",
          teacherNo: "",
          sussexEmail: "",
          annualQuota: 5,
          faculty: "萨塞克斯人工智能学院",
        });
        utils.admin.getUsers.invalidate();
      } else {
        toast.error(result.message);
      }
    },
    onError: (error) => toast.error(error.message),
  });

  // 单项创建学生
  const createStudentMutation = trpc.admin.createStudent.useMutation({
    onSuccess: (result) => {
      if (result.success) {
        toast.success(language === "zh" ? "学生创建成功" : "Student created successfully");
        setShowCreateStudentDialog(false);
        setStudentForm({
          email: "",
          name: "",
          studentType: "non_transfer",
          studentMajor: "electronic_info",
          studentId: "",
          sussexId: "",
          sussexEmail: "",
          studentClass: "",
          academicYear: "",
          namePinyin: "",
        });
        utils.admin.getUsers.invalidate();
      } else {
        toast.error(result.message);
      }
    },
    onError: (error) => toast.error(error.message),
  });

  // 批量修改发布权限
  const batchUpdatePermissionMutation = trpc.admin.batchUpdatePublishPermission.useMutation({
    onSuccess: (result) => {
      toast.success(language === "zh" 
        ? `成功更新 ${result.success} 个导师的发布权限` 
        : `Successfully updated ${result.success} teachers' publish permission`);
      setShowBatchPermissionDialog(false);
      setSelectedUsers(new Set());
      utils.admin.getUsers.invalidate();
    },
    onError: (error) => toast.error(error.message),
  });

  // 批量修改年度限额
  const batchUpdateQuotaMutation = trpc.admin.batchUpdateQuota.useMutation({
    onSuccess: (result) => {
      toast.success(language === "zh" 
        ? `成功更新 ${result.success} 个导师的年度限额` 
        : `Successfully updated ${result.success} teachers' quota`);
      setShowBatchQuotaDialog(false);
      setSelectedUsers(new Set());
      utils.admin.getUsers.invalidate();
    },
    onError: (error) => toast.error(error.message),
  });

  // 批量修改发布权限
  const handleBatchUpdatePermission = () => {
    const teacherIds = Array.from(selectedUsers);
    if (teacherIds.length === 0) {
      toast.error(language === "zh" ? "请先选择导师" : "Please select teachers first");
      return;
    }
    batchUpdatePermissionMutation.mutate({ teacherIds, canPublish: batchPermissionValue });
  };

  // 批量修改年度限额
  const handleBatchUpdateQuota = () => {
    const teacherIds = Array.from(selectedUsers);
    if (teacherIds.length === 0) {
      toast.error(language === "zh" ? "请先选择导师" : "Please select teachers first");
      return;
    }
    batchUpdateQuotaMutation.mutate({ teacherIds, quota: batchQuotaValue });
  };

  const handleCreateTeacher = () => {
    if (!teacherForm.name.trim()) {
      toast.error(language === "zh" ? "请输入导师姓名" : "Please enter teacher name");
      return;
    }
    if (!teacherForm.email.trim()) {
      toast.error(language === "zh" ? "请输入邮箱" : "Please enter email");
      return;
    }
    createTeacherMutation.mutate(teacherForm);
  };

  const handleCreateStudent = () => {
    if (!studentForm.name.trim()) {
      toast.error(language === "zh" ? "请输入学生姓名" : "Please enter student name");
      return;
    }
    if (!studentForm.studentId.trim()) {
      toast.error(language === "zh" ? "请输入中方学号" : "Please enter student ID");
      return;
    }
    createStudentMutation.mutate({
      ...studentForm,
      email: studentForm.studentId, // 学生用学号作为登录标识
    });
  };

  // 创建管理员
  const handleCreateAdmin = () => {
    if (!adminForm.name.trim()) {
      toast.error(language === "zh" ? "请输入管理员姓名" : "Please enter admin name");
      return;
    }
    if (!adminForm.email.trim()) {
      toast.error(language === "zh" ? "请输入登录账号" : "Please enter login account");
      return;
    }
    createAdminMutation.mutate(adminForm);
  };

  // 管理员文件上传处理
  const handleAdminFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = new Uint8Array(event.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: "array" });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];

        if (jsonData.length < 2) {
          toast.error(language === "zh" ? "文件为空或格式错误" : "File is empty or format error");
          return;
        }

        const headers = jsonData[0] as string[];
        const parsedData: any[] = [];

        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i];
          if (!row || row.length === 0) continue;

          const emailIdx = headers.findIndex(h => h?.toString().toLowerCase().includes("账号") || h?.toString().toLowerCase().includes("account") || h?.toString().toLowerCase().includes("email"));
          const nameIdx = headers.findIndex(h => h?.toString().toLowerCase().includes("姓名") || h?.toString().toLowerCase().includes("name"));
          const passwordIdx = headers.findIndex(h => h?.toString().toLowerCase().includes("密码") || h?.toString().toLowerCase().includes("password"));

          const email = row[emailIdx >= 0 ? emailIdx : 0]?.toString().trim();
          if (!email) continue;

          parsedData.push({
            email,
            name: row[nameIdx >= 0 ? nameIdx : 1]?.toString().trim() || email,
            password: row[passwordIdx >= 0 ? passwordIdx : 2]?.toString().trim() || "",
          });
        }

        setAdminImportData(parsedData);
        setAdminImportStep("preview");
      } catch (error) {
        toast.error(language === "zh" ? "文件解析失败" : "Failed to parse file");
      }
    };
    reader.readAsArrayBuffer(file);
  };

  // 管理员导入确认
  const handleAdminImportConfirm = () => {
    if (adminImportData.length === 0) {
      toast.error(language === "zh" ? "没有可导入的数据" : "No data to import");
      return;
    }
    bulkImportAdminsMutation.mutate({ admins: adminImportData });
  };

  // 管理员导入对话框关闭处理
  const handleAdminDialogClose = () => {
    setAdminImportDialogOpen(false);
    setAdminImportStep("upload");
    setAdminImportData([]);
    setAdminImportResult(null);
    if (adminFileInputRef.current) adminFileInputRef.current.value = "";
  };

  // 下载管理员模板
  const downloadAdminTemplate = () => {
    const wb = XLSX.utils.book_new();
    const templateData = [
      {
        "登录账号/Account": "admin001",
        "姓名/Name": "管理员一",
        "初始密码/Password": "zjsu@+账号前三位",
      },
    ];
    const ws = XLSX.utils.json_to_sheet(templateData);
    ws["!cols"] = [{ wch: 25 }, { wch: 20 }, { wch: 18 }];
    XLSX.utils.book_append_sheet(wb, ws, "管理员模板");
    XLSX.writeFile(wb, "管理员导入模板.xlsx");
  };

  const handleLogout = async () => { await logout(); setLocation("/"); };
  if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;

  const teachers = users?.filter(u => {
    if (u.role !== "teacher") return false;
    if (searchTerm && !u.name?.toLowerCase().includes(searchTerm.toLowerCase()) && !u.email?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (teacherTypeFilter !== "all" && u.teacherType !== teacherTypeFilter) return false;
    return true;
  }) || [];
  
  const students = users?.filter(u => {
    if (u.role !== "student") return false;
    if (searchTerm && !u.name?.toLowerCase().includes(searchTerm.toLowerCase()) && !u.email?.toLowerCase().includes(searchTerm.toLowerCase()) && !u.studentId?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (studentTypeFilter !== "all" && u.studentType !== studentTypeFilter) return false;
    if (studentMajorFilter !== "all" && u.studentMajor !== studentMajorFilter) return false;
    if (studentYearFilter !== "all" && u.academicYear !== studentYearFilter) return false;
    return true;
  }) || [];

  // 获取所有学年选项
  const academicYears = Array.from(new Set(users?.filter(u => u.role === "student" && u.academicYear).map(u => u.academicYear) || []));

  // 下载Excel模板
  const downloadTemplate = () => {
    const wb = XLSX.utils.book_new();
    
    if (importType === "teacher") {
      const templateData = [
        {
          "萨塞克斯邮箱/Sussex Email": "teacher@sussex.ac.uk",
          "初始密码/Password": "zjsu@+账号前三位",
          "姓名/Name": "张老师",
          "工号/Teacher No": "T001",
          "类型/Type": "中方",
        },
      ];
      const ws = XLSX.utils.json_to_sheet(templateData);
      ws["!cols"] = [{ wch: 30 }, { wch: 18 }, { wch: 15 }, { wch: 15 }, { wch: 10 }];
      XLSX.utils.book_append_sheet(wb, ws, "导师模板");
    } else {
      const templateData = [
        {
          "中方学号/Chinese ID": "20210001",
          "萨塞克斯学号/Sussex ID": "S12345",
          "萨塞克斯邮箱/Sussex Email": "s12345@sussex.ac.uk",
          "初始密码/Password": "zjsu@+账号前三位",
          "姓名/Name": "李同学",
          "姓名拼音/Name Pinyin": "Li Tongxue",
          "类型/Type": "非分流",
          "专业/Major": "电子信息工程",
          "班级/Class": "电子2101",
          "学院/Faculty": "信息学院",
        },
      ];
      const ws = XLSX.utils.json_to_sheet(templateData);
      ws["!cols"] = [{ wch: 20 }, { wch: 20 }, { wch: 28 }, { wch: 18 }, { wch: 15 }, { wch: 20 }, { wch: 10 }, { wch: 15 }, { wch: 15 }, { wch: 15 }];
      XLSX.utils.book_append_sheet(wb, ws, "学生模板");
    }
    
    XLSX.writeFile(wb, importType === "teacher" ? "导师导入模板.xlsx" : "学生导入模板.xlsx");
  };

  // 解析类型值
  const parseTeacherType = (value: string | undefined): "chinese" | "british" | undefined => {
    if (!value) return undefined;
    const v = String(value).toLowerCase().trim();
    if (v === "中方" || v === "chinese" || v === "中") return "chinese";
    if (v === "英方" || v === "british" || v === "英") return "british";
    return undefined;
  };

  const parseStudentType = (value: string | undefined): "transfer" | "non_transfer" | undefined => {
    if (!value) return undefined;
    const v = String(value).toLowerCase().trim();
    if (v === "分流" || v === "transfer" || v === "是") return "transfer";
    if (v === "非分流" || v === "non_transfer" || v === "non-transfer" || v === "否" || v === "非") return "non_transfer";
    return undefined;
  };

  const parseStudentMajor = (value: string | undefined): "electronic_info" | "communication" | undefined => {
    if (!value) return undefined;
    const v = String(value).toLowerCase().trim();
    if (v.includes("电子") || v === "electronic_info" || v === "electronic") return "electronic_info";
    if (v.includes("通信") || v === "communication") return "communication";
    return undefined;
  };

  // 处理文件上传
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: "array" });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);

        if (jsonData.length === 0) {
          toast.error(language === "zh" ? "文件为空或格式不正确" : "File is empty or format is incorrect");
          return;
        }

        // 解析数据
        const parsedData: any[] = [];
        const errors: string[] = [];

        jsonData.forEach((row: any, index) => {
          const rowNum = index + 2; // Excel行号从2开始（1是表头）
          
          if (importType === "teacher") {
            // 导师数据解析
            const sussexEmail = row["萨塞克斯邮箱/Sussex Email"] || row["萨塞克斯邮箱"] || row["Sussex Email"] || row["email"];
            const password = row["初始密码/Password"] || row["密码"] || row["Password"] || row["password"];
            const name = row["姓名/Name"] || row["姓名"] || row["Name"] || row["name"];
            const teacherNo = row["工号/Teacher No"] || row["工号"] || row["Teacher No"] || row["teacherNo"];
            const type = row["类型/Type"] || row["类型"] || row["Type"] || row["type"];

            if (!sussexEmail) {
              errors.push(`第${rowNum}行: 缺少萨塞克斯邮箱`);
              return;
            }

            parsedData.push({
              email: String(sussexEmail).trim(),
              sussexEmail: String(sussexEmail).trim(),
              password: password ? String(password) : "",
              name: name ? String(name).trim() : undefined,
              role: "teacher" as const,
              teacherType: parseTeacherType(type),
              teacherNo: teacherNo ? String(teacherNo).trim() : "0000000",
            });
          } else {
            // 学生数据解析
            const studentId = row["中方学号/Chinese ID"] || row["中方学号"] || row["Chinese ID"] || row["studentId"];
            const sussexId = row["萨塞克斯学号/Sussex ID"] || row["萨塞克斯学号"] || row["Sussex ID"] || row["sussexId"];
            const sussexEmail = row["萨塞克斯邮箱/Sussex Email"] || row["萨塞克斯邮箱"] || row["Sussex Email"] || row["sussexEmail"];
            const password = row["初始密码/Password"] || row["密码"] || row["Password"] || row["password"];
            const name = row["姓名/Name"] || row["姓名"] || row["Name"] || row["name"];
            const type = row["类型/Type"] || row["类型"] || row["Type"] || row["type"];
            const major = row["专业/Major"] || row["专业"] || row["Major"] || row["major"];
            const studentClass = row["班级/Class"] || row["班级"] || row["Class"] || row["class"];
            const faculty = row["学院/Faculty"] || row["学院"] || row["Faculty"] || row["faculty"];
            const namePinyin = row["姓名拼音/Name Pinyin"] || row["姓名拼音"] || row["Name Pinyin"] || row["namePinyin"];

            if (!studentId) {
              errors.push(`第${rowNum}行: 缺少中方学号`);
              return;
            }

            parsedData.push({
              email: String(studentId).trim(), // 中方学号作为登录名
              password: password ? String(password) : "",
              name: name ? String(name).trim() : undefined,
              role: "student" as const,
              studentId: String(studentId).trim(),
              sussexId: sussexId ? String(sussexId).trim() : undefined,
              sussexEmail: sussexEmail ? String(sussexEmail).trim() : undefined,
              studentType: parseStudentType(type),
              studentMajor: parseStudentMajor(major),
              studentClass: studentClass ? String(studentClass).trim() : undefined,
              faculty: faculty ? String(faculty).trim() : undefined,
              academicYear: currentYear?.yearName || undefined,
              namePinyin: namePinyin ? String(namePinyin).trim() : undefined,
            });
          }
        });

        setImportData(parsedData);
        setImportErrors(errors);
        setImportStep("preview");
      } catch (error) {
        console.error("解析文件失败:", error);
        toast.error(language === "zh" ? "解析文件失败" : "Failed to parse file");
      }
    };
    reader.readAsArrayBuffer(file);
  };

  // 执行导入
  const handleImport = () => {
    if (importData.length === 0) {
      toast.error(language === "zh" ? "没有可导入的数据" : "No data to import");
      return;
    }
    bulkImportMutation.mutate({ users: importData });
  };

  // 重置导入状态
  const resetImport = () => {
    setImportStep("upload");
    setImportData([]);
    setImportErrors([]);
    setImportResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // 关闭对话框
  const handleDialogClose = (open: boolean) => {
    if (!open) {
      resetImport();
    }
    setImportDialogOpen(open);
  };

  // 批量删除相关函数
  const toggleUserSelection = (userId: number) => {
    const newSelected = new Set(selectedUsers);
    if (newSelected.has(userId)) {
      newSelected.delete(userId);
    } else {
      newSelected.add(userId);
    }
    setSelectedUsers(newSelected);
  };

  const toggleSelectAll = (userList: typeof teachers | typeof students) => {
    const userIds = userList.map(u => u.id);
    const allSelected = userIds.every(id => selectedUsers.has(id));
    const newSelected = new Set(selectedUsers);
    if (allSelected) {
      userIds.forEach(id => newSelected.delete(id));
    } else {
      userIds.forEach(id => newSelected.add(id));
    }
    setSelectedUsers(newSelected);
  };

  const handleBulkDelete = async () => {
    if (selectedUsers.size === 0) {
      toast.error(language === "zh" ? "请选择要删除的用户" : "Please select users to delete");
      return;
    }
    
    try {
      for (const userId of Array.from(selectedUsers)) {
        await deleteMutation.mutateAsync({ id: userId });
      }
      toast.success(language === "zh" ? `已成功删除 ${selectedUsers.size} 个用户` : `Successfully deleted ${selectedUsers.size} users`);
      setSelectedUsers(new Set());
      setBulkDeleteDialogOpen(false);
    } catch (error) {
      toast.error(language === "zh" ? "批量删除失败" : "Bulk delete failed");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
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

      <main className="container mx-auto px-4 py-8">
        {/* 页面标题和操作栏 */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => setLocation("/admin")}>
              <ArrowLeft className="w-4 h-4 mr-2" />{t.back}
            </Button>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Users className="h-6 w-6 text-blue-600" />
              {language === "zh" ? "用户管理" : "User Management"}
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <Input
              placeholder={language === "zh" ? "搜索姓名、邮箱或学号..." : "Search name, email or student ID..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
            <Dialog open={importDialogOpen} onOpenChange={handleDialogClose}>
              <DialogTrigger asChild>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  {language === "zh" ? "批量导入" : "Bulk Import"}
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
                <DialogHeader>
                  <DialogTitle>
                    {language === "zh" ? "批量导入用户" : "Bulk Import Users"}
                  </DialogTitle>
                  <DialogDescription>
                    {language === "zh" 
                      ? "上传Excel文件批量导入导师或学生账号。导师使用萨塞克斯邮箱登录，学生使用中方学号登录，初始密码默认为zjsu@+账号前三位" 
                      : "Upload Excel file to import accounts. Teachers login with Sussex email, students login with Chinese ID. Default password: zjsu@ + first 3 chars of account"}
                  </DialogDescription>
                </DialogHeader>

                {importStep === "upload" && (
                  <div className="space-y-6 py-4">
                    {/* 选择导入类型 */}
                    <div className="space-y-2">
                      <Label>{language === "zh" ? "导入类型" : "Import Type"}</Label>
                      <Select value={importType} onValueChange={(v) => setImportType(v as "teacher" | "student")}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="teacher">
                            {language === "zh" ? "导师" : "Teachers"}
                          </SelectItem>
                          <SelectItem value="student">
                            {language === "zh" ? "学生" : "Students"}
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* 下载模板 */}
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-start gap-3">
                        <FileSpreadsheet className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div className="flex-1">
                          <h4 className="font-medium text-blue-900">
                            {language === "zh" ? "下载Excel模板" : "Download Excel Template"}
                          </h4>
                          <p className="text-sm text-blue-700 mt-1">
                            {language === "zh" 
                              ? "请先下载模板文件，按照模板格式填写数据后上传" 
                              : "Please download the template, fill in the data according to the format, and upload"}
                          </p>
                          <Button variant="outline" size="sm" className="mt-3" onClick={downloadTemplate}>
                            <Download className="h-4 w-4 mr-2" />
                            {language === "zh" 
                              ? (importType === "teacher" ? "下载导师模板" : "下载学生模板")
                              : (importType === "teacher" ? "Download Teacher Template" : "Download Student Template")}
                          </Button>
                        </div>
                      </div>
                    </div>

                    {/* 上传文件 */}
                    <div className="space-y-2">
                      <Label>{language === "zh" ? "上传文件" : "Upload File"}</Label>
                      <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept=".xlsx,.xls,.csv"
                          onChange={handleFileUpload}
                          className="hidden"
                          id="file-upload"
                        />
                        <label htmlFor="file-upload" className="cursor-pointer">
                          <Upload className="h-10 w-10 mx-auto text-gray-400 mb-3" />
                          <p className="text-sm text-gray-600">
                            {language === "zh" 
                              ? "点击或拖拽文件到此处上传" 
                              : "Click or drag file to upload"}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {language === "zh" 
                              ? "支持 .xlsx, .xls, .csv 格式" 
                              : "Supports .xlsx, .xls, .csv formats"}
                          </p>
                        </label>
                      </div>
                    </div>

                    {/* 字段说明 */}
                    <div className="text-sm text-gray-500">
                      <h4 className="font-medium text-gray-700 mb-2">
                        {language === "zh" ? "字段说明" : "Field Description"}
                      </h4>
                      {importType === "teacher" ? (
                        <ul className="list-disc list-inside space-y-1">
                          <li>{language === "zh" ? "萨塞克斯邮箱：必填，用于登录" : "Sussex Email: Required, used for login"}</li>
                          <li>{language === "zh" ? "初始密码：选填，默认zjsu@+账号前三位" : "Password: Optional, default zjsu@ + first 3 chars of account"}</li>
                          <li>{language === "zh" ? "姓名：选填" : "Name: Optional"}</li>
                          <li>{language === "zh" ? "工号：选填，默认0000000" : "Teacher No: Optional, default 0000000"}</li>
                          <li>{language === "zh" ? "类型：选填，中方/英方" : "Type: Optional, ZJSU/Sussex"}</li>
                        </ul>
                      ) : (
                        <ul className="list-disc list-inside space-y-1">
                          <li>{language === "zh" ? "中方学号：必填，用于登录" : "Chinese ID: Required, used for login"}</li>
                          <li>{language === "zh" ? "萨塞克斯学号：选填" : "Sussex ID: Optional"}</li>
                          <li>{language === "zh" ? "初始密码：选填，默认zjsu@+账号前三位" : "Password: Optional, default zjsu@ + first 3 chars of account"}</li>
                          <li>{language === "zh" ? "姓名：选填" : "Name: Optional"}</li>
                          <li>{language === "zh" ? "姓名拼音：选填，如 Zhang San" : "Name Pinyin: Optional, e.g. Zhang San"}</li>
                          <li>{language === "zh" ? "类型：选填，分流/非分流" : "Type: Optional, Single-Degree/Dual-Degree"}</li>
                          <li>{language === "zh" ? "专业：选填，电子信息工程/通信工程" : "Major: Optional, Robotics and Electrical Engineering/Communications Engineering"}</li>
                          <li>{language === "zh" ? "班级：选填" : "Class: Optional"}</li>
                          <li>{language === "zh" ? "学院：选填" : "Faculty: Optional"}</li>
                        </ul>
                      )}
                    </div>
                  </div>
                )}

                {importStep === "preview" && (
                  <div className="flex-1 overflow-hidden flex flex-col space-y-4 py-4">
                    {/* 解析错误提示 */}
                    {importErrors.length > 0 && (
                      <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>{language === "zh" ? "解析警告" : "Parse Warnings"}</AlertTitle>
                        <AlertDescription>
                          <ul className="list-disc list-inside mt-2 text-sm">
                            {importErrors.slice(0, 5).map((error, index) => (
                              <li key={index}>{error}</li>
                            ))}
                            {importErrors.length > 5 && (
                              <li>...{language === "zh" ? `还有${importErrors.length - 5}条警告` : `${importErrors.length - 5} more warnings`}</li>
                            )}
                          </ul>
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* 数据预览 */}
                    <div className="flex-1 overflow-hidden">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">
                          {language === "zh" ? "数据预览" : "Data Preview"} ({importData.length} {language === "zh" ? "条记录" : "records"})
                        </h4>
                      </div>
                      <ScrollArea className="h-[300px] border rounded-lg">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>#</TableHead>
                              <TableHead>{importType === "teacher" ? (language === "zh" ? "萨塞克斯邮箱" : "Sussex Email") : (language === "zh" ? "中方学号" : "Chinese ID")}</TableHead>
                              {importType === "student" && <TableHead>{language === "zh" ? "萨塞克斯学号" : "Sussex ID"}</TableHead>}
                              <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                              {importType === "student" && <TableHead>{language === "zh" ? "姓名拼音" : "Name Pinyin"}</TableHead>}
                              <TableHead>{language === "zh" ? "类型" : "Type"}</TableHead>
                              {importType === "teacher" && <TableHead>{language === "zh" ? "工号" : "Teacher No"}</TableHead>}
                              {importType === "student" && <TableHead>{language === "zh" ? "专业" : "Major"}</TableHead>}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {importData.slice(0, 100).map((item, index) => (
                              <TableRow key={index}>
                                <TableCell>{index + 1}</TableCell>
                                <TableCell className="font-mono text-sm">{item.email}</TableCell>
                                {importType === "student" && <TableCell className="font-mono text-sm">{item.sussexId || "-"}</TableCell>}
                                <TableCell>{item.name || "-"}</TableCell>
                                {importType === "student" && <TableCell>{item.namePinyin || "-"}</TableCell>}
                                <TableCell>
                                  {importType === "teacher" 
                                    ? (item.teacherType === "chinese" ? (language === "zh" ? "中方" : "ZJSU") : item.teacherType === "british" ? (language === "zh" ? "英方" : "Sussex") : "-")
                                    : (item.studentType === "transfer" ? (language === "zh" ? "分流" : "Single-Degree") : item.studentType === "non_transfer" ? (language === "zh" ? "非分流" : "Dual-Degree") : "-")}
                                </TableCell>
                                {importType === "teacher" && <TableCell>{item.teacherNo || "0000000"}</TableCell>}
                                {importType === "student" && (
                                  <TableCell>
                                    {item.studentMajor === "electronic_info" ? (language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering") : item.studentMajor === "communication" ? (language === "zh" ? "通信工程" : "Communications Engineering") : "-"}
                                  </TableCell>
                                )}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                        {importData.length > 100 && (
                          <p className="text-center text-sm text-gray-500 py-2">
                            {language === "zh" ? `仅显示前100条，共${importData.length}条` : `Showing first 100 of ${importData.length} records`}
                          </p>
                        )}
                      </ScrollArea>
                    </div>

                    <DialogFooter>
                      <Button variant="outline" onClick={resetImport}>
                        {language === "zh" ? "重新上传" : "Re-upload"}
                      </Button>
                      <Button onClick={handleImport} disabled={importData.length === 0 || bulkImportMutation.isPending}>
                        {bulkImportMutation.isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                        {language === "zh" ? `确认导入 (${importData.length}条)` : `Confirm Import (${importData.length})`}
                      </Button>
                    </DialogFooter>
                  </div>
                )}

                {importStep === "result" && importResult && (
                  <div className="space-y-4 py-4">
                    {/* 导入结果统计 */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-5 w-5 text-green-600" />
                          <span className="font-medium text-green-900">
                            {language === "zh" ? "成功" : "Success"}
                          </span>
                        </div>
                        <p className="text-2xl font-bold text-green-600 mt-2">{importResult.success}</p>
                      </div>
                      <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                        <div className="flex items-center gap-2">
                          <XCircle className="h-5 w-5 text-red-600" />
                          <span className="font-medium text-red-900">
                            {language === "zh" ? "失败" : "Failed"}
                          </span>
                        </div>
                        <p className="text-2xl font-bold text-red-600 mt-2">{importResult.failed}</p>
                      </div>
                    </div>

                    {/* 错误详情 */}
                    {importResult.errors.length > 0 && (
                      <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>{language === "zh" ? "导入错误" : "Import Errors"}</AlertTitle>
                        <AlertDescription>
                          <ScrollArea className="h-[150px] mt-2">
                            <ul className="list-disc list-inside text-sm space-y-1">
                              {importResult.errors.map((error, index) => (
                                <li key={index}>{error}</li>
                              ))}
                            </ul>
                          </ScrollArea>
                        </AlertDescription>
                      </Alert>
                    )}

                    <DialogFooter>
                      <Button onClick={() => handleDialogClose(false)}>
                        {language === "zh" ? "完成" : "Done"}
                      </Button>
                    </DialogFooter>
                  </div>
                )}
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* 用户列表 Tabs */}
        <Tabs defaultValue="teachers">
          <TabsList>
            <TabsTrigger value="teachers">
              {language === "zh" ? "导师" : "Teachers"} ({teachers.length})
            </TabsTrigger>
            <TabsTrigger value="students">
              {language === "zh" ? "学生" : "Students"} ({students.length})
            </TabsTrigger>
            <TabsTrigger value="admins">
              {language === "zh" ? "管理员" : "Admins"} ({admins?.length || 0})
            </TabsTrigger>
          </TabsList>

          {/* 导师列表 */}
          <TabsContent value="teachers">
            <Card>
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <CardTitle>{language === "zh" ? "导师列表" : "Teacher List"}</CardTitle>
                    <CardDescription>
                      {language === "zh" ? "导师使用萨塞克斯邮箱登录，初始密码为zjsu@+账号前三位" : "Teachers login with Sussex email, initial password: zjsu@ + first 3 chars of account"}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Select value={teacherTypeFilter} onValueChange={setTeacherTypeFilter}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder={language === "zh" ? "类型" : "Type"} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{language === "zh" ? "全部类型" : "All Types"}</SelectItem>
                        <SelectItem value="chinese">{language === "zh" ? "中方" : "ZJSU"}</SelectItem>
                        <SelectItem value="british">{language === "zh" ? "英方" : "Sussex"}</SelectItem>
                      </SelectContent>
                    </Select>
                    {selectedUsers.size > 0 && (
                      <>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={() => setBulkDeleteDialogOpen(true)}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          {language === "zh" ? `删除 (${selectedUsers.size})` : `Delete (${selectedUsers.size})`}
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => setShowBatchPermissionDialog(true)}
                        >
                          <Settings className="h-4 w-4 mr-2" />
                          {language === "zh" ? `修改权限 (${selectedUsers.size})` : `Edit Permission (${selectedUsers.size})`}
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => setShowBatchQuotaDialog(true)}
                        >
                          <Settings className="h-4 w-4 mr-2" />
                          {language === "zh" ? `修改限额 (${selectedUsers.size})` : `Edit Quota (${selectedUsers.size})`}
                        </Button>
                      </>
                    )}
                    <Button onClick={() => setShowCreateTeacherDialog(true)}>
                      <UserPlus className="h-4 w-4 mr-2" />
                      {language === "zh" ? "添加导师" : "Add Teacher"}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">
                          <input
                            type="checkbox"
                            checked={teachers.length > 0 && teachers.every(t => selectedUsers.has(t.id))}
                            onChange={() => toggleSelectAll(teachers)}
                            className="cursor-pointer"
                          />
                        </TableHead>
                        <TableHead>ID</TableHead>
                        <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                        <TableHead>{language === "zh" ? "工号" : "Teacher No"}</TableHead>
                        <TableHead>{language === "zh" ? "萨塞克斯邮箱" : "Sussex Email"}</TableHead>
                        <TableHead>{language === "zh" ? "类型" : "Type"}</TableHead>
                        <TableHead>{language === "zh" ? "年度限额" : "Annual Quota"}</TableHead>
                        <TableHead>{language === "zh" ? "发布权限" : "Publish"}</TableHead>
                        <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {teachers.map((teacher) => (
                        <TableRow key={teacher.id}>
                          <TableCell>
                            <input
                              type="checkbox"
                              checked={selectedUsers.has(teacher.id)}
                              onChange={() => toggleUserSelection(teacher.id)}
                              className="cursor-pointer"
                            />
                          </TableCell>
                          <TableCell>{teacher.id}</TableCell>
                          <TableCell>{teacher.name || "-"}</TableCell>
                          <TableCell className="font-mono text-sm">{teacher.teacherNo || "0000000"}</TableCell>
                          <TableCell className="font-mono text-sm">{teacher.email}</TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {teacher.teacherType === "chinese" ? (language === "zh" ? "中方" : "ZJSU") : (language === "zh" ? "英方" : "Sussex")}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {teacher.teacherType === "chinese" ? (
                              <Input
                                type="number"
                                className="w-20"
                                defaultValue={teacher.annualQuota || 5}
                                onBlur={(e) => updateQuotaMutation.mutate({ userId: teacher.id, quota: parseInt(e.target.value) || 5 })}
                              />
                            ) : (
                              <span className="text-gray-500">{language === "zh" ? "不限" : "Unlimited"}</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Switch
                                checked={(teacher as any).canPublish === 1 || (teacher as any).canPublish === true}
                                onCheckedChange={(checked) => {
                                  togglePublishMutation.mutate({ teacherId: teacher.id, canPublish: checked });
                                }}
                              />
                              {((teacher as any).canPublish === 0 || (teacher as any).canPublish === false) && (
                                <Ban className="h-4 w-4 text-red-500" />
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  if (confirm(language === "zh" ? "确定要重置此用户密码吗？" : "Are you sure you want to reset this user's password?")) {
                                    resetPasswordMutation.mutate({ userId: teacher.id });
                                  }
                                }}
                                title={language === "zh" ? "重置密码" : "Reset Password"}
                              >
                                <KeyRound className="h-4 w-4 text-orange-500" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  if (confirm(language === "zh" ? "确定要删除此导师吗？" : "Are you sure you want to delete this teacher?")) {
                                    deleteMutation.mutate({ id: teacher.id });
                                  }
                                }}
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      {teachers.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                            {language === "zh" ? "没有找到导师" : "No teachers found"}
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 学生列表 */}
          <TabsContent value="students">
            <Card>
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <CardTitle>{language === "zh" ? "学生列表" : "Student List"}</CardTitle>
                    <CardDescription>
                      {language === "zh" ? "学生使用中方学号登录，初始密码为zjsu@+账号前三位。学生数据按学年隔离管理" : "Students login with Chinese ID, initial password: zjsu@ + first 3 chars of account. Student data is isolated by academic year"}
                    </CardDescription>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Select value={studentTypeFilter} onValueChange={setStudentTypeFilter}>
                      <SelectTrigger className="w-28">
                        <SelectValue placeholder={language === "zh" ? "类型" : "Type"} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{language === "zh" ? "全部" : "All"}</SelectItem>
                        <SelectItem value="transfer">{language === "zh" ? "分流" : "Single-Degree"}</SelectItem>
                        <SelectItem value="non_transfer">{language === "zh" ? "非分流" : "Dual-Degree"}</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={studentMajorFilter} onValueChange={setStudentMajorFilter}>
                      <SelectTrigger className="w-28">
                        <SelectValue placeholder={language === "zh" ? "专业" : "Major"} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{language === "zh" ? "全部" : "All"}</SelectItem>
                        <SelectItem value="electronic_info">{language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering"}</SelectItem>
                        <SelectItem value="communication">{language === "zh" ? "通信工程" : "Communications Engineering"}</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={studentYearFilter} onValueChange={setStudentYearFilter}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder={language === "zh" ? "学年" : "Year"} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{language === "zh" ? "全部学年" : "All Years"}</SelectItem>
                        {academicYears.map(year => (
                          <SelectItem key={year} value={year || "unknown"}>{year}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {selectedUsers.size > 0 && (
                      <Button 
                        variant="destructive" 
                        size="sm"
                        onClick={() => setBulkDeleteDialogOpen(true)}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        {language === "zh" ? `删除 (${selectedUsers.size})` : `Delete (${selectedUsers.size})`}
                      </Button>
                    )}
                    <Button onClick={() => setShowCreateStudentDialog(true)}>
                      <UserPlus className="h-4 w-4 mr-2" />
                      {language === "zh" ? "添加学生" : "Add Student"}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">
                          <input
                            type="checkbox"
                            checked={students.length > 0 && students.every(s => selectedUsers.has(s.id))}
                            onChange={() => toggleSelectAll(students)}
                            className="cursor-pointer"
                          />
                        </TableHead>
                        <TableHead>ID</TableHead>
                        <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                        <TableHead>{language === "zh" ? "姓名拼音" : "Name Pinyin"}</TableHead>
                        <TableHead>{language === "zh" ? "中方学号" : "Chinese ID"}</TableHead>
                        <TableHead>{language === "zh" ? "萨塞克斯学号" : "Sussex ID"}</TableHead>
                        <TableHead>{language === "zh" ? "萨塞克斯邮箱" : "Sussex Email"}</TableHead>
                        <TableHead>{language === "zh" ? "类型" : "Type"}</TableHead>
                        <TableHead>{language === "zh" ? "专业" : "Major"}</TableHead>
                        <TableHead>{language === "zh" ? "学年" : "Year"}</TableHead>
                        <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {students.map((student) => (
                        <TableRow key={student.id}>
                          <TableCell>
                            <input
                              type="checkbox"
                              checked={selectedUsers.has(student.id)}
                              onChange={() => toggleUserSelection(student.id)}
                              className="cursor-pointer"
                            />
                          </TableCell>
                          <TableCell>{student.id}</TableCell>
                          <TableCell>{student.name || "-"}</TableCell>
                          <TableCell>{(student as any).namePinyin || "-"}</TableCell>
                          <TableCell className="font-mono text-sm">{student.studentId || "-"}</TableCell>
                          <TableCell className="font-mono text-sm">{student.sussexId || "-"}</TableCell>
                          <TableCell className="text-sm">{student.sussexEmail || "-"}</TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {student.studentType === "transfer" ? (language === "zh" ? "分流" : "Single-Degree") : (language === "zh" ? "非分流" : "Dual-Degree")}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {student.studentMajor === "electronic_info" ? (language === "zh" ? "电子信息工程" : "Robotics and Electrical Engineering") : student.studentMajor === "communication" ? (language === "zh" ? "通信工程" : "Communications Engineering") : "-"}
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{student.academicYear || "-"}</Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  if (confirm(language === "zh" ? "确定要重置此用户密码吗？" : "Are you sure you want to reset this user's password?")) {
                                    resetPasswordMutation.mutate({ userId: student.id });
                                  }
                                }}
                                title={language === "zh" ? "重置密码" : "Reset Password"}
                              >
                                <KeyRound className="h-4 w-4 text-orange-500" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  if (confirm(language === "zh" ? "确定要删除此学生吗？" : "Are you sure you want to delete this student?")) {
                                    deleteMutation.mutate({ id: student.id });
                                  }
                                }}
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      {students.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                            {language === "zh" ? "没有找到学生" : "No students found"}
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 管理员列表 */}
          <TabsContent value="admins">
            <Card>
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <CardTitle>{language === "zh" ? "管理员列表" : "Admin List"}</CardTitle>
                    <CardDescription>
                      {language === "zh" ? "管理员使用账号密码登录，初始密码为zjsu@+账号前三位" : "Admins login with account and password, initial password: zjsu@ + first 3 chars of account"}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" onClick={() => setAdminImportDialogOpen(true)}>
                      <Upload className="h-4 w-4 mr-2" />
                      {language === "zh" ? "批量导入" : "Bulk Import"}
                    </Button>
                    <Button onClick={() => setShowCreateAdminDialog(true)}>
                      <UserPlus className="h-4 w-4 mr-2" />
                      {language === "zh" ? "添加管理员" : "Add Admin"}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {adminsLoading ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                        <TableHead>{language === "zh" ? "登录账号" : "Account"}</TableHead>
                        <TableHead>{language === "zh" ? "初始密码" : "Initial Password"}</TableHead>
                        <TableHead>{language === "zh" ? "创建时间" : "Created At"}</TableHead>
                        <TableHead>{language === "zh" ? "操作" : "Actions"}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {admins?.map((admin) => (
                        <TableRow key={admin.id}>
                          <TableCell>{admin.id}</TableCell>
                          <TableCell>{admin.name || "-"}</TableCell>
                          <TableCell className="font-mono text-sm">{admin.email}</TableCell>
                          <TableCell className="font-mono text-sm">{admin.initialPassword || ("zjsu@" + (admin.email || "").slice(0, 3).toLowerCase())}</TableCell>
                          <TableCell>{admin.createdAt ? new Date(admin.createdAt).toLocaleDateString() : "-"}</TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setEditPasswordAdmin({ id: admin.id, name: admin.name || "", email: admin.email });
                                  setNewInitialPassword(admin.initialPassword || ("zjsu@" + (admin.email || "").slice(0, 3).toLowerCase()));
                                  setShowEditPasswordDialog(true);
                                }}
                                title={language === "zh" ? "修改初始密码" : "Edit Initial Password"}
                              >
                                <KeyRound className="h-4 w-4 text-orange-500" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  if (admin.id === user?.id) {
                                    toast.error(language === "zh" ? "不能删除自己的账号" : "Cannot delete your own account");
                                    return;
                                  }
                                  if (confirm(language === "zh" ? "确定要删除此管理员吗？" : "Are you sure you want to delete this admin?")) {
                                    deleteAdminMutation.mutate({ id: admin.id });
                                  }
                                }}
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      {(!admins || admins.length === 0) && (
                        <TableRow>
                          <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                            {language === "zh" ? "没有找到管理员" : "No admins found"}
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* 批量删除确认对话框 */}
      <Dialog open={bulkDeleteDialogOpen} onOpenChange={setBulkDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "确认批量删除" : "Confirm Bulk Delete"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `您即将删除 ${selectedUsers.size} 个用户，此操作不可恢复。是否继续？`
                : `You are about to delete ${selectedUsers.size} users. This action cannot be undone. Continue?`}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBulkDeleteDialogOpen(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleBulkDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "删除中..." : "Deleting..."}</>
              ) : (
                <><Trash2 className="h-4 w-4 mr-2" />{language === "zh" ? "确认删除" : "Confirm Delete"}</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 创建导师对话框 */}
      <Dialog open={showCreateTeacherDialog} onOpenChange={setShowCreateTeacherDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "添加导师" : "Add Teacher"}</DialogTitle>
            <DialogDescription>
              {language === "zh" ? "创建新导师账户，初始密码为zjsu@+账号前三位" : "Create a new teacher account, initial password: zjsu@ + first 3 chars of account"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>{language === "zh" ? "姓名 *" : "Name *"}</Label>
              <Input
                value={teacherForm.name}
                onChange={(e) => setTeacherForm({ ...teacherForm, name: e.target.value })}
                placeholder={language === "zh" ? "请输入导师姓名" : "Enter teacher name"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "萨塞克斯邮箱 *" : "Sussex Email *"}</Label>
              <Input
                type="email"
                value={teacherForm.email}
                onChange={(e) => setTeacherForm({ ...teacherForm, email: e.target.value, sussexEmail: e.target.value })}
                placeholder="xxx@sussex.ac.uk"
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "导师类型 *" : "Teacher Type *"}</Label>
              <Select value={teacherForm.teacherType} onValueChange={(v: "chinese" | "british") => setTeacherForm({ ...teacherForm, teacherType: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="chinese">{language === "zh" ? "中方导师" : "ZJSU Teacher"}</SelectItem>
                  <SelectItem value="british">{language === "zh" ? "英方导师" : "Sussex Teacher"}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "工号" : "Teacher No"}</Label>
              <Input
                value={teacherForm.teacherNo}
                onChange={(e) => setTeacherForm({ ...teacherForm, teacherNo: e.target.value })}
                placeholder={language === "zh" ? "可选" : "Optional"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "年度限额" : "Annual Quota"}</Label>
              <Input
                type="number"
                value={teacherForm.annualQuota}
                onChange={(e) => setTeacherForm({ ...teacherForm, annualQuota: parseInt(e.target.value) || 5 })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateTeacherDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleCreateTeacher} disabled={createTeacherMutation.isPending}>
              {createTeacherMutation.isPending ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "创建中..." : "Creating..."}</>
              ) : (
                language === "zh" ? "创建" : "Create"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 创建学生对话框 */}
      <Dialog open={showCreateStudentDialog} onOpenChange={setShowCreateStudentDialog}>
        <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "添加学生" : "Add Student"}</DialogTitle>
            <DialogDescription>
              {language === "zh" ? "创建新学生账户，初始密码为zjsu@+账号前三位" : "Create a new student account, initial password: zjsu@ + first 3 chars of account"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>{language === "zh" ? "姓名 *" : "Name *"}</Label>
              <Input
                value={studentForm.name}
                onChange={(e) => setStudentForm({ ...studentForm, name: e.target.value })}
                placeholder={language === "zh" ? "请输入学生姓名" : "Enter student name"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "姓名拼音" : "Name Pinyin"}</Label>
              <Input
                value={studentForm.namePinyin}
                onChange={(e) => setStudentForm({ ...studentForm, namePinyin: e.target.value })}
                placeholder={language === "zh" ? "可选" : "Optional"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "中方学号 *" : "Chinese ID *"}</Label>
              <Input
                value={studentForm.studentId}
                onChange={(e) => setStudentForm({ ...studentForm, studentId: e.target.value })}
                placeholder={language === "zh" ? "用于登录" : "Used for login"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "萨塞克斯学号" : "Sussex ID"}</Label>
              <Input
                value={studentForm.sussexId}
                onChange={(e) => setStudentForm({ ...studentForm, sussexId: e.target.value })}
                placeholder={language === "zh" ? "可选" : "Optional"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "萨塞克斯邮箱" : "Sussex Email"}</Label>
              <Input
                value={studentForm.sussexEmail || ""}
                onChange={(e) => setStudentForm({ ...studentForm, sussexEmail: e.target.value })}
                placeholder={language === "zh" ? "可选，如 xx@sussex.ac.uk" : "Optional, e.g. xx@sussex.ac.uk"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "类型 *" : "Type *"}</Label>
              <Select value={studentForm.studentType} onValueChange={(v: "transfer" | "non_transfer") => setStudentForm({ ...studentForm, studentType: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="non_transfer">{language === "zh" ? "非分流" : "Dual-Degree"}</SelectItem>
                  <SelectItem value="transfer">{language === "zh" ? "分流" : "Single-Degree"}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "专业 *" : "Major *"}</Label>
              <Select value={studentForm.studentMajor} onValueChange={(v: "electronic_info" | "communication") => setStudentForm({ ...studentForm, studentMajor: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="electronic_info">{language === "zh" ? "电子信息工程" : "Electronic Info"}</SelectItem>
                  <SelectItem value="communication">{language === "zh" ? "通信工程" : "Communication"}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "学年" : "Year"}</Label>
              <Input
                value={studentForm.academicYear}
                onChange={(e) => setStudentForm({ ...studentForm, academicYear: e.target.value })}
                placeholder={language === "zh" ? "如 2024-2025，留空则使用当前学年" : "e.g. 2024-2025, leave empty for current year"}
              />
            </div>

            <div className="space-y-2">
              <Label>{language === "zh" ? "班级" : "Class"}</Label>
              <Input
                value={studentForm.studentClass}
                onChange={(e) => setStudentForm({ ...studentForm, studentClass: e.target.value })}
                placeholder={language === "zh" ? "可选" : "Optional"}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateStudentDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleCreateStudent} disabled={createStudentMutation.isPending}>
              {createStudentMutation.isPending ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "创建中..." : "Creating..."}</>
              ) : (
                language === "zh" ? "创建" : "Create"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 批量修改发布权限对话框 */}
      <Dialog open={showBatchPermissionDialog} onOpenChange={setShowBatchPermissionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "批量修改发布权限" : "Batch Update Publish Permission"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `您即将修改 ${selectedUsers.size} 个导师的发布权限`
                : `You are about to update publish permission for ${selectedUsers.size} teachers`}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="flex items-center space-x-4">
              <Label>{language === "zh" ? "发布权限" : "Publish Permission"}</Label>
              <Switch
                checked={batchPermissionValue}
                onCheckedChange={setBatchPermissionValue}
              />
              <span className="text-sm text-gray-500">
                {batchPermissionValue 
                  ? (language === "zh" ? "开启" : "Enabled")
                  : (language === "zh" ? "关闭" : "Disabled")}
              </span>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBatchPermissionDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleBatchUpdatePermission} disabled={batchUpdatePermissionMutation.isPending}>
              {batchUpdatePermissionMutation.isPending ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "更新中..." : "Updating..."}</>
              ) : (
                language === "zh" ? "确认修改" : "Confirm"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 批量修改年度限额对话框 */}
      <Dialog open={showBatchQuotaDialog} onOpenChange={setShowBatchQuotaDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "批量修改年度限额" : "Batch Update Annual Quota"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `您即将修改 ${selectedUsers.size} 个导师的年度课题限额`
                : `You are about to update annual quota for ${selectedUsers.size} teachers`}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-2">
              <Label>{language === "zh" ? "年度课题限额" : "Annual Quota"}</Label>
              <Input
                type="number"
                min={0}
                value={batchQuotaValue}
                onChange={(e) => setBatchQuotaValue(parseInt(e.target.value) || 0)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBatchQuotaDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleBatchUpdateQuota} disabled={batchUpdateQuotaMutation.isPending}>
              {batchUpdateQuotaMutation.isPending ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "更新中..." : "Updating..."}</>
              ) : (
                language === "zh" ? "确认修改" : "Confirm"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 创建管理员对话框 */}
      <Dialog open={showCreateAdminDialog} onOpenChange={setShowCreateAdminDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "添加管理员" : "Add Admin"}</DialogTitle>
            <DialogDescription>
              {language === "zh" ? "创建新管理员账户，初始密码默认为zjsu@+账号前三位" : "Create a new admin account, default password: zjsu@ + first 3 chars of account"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>{language === "zh" ? "姓名 *" : "Name *"}</Label>
              <Input
                value={adminForm.name}
                onChange={(e) => setAdminForm({ ...adminForm, name: e.target.value })}
                placeholder={language === "zh" ? "请输入管理员姓名" : "Enter admin name"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "登录账号 *" : "Login Account *"}</Label>
              <Input
                value={adminForm.email}
                onChange={(e) => setAdminForm({ ...adminForm, email: e.target.value })}
                placeholder={language === "zh" ? "请输入登录账号" : "Enter login account"}
              />
            </div>
            <div className="space-y-2">
              <Label>{language === "zh" ? "初始密码" : "Initial Password"}</Label>
              <Input
                value={adminForm.password}
                onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })}
                placeholder="留留空则默认zjsu@+账号前三位"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateAdminDialog(false)}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button onClick={handleCreateAdmin} disabled={createAdminMutation.isPending}>
              {createAdminMutation.isPending ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "创建中..." : "Creating..."}</>
              ) : (
                language === "zh" ? "创建" : "Create"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 管理员批量导入对话框 */}
      <Dialog open={adminImportDialogOpen} onOpenChange={handleAdminDialogClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "批量导入管理员" : "Bulk Import Admins"}</DialogTitle>
            <DialogDescription>
              {language === "zh" ? "上传Excel文件批量导入管理员账户" : "Upload Excel file to bulk import admin accounts"}
            </DialogDescription>
          </DialogHeader>

          {adminImportStep === "upload" && (
            <div className="space-y-4 py-4">
              <div className="flex items-center gap-4">
                <Button variant="outline" onClick={downloadAdminTemplate}>
                  <Download className="h-4 w-4 mr-2" />
                  {language === "zh" ? "下载模板" : "Download Template"}
                </Button>
              </div>
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <input
                  ref={adminFileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleAdminFileUpload}
                  className="hidden"
                />
                <FileSpreadsheet className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-2">
                  {language === "zh" ? "点击或拖拽Excel文件到此处" : "Click or drag Excel file here"}
                </p>
                <Button onClick={() => adminFileInputRef.current?.click()}>
                  <Upload className="h-4 w-4 mr-2" />
                  {language === "zh" ? "选择文件" : "Select File"}
                </Button>
              </div>
            </div>
          )}

          {adminImportStep === "preview" && (
            <div className="space-y-4 py-4">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>{language === "zh" ? "数据预览" : "Data Preview"}</AlertTitle>
                <AlertDescription>
                  {language === "zh" 
                    ? `共解析到 ${adminImportData.length} 条记录，请确认后导入`
                    : `Found ${adminImportData.length} records, please confirm before import`}
                </AlertDescription>
              </Alert>
              <ScrollArea className="h-[300px] border rounded-lg">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{language === "zh" ? "登录账号" : "Account"}</TableHead>
                      <TableHead>{language === "zh" ? "姓名" : "Name"}</TableHead>
                      <TableHead>{language === "zh" ? "初始密码" : "Password"}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {adminImportData.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.email}</TableCell>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>{item.password}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
              <DialogFooter>
                <Button variant="outline" onClick={() => { setAdminImportStep("upload"); setAdminImportData([]); }}>
                  {language === "zh" ? "返回" : "Back"}
                </Button>
                <Button onClick={handleAdminImportConfirm} disabled={bulkImportAdminsMutation.isPending}>
                  {bulkImportAdminsMutation.isPending ? (
                    <><Loader2 className="h-4 w-4 mr-2 animate-spin" />{language === "zh" ? "导入中..." : "Importing..."}</>
                  ) : (
                    language === "zh" ? `确认导入 (${adminImportData.length}条)` : `Confirm Import (${adminImportData.length})`
                  )}
                </Button>
              </DialogFooter>
            </div>
          )}

          {adminImportStep === "result" && adminImportResult && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <span className="font-medium text-green-900">
                      {language === "zh" ? "成功" : "Success"}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-green-600 mt-2">{adminImportResult.success}</p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-5 w-5 text-red-600" />
                    <span className="font-medium text-red-900">
                      {language === "zh" ? "失败" : "Failed"}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-red-600 mt-2">{adminImportResult.failed}</p>
                </div>
              </div>
              {adminImportResult.errors.length > 0 && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>{language === "zh" ? "导入错误" : "Import Errors"}</AlertTitle>
                  <AlertDescription>
                    <ScrollArea className="h-[150px] mt-2">
                      <ul className="list-disc list-inside text-sm space-y-1">
                        {adminImportResult.errors.map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </ScrollArea>
                  </AlertDescription>
                </Alert>
              )}
              <DialogFooter>
                <Button onClick={handleAdminDialogClose}>
                  {language === "zh" ? "完成" : "Done"}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 修改初始密码对话框 */}
      <Dialog open={showEditPasswordDialog} onOpenChange={setShowEditPasswordDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{language === "zh" ? "修改初始密码" : "Edit Initial Password"}</DialogTitle>
            <DialogDescription>
              {language === "zh" 
                ? `修改管理员 ${editPasswordAdmin?.name || editPasswordAdmin?.email} 的初始密码`
                : `Edit initial password for admin ${editPasswordAdmin?.name || editPasswordAdmin?.email}`}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>{language === "zh" ? "新初始密码" : "New Initial Password"}</Label>
              <Input
                type="text"
                value={newInitialPassword}
                onChange={(e) => setNewInitialPassword(e.target.value)}
                placeholder={language === "zh" ? "请输入新的初始密码" : "Enter new initial password"}
              />
              <p className="text-sm text-gray-500">
                {language === "zh" 
                  ? "修改后，该管理员下次登录时需使用新密码"
                  : "After modification, the admin will need to use the new password to login"}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowEditPasswordDialog(false);
              setEditPasswordAdmin(null);
              setNewInitialPassword("");
            }}>
              {language === "zh" ? "取消" : "Cancel"}
            </Button>
            <Button 
              onClick={() => {
                if (!newInitialPassword.trim()) {
                  toast.error(language === "zh" ? "请输入新密码" : "Please enter new password");
                  return;
                }
                if (editPasswordAdmin) {
                  updateAdminPasswordMutation.mutate({
                    adminId: editPasswordAdmin.id,
                    newPassword: newInitialPassword.trim(),
                  });
                }
              }}
              disabled={updateAdminPasswordMutation.isPending}
            >
              {updateAdminPasswordMutation.isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {language === "zh" ? "确认修改" : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 重置密码结果对话框 */}
      <Dialog open={showResetResultDialog} onOpenChange={setShowResetResultDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-green-500" />
              {language === "zh" ? "密码重置成功" : "Password Reset Successful"}
            </DialogTitle>
            <DialogDescription>
              {language === "zh" ? "请将新密码告知该用户" : "Please inform the user of their new password"}
            </DialogDescription>
          </DialogHeader>
          {resetPasswordResult && (
            <div className="space-y-4 py-2">
              <div className="rounded-lg bg-green-50 border border-green-200 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{language === "zh" ? "用户" : "User"}</span>
                  <span className="font-medium">{resetPasswordResult.userName}</span>
                </div>
                <div className="border-t border-green-200" />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{language === "zh" ? "新密码" : "New Password"}</span>
                  <div className="flex items-center gap-2">
                    <code className="bg-white px-3 py-1.5 rounded border text-base font-bold tracking-wider text-green-700">
                      {resetPasswordResult.newPassword}
                    </code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(resetPasswordResult.newPassword);
                        toast.success(language === "zh" ? "密码已复制到剪贴板" : "Password copied to clipboard");
                      }}
                      title={language === "zh" ? "复制密码" : "Copy Password"}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500">
                {language === "zh"
                  ? "提示：默认密码规则为 zjsu@+账号前三位字符，请提醒用户登录后及时修改密码"
                  : "Note: Default password is zjsu@ + first 3 chars of account. Please remind the user to change password after login."}
              </p>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setShowResetResultDialog(false)}>
              {language === "zh" ? "确定" : "OK"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
