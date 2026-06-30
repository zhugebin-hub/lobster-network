import { useState } from "react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  FlaskConical,
  Building2,
  User,
  BookOpen,
  CheckCircle2,
  Loader2,
  Sparkles,
} from "lucide-react";

type ProposalType = "national_key_rd" | "national_sci_tech" | "nsfc";

const PROPOSAL_TYPES: Array<{ value: ProposalType; label: string; desc: string; color: string }> = [
  {
    value: "national_key_rd",
    label: "国家重点研发计划",
    desc: "面向国家重大战略需求，支持重大科学问题和关键技术攻关",
    color: "border-blue-300 bg-blue-50 hover:bg-blue-100",
  },
  {
    value: "national_sci_tech",
    label: "国家科技重大专项",
    desc: "聚焦国家战略目标，突破重大技术瓶颈",
    color: "border-purple-300 bg-purple-50 hover:bg-purple-100",
  },
  {
    value: "nsfc",
    label: "国家自然科学基金",
    desc: "支持基础研究，培育原始创新能力",
    color: "border-emerald-300 bg-emerald-50 hover:bg-emerald-100",
  },
];

interface FormData {
  title: string;
  abstract: string;
  researchField: string;
  proposalType: ProposalType;
  applicantUnit: string;
  principalInvestigatorName: string;
  principalInvestigatorEmail: string;
  principalInvestigatorPhone: string;
}

export default function ProposalConfig() {
  const [, navigate] = useLocation();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormData>({
    title: "",
    abstract: "",
    researchField: "",
    proposalType: "national_key_rd",
    applicantUnit: "",
    principalInvestigatorName: "",
    principalInvestigatorEmail: "",
    principalInvestigatorPhone: "",
  });
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});

  const createMutation = trpc.proposal.create.useMutation({
    onSuccess: (data) => {
      toast.success("申报书项目创建成功！");
      navigate(`/proposal/${data.id}`);
    },
    onError: (err) => {
      toast.error(`创建失败：${err.message}`);
    },
  });

  const update = (field: keyof FormData, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  const validateStep1 = () => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};
    if (!form.title.trim()) newErrors.title = "请输入项目名称";
    if (!form.abstract.trim()) newErrors.abstract = "请输入项目摘要";
    if (!form.researchField.trim()) newErrors.researchField = "请输入研究领域";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};
    if (!form.applicantUnit.trim()) newErrors.applicantUnit = "请输入申报单位";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) setStep(2);
    else if (step === 2 && validateStep2()) setStep(3);
  };

  const handleSubmit = () => {
    createMutation.mutate({
      title: form.title,
      researchField: form.researchField,
      applicantUnit: form.applicantUnit,
      principalInvestigator: form.principalInvestigatorName || "",
      piEmail: form.principalInvestigatorEmail || "",
      piPhone: form.principalInvestigatorPhone || "",
    });
  };

  const steps = [
    { num: 1, label: "项目信息", icon: <BookOpen className="h-4 w-4" /> },
    { num: 2, label: "单位信息", icon: <Building2 className="h-4 w-4" /> },
    { num: 3, label: "负责人信息", icon: <User className="h-4 w-4" /> },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航 */}
      <header className="sticky top-0 z-50 border-b border-border bg-white/80 backdrop-blur-md">
        <div className="container flex h-16 items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="gap-2 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            返回
          </Button>
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
              <FlaskConical className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold text-foreground">新建申报书</span>
          </div>
        </div>
      </header>

      <div className="container py-10 max-w-3xl mx-auto">
        {/* 步骤指示器 */}
        <div className="flex items-center justify-center mb-10">
          {steps.map((s, i) => (
            <div key={s.num} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all ${
                    step > s.num
                      ? "border-primary bg-primary text-primary-foreground"
                      : step === s.num
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-background text-muted-foreground"
                  }`}
                >
                  {step > s.num ? <CheckCircle2 className="h-5 w-5" /> : s.icon}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    step >= s.num ? "text-primary" : "text-muted-foreground"
                  }`}
                >
                  {s.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`mx-4 h-0.5 w-16 transition-all ${
                    step > s.num ? "bg-primary" : "bg-border"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* 步骤1：项目信息 */}
        {step === 1 && (
          <Card className="border-border shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                项目基本信息
              </CardTitle>
              <CardDescription>填写申报项目的核心信息，AI将基于此生成各章节内容</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title" className="text-sm font-medium">
                  项目名称 <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="title"
                  placeholder="例如：面向复杂场景的智能感知与决策关键技术研究"
                  value={form.title}
                  onChange={e => update("title", e.target.value)}
                  className={errors.title ? "border-destructive" : ""}
                />
                {errors.title && <p className="text-xs text-destructive">{errors.title}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="researchField" className="text-sm font-medium">
                  研究领域 <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="researchField"
                  placeholder="例如：人工智能、生物医学、新能源材料"
                  value={form.researchField}
                  onChange={e => update("researchField", e.target.value)}
                  className={errors.researchField ? "border-destructive" : ""}
                />
                {errors.researchField && <p className="text-xs text-destructive">{errors.researchField}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="abstract" className="text-sm font-medium">
                  项目摘要 <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="abstract"
                  placeholder="简要描述项目的研究背景、核心目标、主要研究内容和预期成果（200-500字）"
                  value={form.abstract}
                  onChange={e => update("abstract", e.target.value)}
                  rows={5}
                  className={errors.abstract ? "border-destructive" : ""}
                />
                {errors.abstract && <p className="text-xs text-destructive">{errors.abstract}</p>}
                <p className="text-xs text-muted-foreground">
                  详细的摘要有助于AI生成更高质量的章节内容
                </p>
              </div>

              <div className="space-y-3">
                <Label className="text-sm font-medium">
                  申报类型 <span className="text-destructive">*</span>
                </Label>
                <div className="grid grid-cols-1 gap-3">
                  {PROPOSAL_TYPES.map(type => (
                    <div
                      key={type.value}
                      onClick={() => update("proposalType", type.value)}
                      className={`cursor-pointer rounded-lg border-2 p-4 transition-all ${
                        form.proposalType === type.value
                          ? "border-primary bg-primary/5 shadow-sm"
                          : type.color
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-foreground">{type.label}</div>
                          <div className="text-sm text-muted-foreground mt-0.5">{type.desc}</div>
                        </div>
                        {form.proposalType === type.value && (
                          <CheckCircle2 className="h-5 w-5 text-primary flex-shrink-0" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 步骤2：单位信息 */}
        {step === 2 && (
          <Card className="border-border shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-primary" />
                申报单位信息
              </CardTitle>
              <CardDescription>填写项目申报单位的基本信息</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="applicantUnit" className="text-sm font-medium">
                  申报单位名称 <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="applicantUnit"
                  placeholder="例如：北京大学"
                  value={form.applicantUnit}
                  onChange={e => update("applicantUnit", e.target.value)}
                  className={errors.applicantUnit ? "border-destructive" : ""}
                />
                {errors.applicantUnit && (
                  <p className="text-xs text-destructive">{errors.applicantUnit}</p>
                )}
              </div>

              <div className="rounded-lg bg-muted/50 p-4 border border-border">
                <div className="flex items-start gap-3">
                  <Sparkles className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium text-foreground mb-1">提示</p>
                    <p>
                      单位信息将用于申报书封面页和相关章节的生成。您可以在创建后在工作区中进一步完善参与单位、团队成员等详细信息。
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 步骤3：负责人信息 */}
        {step === 3 && (
          <Card className="border-border shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-primary" />
                项目负责人信息
              </CardTitle>
              <CardDescription>填写项目负责人的基本信息（可选）</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="piName" className="text-sm font-medium">
                  负责人姓名
                </Label>
                <Input
                  id="piName"
                  placeholder="请输入项目负责人姓名"
                  value={form.principalInvestigatorName}
                  onChange={e => update("principalInvestigatorName", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="piEmail" className="text-sm font-medium">
                  负责人邮箱
                </Label>
                <Input
                  id="piEmail"
                  type="email"
                  placeholder="请输入联系邮箱"
                  value={form.principalInvestigatorEmail}
                  onChange={e => update("principalInvestigatorEmail", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="piPhone" className="text-sm font-medium">
                  负责人电话
                </Label>
                <Input
                  id="piPhone"
                  placeholder="请输入联系电话"
                  value={form.principalInvestigatorPhone}
                  onChange={e => update("principalInvestigatorPhone", e.target.value)}
                />
              </div>

              {/* 信息确认摘要 */}
              <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-3">
                <p className="text-sm font-medium text-foreground">确认项目信息</p>
                <div className="space-y-2 text-sm">
                  <div className="flex gap-2">
                    <span className="text-muted-foreground w-20 flex-shrink-0">项目名称</span>
                    <span className="text-foreground font-medium">{form.title}</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-muted-foreground w-20 flex-shrink-0">研究领域</span>
                    <span className="text-foreground">{form.researchField}</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-muted-foreground w-20 flex-shrink-0">申报类型</span>
                    <Badge variant="outline" className="text-xs">
                      {PROPOSAL_TYPES.find(t => t.value === form.proposalType)?.label}
                    </Badge>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-muted-foreground w-20 flex-shrink-0">申报单位</span>
                    <span className="text-foreground">{form.applicantUnit}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 操作按钮 */}
        <div className="flex items-center justify-between mt-6">
          <Button
            variant="outline"
            onClick={() => (step > 1 ? setStep(step - 1) : navigate("/"))}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            {step > 1 ? "上一步" : "取消"}
          </Button>

          {step < 3 ? (
            <Button onClick={handleNext} className="gap-2">
              下一步
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={createMutation.isPending}
              className="gap-2 min-w-[120px]"
            >
              {createMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  创建中...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  开始撰写
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
