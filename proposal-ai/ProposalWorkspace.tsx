import { useLocation, useParams } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { Streamdown } from "streamdown";
import {
  ArrowLeft,
  FlaskConical,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  Clock,
  Loader2,
  RefreshCw,
  Check,
  Download,
  History,
  Edit3,
  AlertCircle,
  Lock,
  FileText,
  Send,
  X,
} from "lucide-react";
import { useState, useEffect } from "react";

export default function ProposalWorkspace() {
  const { id: proposalId } = useParams<{ id: string }>();
  const [, navigate] = useLocation();
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [editingContent, setEditingContent] = useState<string>("");

  const numericProposalId = parseInt(proposalId || "0");
  const isValidId = !isNaN(numericProposalId) && numericProposalId > 0;

  const proposalQuery = trpc.proposal.getById.useQuery(
    { proposalId: numericProposalId },
    { enabled: isValidId, retry: false }
  );

  const sectionsQuery = trpc.proposal.getSections.useQuery(
    { proposalId: numericProposalId },
    { enabled: isValidId && !proposalQuery.isError, retry: false }
  );

  const historyQuery = trpc.proposal.getHistory.useQuery(
    { proposalId: numericProposalId },
    { enabled: isValidId && !proposalQuery.isError, retry: false }
  );

  const generateMutation = trpc.proposal.generateSection.useMutation();
  const confirmMutation = trpc.proposal.confirmSection.useMutation();
  const exportMutation = trpc.proposal.exportWord.useMutation();

  // 切换章节时同步内容到编辑区（必须在所有条件return之前）
  useEffect(() => {
    const sectionsList = sectionsQuery.data || [];
    const section = selectedSection
      ? sectionsList.find((s) => s.key === selectedSection)
      : sectionsList[0];
    const content = section ? ((section.content as string) || "") : "";
    setEditingContent(content);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSection, sectionsQuery.dataUpdatedAt]);

  if (proposalQuery.isLoading || sectionsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
          <p className="text-slate-500 text-sm">正在加载申报书...</p>
        </div>
      </div>
    );
  }

  if (proposalQuery.isError || !proposalQuery.data) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-6 text-center max-w-md px-6">
          <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-800 mb-2">申报书不存在</h2>
            <p className="text-slate-500 text-sm">
              该申报书不存在或您没有访问权限。可能是链接已失效，或该申报书属于其他账号。
            </p>
          </div>
          <Button
            onClick={() => navigate("/")}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            返回首页
          </Button>
        </div>
      </div>
    );
  }

  const proposal = proposalQuery.data;
  const sections = sectionsQuery.data || [];
  const currentSection = selectedSection
    ? sections.find((s) => s.key === selectedSection)
    : sections[0];

  const handleGenerate = async () => {
    if (!currentSection) return;
    // 前置条件检查：在前端直接提示，不走后端报错
    const unmetDeps = (currentSection.dependencies || []).filter((dep: string) => {
      const depSection = sections.find((s) => s.key === dep);
      return depSection?.status !== "confirmed" && depSection?.status !== "draft_ready";
    });
    if (unmetDeps.length > 0) {
      const depTitles = unmetDeps.map((dep: string) => {
        const depSection = sections.find((s) => s.key === dep);
        return depSection?.title || dep;
      });
      toast.warning(`请先完成以下章节：${depTitles.join("、")}`);
      return;
    }
    try {
      await generateMutation.mutateAsync({
        proposalId: parseInt(proposalId || "0"),
        sectionKey: currentSection.key,
      });
      toast.success("章节内容已生成");
      sectionsQuery.refetch();
    } catch (error: unknown) {
      // 识别前置条件错误，显示友好提示而不是通用错误
      const msg = (error as { message?: string })?.message || "";
      if (msg.includes("请先完成以下章节")) {
        toast.warning(msg);
      } else {
        toast.error("生成失败，请重试");
      }
    }
  };

  const handleConfirm = async () => {
    if (!currentSection) return;
    try {
      await confirmMutation.mutateAsync({
        proposalId: parseInt(proposalId || "0"),
        sectionKey: currentSection.key,
        content: editingContent || (currentSection.content as string) || "",
      });
      toast.success("章节已确认");
      sectionsQuery.refetch();
    } catch (error) {
      toast.error("确认失败，请重试");
    }
  };

  const handleExport = async () => {
    try {
      const result = await exportMutation.mutateAsync({
        proposalId: parseInt(proposalId || "0"),
      });
      // 下载文件（浏览器兼容方式，不使用Node.js Buffer）
      const binaryStr = atob(result.buffer);
      const bytes = new Uint8Array(binaryStr.length);
      for (let i = 0; i < binaryStr.length; i++) {
        bytes[i] = binaryStr.charCodeAt(i);
      }
      const blob = new Blob([bytes], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success("Word文档导出成功");
      setShowExport(false);
    } catch (error) {
      toast.error("导出失败，请重试");
    }
  };

  const confirmedCount = sections.filter((s) => s.status === "confirmed").length;
  const progress = sections.length > 0 ? (confirmedCount / sections.length) * 100 : 0;

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* 顶部导航栏 */}
      <div className="border-b bg-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <h1 className="text-xl font-bold">{proposal?.title}</h1>
              <p className="text-sm text-muted-foreground">
                {proposal?.researchField}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowHistory(!showHistory)}
            >
              <History className="w-4 h-4 mr-2" />
              历史记录
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowExport(!showExport)}
            >
              <Download className="w-4 h-4 mr-2" />
              导出Word
            </Button>
          </div>
        </div>

        {/* 进度条 */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              进度: {confirmedCount}/{sections.length} 章节
            </span>
            <span className="text-sm text-muted-foreground">{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      </div>

      {/* 主体区域 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 左侧：章节导航 */}
        <div className="w-64 border-r bg-slate-50 flex flex-col">
          <ScrollArea className="flex-1 h-0">
            <div className="p-4 space-y-2">
              {sections.map((section) => (
                <button
                  key={section.key}
                  onClick={() => setSelectedSection(section.key)}
                  className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                    selectedSection === section.key
                      ? "bg-blue-100 text-blue-900"
                      : "hover:bg-slate-100"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium truncate">
                      {section.title}
                    </span>
                    {section.status === "confirmed" ? (
                      <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                    ) : section.status === "generating" ? (
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600 flex-shrink-0" />
                    ) : (
                      <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {section.wordLimit}字
                  </div>
                </button>
              ))}
            </div>
          </ScrollArea>
        </div>

        {/* 中间：AI对话面板 */}
        <div className="flex-1 border-r bg-white flex flex-col">
          {currentSection ? (
            <>
              <div className="border-b p-4">
                <h2 className="text-lg font-bold">{currentSection.title}</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {currentSection.description}
                </p>
              </div>

              <ScrollArea className="flex-1 h-0 p-4">
                {currentSection.status === "confirmed" ? (
                  <div className="space-y-4">
                    <Badge variant="outline" className="bg-green-50">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      已确认
                    </Badge>
                    <Streamdown>{currentSection.content as string || ""}</Streamdown>
                  </div>
                ) : currentSection.content ? (
                  <div className="space-y-4">
                    <Badge variant="outline" className="bg-blue-50">
                      <Sparkles className="w-3 h-3 mr-1" />
                      待确认
                    </Badge>
                    <Streamdown>{currentSection.content}</Streamdown>
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    {(() => {
                      const unmetDeps = (currentSection.dependencies || []).filter((dep: string) => {
                        const depSection = sections.find((s) => s.key === dep);
                        return depSection?.status !== "confirmed" && depSection?.status !== "draft_ready";
                      });
                      if (unmetDeps.length > 0) {
                        const depTitles = unmetDeps.map((dep: string) => {
                          const depSection = sections.find((s) => s.key === dep);
                          return depSection?.title || dep;
                        });
                        return (
                          <div className="space-y-2">
                            <p className="text-amber-600 font-medium">需先完成前置章节</p>
                            <div className="text-sm space-y-1">
                              {depTitles.map((title: string, i: number) => (
                                <div key={i} className="flex items-center gap-1 justify-center text-amber-500">
                                  <span>→</span>
                                  <span>{title}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }
                      return <p>点击下方“生成内容”按鈕开始AI撰写</p>;
                    })()}
                  </div>
                )}
              </ScrollArea>

              <div className="border-t p-4 flex gap-2">
                <Button
                  onClick={handleGenerate}
                  disabled={
                    generateMutation.isPending ||
                    currentSection.status === "confirmed"
                  }
                  className="flex-1"
                >
                  {generateMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      生成内容
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              选择左侧章节开始编辑
            </div>
          )}
        </div>

        {/* 右侧：内容编辑区 */}
        <div className="w-80 border-l bg-white flex flex-col">
          <div className="border-b p-4">
            <h3 className="font-bold">内容编辑</h3>
          </div>

          {currentSection ? (
            <>
              <ScrollArea className="flex-1 h-0 p-4">
                <Textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  placeholder="编辑或粘贴内容..."
                  className="min-h-96 resize-none"
                />
                <div className="text-xs mt-2 flex justify-between items-center">
                  <span className={editingContent.length > currentSection.wordLimit ? "text-red-500 font-medium" : "text-muted-foreground"}>
                    字数: {editingContent.length} / {currentSection.wordLimit}
                  </span>
                  {editingContent.length > currentSection.wordLimit && (
                    <span className="text-red-500 text-xs">超出限制</span>
                  )}
                </div>
              </ScrollArea>

              <div className="border-t p-4 space-y-2">
                <Button
                  onClick={handleConfirm}
                  disabled={
                    confirmMutation.isPending ||
                    currentSection.status === "confirmed"
                  }
                  className="w-full"
                >
                  {confirmMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      确认中...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      确认章节
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              选择章节编辑
            </div>
          )}
        </div>
      </div>

      {/* 历史记录对话框 */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">操作历史</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowHistory(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <div className="space-y-2">
              {historyQuery.data?.map((log: any, idx: number) => (
                <div key={idx} className="p-3 bg-slate-50 rounded-md">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">{log.action}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(log.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {log.detail}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 导出对话框 */}
      {showExport && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">导出Word文档</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowExport(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <div className="bg-blue-50 p-4 rounded-md mb-4">
              <p className="text-sm">
                已确认章节: {confirmedCount}/{sections.length}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                仅导出已确认的章节内容
              </p>
            </div>
            <Button
              onClick={handleExport}
              disabled={exportMutation.isPending || confirmedCount === 0}
              className="w-full"
            >
              {exportMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  导出中...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  下载文档
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
