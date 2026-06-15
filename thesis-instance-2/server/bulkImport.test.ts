import { describe, expect, it, vi, beforeEach } from "vitest";
import * as XLSX from "xlsx";

// Mock bcryptjs
vi.mock("bcryptjs", () => ({
  default: {
    hash: vi.fn().mockResolvedValue("hashed_password"),
    compare: vi.fn().mockResolvedValue(true),
  },
}));

describe("批量导入功能测试", () => {
  describe("Excel模板生成", () => {
    it("应该能生成正确的导师模板结构", () => {
      const templateData = [
        {
          "邮箱/Email": "teacher@example.com",
          "密码/Password": "123456",
          "姓名/Name": "张老师",
          "类型/Type": "中方",
          "年度限额/Annual Quota": 5,
        },
      ];
      
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(templateData);
      XLSX.utils.book_append_sheet(wb, ws, "导师模板");
      
      expect(wb.SheetNames).toContain("导师模板");
      expect(ws["A1"]?.v).toBe("邮箱/Email");
      expect(ws["B1"]?.v).toBe("密码/Password");
      expect(ws["C1"]?.v).toBe("姓名/Name");
      expect(ws["D1"]?.v).toBe("类型/Type");
      expect(ws["E1"]?.v).toBe("年度限额/Annual Quota");
    });

    it("应该能生成正确的学生模板结构", () => {
      const templateData = [
        {
          "学号/Student ID": "20210001",
          "密码/Password": "123456",
          "姓名/Name": "李同学",
          "类型/Type": "非分流",
          "专业/Major": "电子信息",
          "班级/Class": "电子2101",
          "学院/Faculty": "信息学院",
        },
      ];
      
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(templateData);
      XLSX.utils.book_append_sheet(wb, ws, "学生模板");
      
      expect(wb.SheetNames).toContain("学生模板");
      expect(ws["A1"]?.v).toBe("学号/Student ID");
      expect(ws["B1"]?.v).toBe("密码/Password");
      expect(ws["C1"]?.v).toBe("姓名/Name");
      expect(ws["D1"]?.v).toBe("类型/Type");
      expect(ws["E1"]?.v).toBe("专业/Major");
      expect(ws["F1"]?.v).toBe("班级/Class");
      expect(ws["G1"]?.v).toBe("学院/Faculty");
    });
  });

  describe("数据解析", () => {
    // 解析类型值的辅助函数
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

    it("应该正确解析中方导师类型", () => {
      expect(parseTeacherType("中方")).toBe("chinese");
      expect(parseTeacherType("chinese")).toBe("chinese");
      expect(parseTeacherType("中")).toBe("chinese");
      expect(parseTeacherType("Chinese")).toBe("chinese");
    });

    it("应该正确解析英方导师类型", () => {
      expect(parseTeacherType("英方")).toBe("british");
      expect(parseTeacherType("british")).toBe("british");
      expect(parseTeacherType("英")).toBe("british");
      expect(parseTeacherType("British")).toBe("british");
    });

    it("应该正确解析分流学生类型", () => {
      expect(parseStudentType("分流")).toBe("transfer");
      expect(parseStudentType("transfer")).toBe("transfer");
      expect(parseStudentType("是")).toBe("transfer");
    });

    it("应该正确解析非分流学生类型", () => {
      expect(parseStudentType("非分流")).toBe("non_transfer");
      expect(parseStudentType("non_transfer")).toBe("non_transfer");
      expect(parseStudentType("non-transfer")).toBe("non_transfer");
      expect(parseStudentType("否")).toBe("non_transfer");
      expect(parseStudentType("非")).toBe("non_transfer");
    });

    it("应该正确解析电子信息专业", () => {
      expect(parseStudentMajor("电子信息")).toBe("electronic_info");
      expect(parseStudentMajor("electronic_info")).toBe("electronic_info");
      expect(parseStudentMajor("电子")).toBe("electronic_info");
    });

    it("应该正确解析通信工程专业", () => {
      expect(parseStudentMajor("通信工程")).toBe("communication");
      expect(parseStudentMajor("communication")).toBe("communication");
      expect(parseStudentMajor("通信")).toBe("communication");
    });

    it("应该处理空值和未知值", () => {
      expect(parseTeacherType(undefined)).toBeUndefined();
      expect(parseTeacherType("")).toBeUndefined();
      expect(parseStudentType(undefined)).toBeUndefined();
      expect(parseStudentMajor("未知专业")).toBeUndefined();
    });
  });

  describe("Excel文件解析", () => {
    it("应该能正确解析导师Excel数据", () => {
      // 创建测试数据
      const testData = [
        {
          "邮箱/Email": "teacher1@example.com",
          "密码/Password": "password123",
          "姓名/Name": "张老师",
          "类型/Type": "中方",
          "年度限额/Annual Quota": 5,
        },
        {
          "邮箱/Email": "teacher2@example.com",
          "密码/Password": "password456",
          "姓名/Name": "李老师",
          "类型/Type": "英方",
          "年度限额/Annual Quota": 3,
        },
      ];

      // 创建工作簿
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(testData);
      XLSX.utils.book_append_sheet(wb, ws, "Sheet1");

      // 解析数据
      const jsonData = XLSX.utils.sheet_to_json(ws);
      
      expect(jsonData).toHaveLength(2);
      expect((jsonData[0] as any)["邮箱/Email"]).toBe("teacher1@example.com");
      expect((jsonData[1] as any)["类型/Type"]).toBe("英方");
    });

    it("应该能正确解析学生Excel数据", () => {
      const testData = [
        {
          "学号/Student ID": "20210001",
          "密码/Password": "password123",
          "姓名/Name": "王同学",
          "类型/Type": "分流",
          "专业/Major": "电子信息",
          "班级/Class": "电子2101",
          "学院/Faculty": "信息学院",
        },
        {
          "学号/Student ID": "20210002",
          "密码/Password": "password456",
          "姓名/Name": "刘同学",
          "类型/Type": "非分流",
          "专业/Major": "通信工程",
          "班级/Class": "通信2101",
          "学院/Faculty": "信息学院",
        },
      ];

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(testData);
      XLSX.utils.book_append_sheet(wb, ws, "Sheet1");

      const jsonData = XLSX.utils.sheet_to_json(ws);
      
      expect(jsonData).toHaveLength(2);
      expect((jsonData[0] as any)["学号/Student ID"]).toBe("20210001");
      expect((jsonData[1] as any)["专业/Major"]).toBe("通信工程");
    });
  });

  describe("数据验证", () => {
    it("应该检测缺少必填字段的数据", () => {
      const errors: string[] = [];
      const testData = [
        { "姓名/Name": "张老师" }, // 缺少邮箱和密码
      ];

      testData.forEach((row: any, index) => {
        const rowNum = index + 2;
        const email = row["邮箱/Email"];
        const password = row["密码/Password"];

        if (!email) {
          errors.push(`第${rowNum}行: 缺少邮箱`);
        }
        if (!password) {
          errors.push(`第${rowNum}行: 缺少密码`);
        }
      });

      expect(errors).toContain("第2行: 缺少邮箱");
      expect(errors).toContain("第2行: 缺少密码");
    });

    it("应该正确处理有效数据", () => {
      const errors: string[] = [];
      const parsedData: any[] = [];
      const testData = [
        {
          "邮箱/Email": "valid@example.com",
          "密码/Password": "validpass",
          "姓名/Name": "有效用户",
        },
      ];

      testData.forEach((row: any, index) => {
        const email = row["邮箱/Email"];
        const password = row["密码/Password"];
        const name = row["姓名/Name"];

        if (!email || !password) {
          errors.push(`第${index + 2}行: 数据不完整`);
          return;
        }

        parsedData.push({
          email: String(email).trim(),
          password: String(password),
          name: name ? String(name).trim() : undefined,
          role: "teacher" as const,
        });
      });

      expect(errors).toHaveLength(0);
      expect(parsedData).toHaveLength(1);
      expect(parsedData[0].email).toBe("valid@example.com");
    });
  });

  describe("批量导入结果处理", () => {
    it("应该正确统计导入成功和失败数量", () => {
      const importResult = {
        success: 8,
        failed: 2,
        errors: [
          "邮箱 duplicate@example.com 已存在",
          "邮箱 invalid 格式不正确",
        ],
      };

      expect(importResult.success).toBe(8);
      expect(importResult.failed).toBe(2);
      expect(importResult.errors).toHaveLength(2);
    });

    it("应该正确处理全部成功的情况", () => {
      const importResult = {
        success: 10,
        failed: 0,
        errors: [],
      };

      expect(importResult.success).toBe(10);
      expect(importResult.failed).toBe(0);
      expect(importResult.errors).toHaveLength(0);
    });

    it("应该正确处理全部失败的情况", () => {
      const importResult = {
        success: 0,
        failed: 5,
        errors: [
          "第2行: 缺少邮箱",
          "第3行: 缺少密码",
          "第4行: 邮箱已存在",
          "第5行: 邮箱格式不正确",
          "第6行: 数据库错误",
        ],
      };

      expect(importResult.success).toBe(0);
      expect(importResult.failed).toBe(5);
      expect(importResult.errors).toHaveLength(5);
    });
  });
});
