import { describe, expect, it, vi, beforeEach } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

// Mock database helpers
vi.mock("./db", () => ({
  createProposal: vi.fn().mockResolvedValue({ insertId: 1 }),
  getProposalById: vi.fn().mockResolvedValue({
    id: 1,
    userId: 1,
    title: "测试项目",
    abstract: "测试摘要",
    researchField: "人工智能",
    proposalType: "national_key_rd",
    applicantUnit: "北京大学",
    principalInvestigatorName: "张三",
    principalInvestigatorEmail: null,
    principalInvestigatorPhone: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  }),
  getProposalsByUserId: vi.fn().mockResolvedValue([
    {
      id: 1,
      userId: 1,
      title: "测试项目",
      abstract: "测试摘要",
      researchField: "人工智能",
      proposalType: "national_key_rd",
      applicantUnit: "北京大学",
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ]),
  updateProposal: vi.fn().mockResolvedValue(undefined),
  deleteProposal: vi.fn().mockResolvedValue(undefined),
  createSection: vi.fn().mockResolvedValue(undefined),
  getProposalSections: vi.fn().mockResolvedValue([
    {
      id: 1,
      proposalId: 1,
      sectionKey: "project_intro",
      title: "申报项目简介",
      content: "测试内容",
      status: "draft_ready",
      wordCount: 100,
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ]),
  updateSection: vi.fn().mockResolvedValue(undefined),
  addOperationLog: vi.fn().mockResolvedValue(undefined),
  getOperationLogs: vi.fn().mockResolvedValue([
    {
      id: 1,
      proposalId: 1,
      action: "create",
      sectionKey: null,
      detail: "创建新项目",
      createdAt: new Date(),
    },
  ]),
}));

// Mock LLM
vi.mock("./_core/llm", () => ({
  invokeLLM: vi.fn().mockResolvedValue({
    choices: [
      {
        message: {
          content: "这是AI生成的测试内容，包含足够的中文字符以通过字数统计测试。",
        },
      },
    ],
  }),
}));

// Mock docx generator
vi.mock("./docxGenerator", () => ({
  generateDocxBuffer: vi.fn().mockResolvedValue(Buffer.from("mock-docx-content")),
}));

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createAuthContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "test-user-open-id",
    email: "test@example.com",
    name: "测试用户",
    loginMethod: "manus",
    role: "user",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
  };

  return {
    user,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: vi.fn(),
    } as unknown as TrpcContext["res"],
  };
}

describe("proposal router", () => {
  let ctx: TrpcContext;
  let caller: ReturnType<typeof appRouter.createCaller>;

  beforeEach(() => {
    ctx = createAuthContext();
    caller = appRouter.createCaller(ctx);
  });

  describe("proposal.create", () => {
    it("should create a proposal and return id", async () => {
      const result = await caller.proposal.create({
        title: "测试项目",
        researchField: "人工智能",
        applicantUnit: "北京大学",
        principalInvestigator: "张三",
        piEmail: "zhangsan@example.com",
        piPhone: "13800138000",
      });

      expect(result).toHaveProperty("id");
      expect(result.id).toBe(1);
      expect(result.title).toBe("测试项目");
    });
  });

  describe("proposal.list", () => {
    it("should return list of proposals for user", async () => {
      const result = await caller.proposal.list();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty("title");
    });
  });

  describe("proposal.getById", () => {
    it("should return proposal with sections", async () => {
      const result = await caller.proposal.getById({ proposalId: 1 });
      // API直接返回proposal对象，不是包装对象
      expect(result).toHaveProperty("id");
      expect(result.id).toBe(1);
    });
  });

  describe("proposal.confirmSection", () => {
    it("should confirm a section", async () => {
      const result = await caller.proposal.confirmSection({
        proposalId: 1,
        sectionKey: "project_intro",
      });
      expect(result.success).toBe(true);
    });
  });

  describe("proposal.getHistory", () => {
    it("should return operation logs", async () => {
      const result = await caller.proposal.getHistory({ proposalId: 1 });
      expect(Array.isArray(result)).toBe(true);
      expect(result[0]).toHaveProperty("action");
    });
  });

  describe("proposal.delete", () => {
    it("should delete a proposal", async () => {
      const result = await caller.proposal.delete({ proposalId: 1 });
      expect(result.success).toBe(true);
    });
  });

  describe("proposal.exportWord", () => {
    it("should export word document as base64", async () => {
      const result = await caller.proposal.exportWord({ proposalId: 1 });
      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("filename");
      expect(result).toHaveProperty("buffer");
      expect(result.success).toBe(true);
      expect(result.filename).toContain(".docx");
    });
  });
});

describe("auth.logout", () => {
  it("should clear session cookie and return success", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);
    const result = await caller.auth.logout();
    expect(result.success).toBe(true);
  });
});
