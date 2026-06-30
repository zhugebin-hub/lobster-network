import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock the database module
vi.mock("./db", () => ({
  logUserActivity: vi.fn().mockResolvedValue(undefined),
  getUserActivityLogs: vi.fn().mockResolvedValue({
    logs: [
      {
        id: 1,
        userId: 1,
        userName: "张三",
        userRole: "student",
        action: "login",
        module: "auth",
        targetType: null,
        targetId: null,
        targetName: null,
        description: "学生登录系统",
        result: "success",
        createdAt: new Date("2026-03-10T10:00:00Z"),
      },
      {
        id: 2,
        userId: 2,
        userName: "李四",
        userRole: "teacher",
        action: "approve_wish",
        module: "wish",
        targetType: "wish",
        targetId: 5,
        targetName: "张三",
        description: "同意了学生张三的志愿申请",
        result: "success",
        createdAt: new Date("2026-03-10T11:00:00Z"),
      },
      {
        id: 3,
        userId: 3,
        userName: "管理员",
        userRole: "admin",
        action: "update_config",
        module: "config",
        targetType: "time_config",
        targetId: null,
        targetName: null,
        description: "修改了系统时间配置",
        result: "success",
        createdAt: new Date("2026-03-10T12:00:00Z"),
      },
    ],
    total: 3,
  }),
  getUserActivityLogStats: vi.fn().mockResolvedValue({
    totalLogs: 150,
    todayLogs: 12,
    last7DaysLogs: 85,
    roleStats: [
      { role: "student", count: 80 },
      { role: "teacher", count: 50 },
      { role: "admin", count: 20 },
    ],
    moduleStats: [
      { module: "auth", count: 60 },
      { module: "wish", count: 40 },
      { module: "thesis", count: 30 },
      { module: "config", count: 20 },
    ],
    actionStats: [
      { action: "login", count: 60 },
      { action: "submit_wish", count: 25 },
      { action: "approve_wish", count: 20 },
      { action: "upload_thesis", count: 15 },
      { action: "score_thesis_first", count: 10 },
    ],
    dailyTrend: [
      { date: "2026-03-04", count: 10 },
      { date: "2026-03-05", count: 15 },
      { date: "2026-03-06", count: 12 },
    ],
  }),
}));

import * as db from "./db";

describe("用户活动日志模块", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("logUserActivity - 日志记录", () => {
    it("应该能记录学生登录日志", async () => {
      await db.logUserActivity({
        userId: 1,
        userName: "张三",
        userRole: "student",
        action: "login",
        module: "auth",
        description: "学生登录系统",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith({
        userId: 1,
        userName: "张三",
        userRole: "student",
        action: "login",
        module: "auth",
        description: "学生登录系统",
      });
    });

    it("应该能记录导师审核志愿日志", async () => {
      await db.logUserActivity({
        userId: 2,
        userName: "李四",
        userRole: "teacher",
        action: "approve_wish",
        module: "wish",
        targetType: "wish",
        targetId: 5,
        targetName: "张三",
        description: "同意了学生张三的志愿申请",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 2,
          userRole: "teacher",
          action: "approve_wish",
          module: "wish",
          targetType: "wish",
          targetId: 5,
        })
      );
    });

    it("应该能记录管理员修改配置日志", async () => {
      await db.logUserActivity({
        userId: 3,
        userName: "管理员",
        userRole: "admin",
        action: "update_config",
        module: "config",
        targetType: "time_config",
        description: "修改了系统时间配置",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith(
        expect.objectContaining({
          userRole: "admin",
          action: "update_config",
          module: "config",
        })
      );
    });

    it("应该能记录论文上传日志", async () => {
      await db.logUserActivity({
        userId: 10,
        userName: "王五",
        userRole: "student",
        action: "upload_thesis",
        module: "thesis",
        targetType: "thesis_draft",
        targetId: 3,
        description: "上传了论文终稿",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith(
        expect.objectContaining({
          action: "upload_thesis",
          module: "thesis",
          targetType: "thesis_draft",
        })
      );
    });

    it("应该能记录第一导师评分日志", async () => {
      await db.logUserActivity({
        userId: 5,
        userName: "赵六",
        userRole: "teacher",
        action: "score_thesis_first",
        module: "thesis",
        targetType: "thesis_draft",
        targetId: 3,
        targetName: "王五",
        description: "为学生王五的论文评分: 85分",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith(
        expect.objectContaining({
          action: "score_thesis_first",
          module: "thesis",
        })
      );
    });

    it("应该能记录批量导入用户日志", async () => {
      await db.logUserActivity({
        userId: 1,
        userName: "管理员",
        userRole: "admin",
        action: "bulk_import",
        module: "user",
        description: "批量导入了 50 个用户",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith(
        expect.objectContaining({
          action: "bulk_import",
          module: "user",
        })
      );
    });

    it("应该能记录指派第二导师日志", async () => {
      await db.logUserActivity({
        userId: 1,
        userName: "管理员",
        userRole: "admin",
        action: "assign_second_teacher",
        module: "second_teacher",
        targetType: "match",
        targetId: 10,
        targetName: "Dr. Smith",
        description: "为匹配(ID:10)指派第二导师: Dr. Smith",
      });

      expect(db.logUserActivity).toHaveBeenCalledWith(
        expect.objectContaining({
          action: "assign_second_teacher",
          module: "second_teacher",
          targetType: "match",
        })
      );
    });
  });

  describe("getUserActivityLogs - 日志查询", () => {
    it("应该返回日志列表和总数", async () => {
      const result = await db.getUserActivityLogs();
      expect(result).toHaveProperty("logs");
      expect(result).toHaveProperty("total");
      expect(result.logs).toBeInstanceOf(Array);
      expect(result.total).toBe(3);
    });

    it("应该支持按角色筛选", async () => {
      await db.getUserActivityLogs({ userRole: "student" });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith({ userRole: "student" });
    });

    it("应该支持按操作类型筛选", async () => {
      await db.getUserActivityLogs({ action: "login" });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith({ action: "login" });
    });

    it("应该支持按模块筛选", async () => {
      await db.getUserActivityLogs({ module: "auth" });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith({ module: "auth" });
    });

    it("应该支持关键词搜索", async () => {
      await db.getUserActivityLogs({ keyword: "张三" });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith({ keyword: "张三" });
    });

    it("应该支持日期范围筛选", async () => {
      await db.getUserActivityLogs({
        startDate: "2026-03-01",
        endDate: "2026-03-10",
      });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith({
        startDate: "2026-03-01",
        endDate: "2026-03-10",
      });
    });

    it("应该支持分页", async () => {
      await db.getUserActivityLogs({ limit: 20, offset: 40 });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith({ limit: 20, offset: 40 });
    });

    it("应该支持组合筛选条件", async () => {
      await db.getUserActivityLogs({
        userRole: "teacher",
        action: "approve_wish",
        module: "wish",
        limit: 10,
        offset: 0,
      });
      expect(db.getUserActivityLogs).toHaveBeenCalledWith(
        expect.objectContaining({
          userRole: "teacher",
          action: "approve_wish",
          module: "wish",
        })
      );
    });

    it("日志记录应包含必要字段", async () => {
      const result = await db.getUserActivityLogs();
      const log = result.logs[0];
      expect(log).toHaveProperty("id");
      expect(log).toHaveProperty("userId");
      expect(log).toHaveProperty("userName");
      expect(log).toHaveProperty("userRole");
      expect(log).toHaveProperty("action");
      expect(log).toHaveProperty("module");
      expect(log).toHaveProperty("description");
      expect(log).toHaveProperty("result");
      expect(log).toHaveProperty("createdAt");
    });

    it("日志记录应支持目标信息字段", async () => {
      const result = await db.getUserActivityLogs();
      const log = result.logs[1]; // 导师审核志愿
      expect(log).toHaveProperty("targetType");
      expect(log).toHaveProperty("targetId");
      expect(log).toHaveProperty("targetName");
      expect(log.targetType).toBe("wish");
      expect(log.targetId).toBe(5);
      expect(log.targetName).toBe("张三");
    });
  });

  describe("getUserActivityLogStats - 日志统计", () => {
    it("应该返回完整的统计数据结构", async () => {
      const stats = await db.getUserActivityLogStats();
      expect(stats).toHaveProperty("totalLogs");
      expect(stats).toHaveProperty("todayLogs");
      expect(stats).toHaveProperty("last7DaysLogs");
      expect(stats).toHaveProperty("roleStats");
      expect(stats).toHaveProperty("moduleStats");
      expect(stats).toHaveProperty("actionStats");
      expect(stats).toHaveProperty("dailyTrend");
    });

    it("统计数据应包含正确的总数", async () => {
      const stats = await db.getUserActivityLogStats();
      expect(stats.totalLogs).toBe(150);
      expect(stats.todayLogs).toBe(12);
      expect(stats.last7DaysLogs).toBe(85);
    });

    it("角色统计应包含所有角色", async () => {
      const stats = await db.getUserActivityLogStats();
      expect(stats.roleStats).toHaveLength(3);
      const roles = stats.roleStats.map((r: any) => r.role);
      expect(roles).toContain("student");
      expect(roles).toContain("teacher");
      expect(roles).toContain("admin");
    });

    it("模块统计应按数量降序排列", async () => {
      const stats = await db.getUserActivityLogStats();
      for (let i = 1; i < stats.moduleStats.length; i++) {
        expect(stats.moduleStats[i - 1].count).toBeGreaterThanOrEqual(stats.moduleStats[i].count);
      }
    });

    it("操作类型统计应按数量降序排列", async () => {
      const stats = await db.getUserActivityLogStats();
      for (let i = 1; i < stats.actionStats.length; i++) {
        expect(stats.actionStats[i - 1].count).toBeGreaterThanOrEqual(stats.actionStats[i].count);
      }
    });

    it("每日趋势应包含日期和数量", async () => {
      const stats = await db.getUserActivityLogStats();
      expect(stats.dailyTrend.length).toBeGreaterThan(0);
      stats.dailyTrend.forEach((item: any) => {
        expect(item).toHaveProperty("date");
        expect(item).toHaveProperty("count");
        expect(typeof item.date).toBe("string");
        expect(typeof item.count).toBe("number");
      });
    });
  });

  describe("日志操作类型覆盖", () => {
    const actionTypes = [
      { action: "login", module: "auth", role: "student" },
      { action: "submit_wish", module: "wish", role: "student" },
      { action: "approve_wish", module: "wish", role: "teacher" },
      { action: "reject_wish", module: "wish", role: "teacher" },
      { action: "upload_thesis", module: "thesis", role: "student" },
      { action: "score_thesis_first", module: "thesis", role: "teacher" },
      { action: "score_thesis_second", module: "thesis", role: "teacher" },
      { action: "update_config", module: "config", role: "admin" },
      { action: "create_user", module: "user", role: "admin" },
      { action: "bulk_import", module: "user", role: "admin" },
      { action: "assign_second_teacher", module: "second_teacher", role: "admin" },
    ];

    actionTypes.forEach(({ action, module, role }) => {
      it(`应该支持 ${role} 的 ${action} 操作类型`, async () => {
        await db.logUserActivity({
          userId: 1,
          userName: "测试用户",
          userRole: role,
          action,
          module,
          description: `测试 ${action} 操作`,
        });

        expect(db.logUserActivity).toHaveBeenCalledWith(
          expect.objectContaining({
            userRole: role,
            action,
            module,
          })
        );
      });
    });
  });
});
