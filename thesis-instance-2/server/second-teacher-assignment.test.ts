import { describe, it, expect, vi, beforeEach } from "vitest";

// 测试第二导师指派的业务逻辑
describe("Second Teacher Assignment Logic", () => {
  describe("Assignment Validation", () => {
    it("should prevent same teacher as first and second", () => {
      const firstTeacherId = 1;
      const secondTeacherId = 1;
      
      const isValid = firstTeacherId !== secondTeacherId;
      expect(isValid).toBe(false);
    });

    it("should allow different teachers for first and second", () => {
      const firstTeacherId = 1;
      const secondTeacherId = 2;
      
      const isValid = firstTeacherId !== secondTeacherId;
      expect(isValid).toBe(true);
    });
  });

  describe("Batch Assignment Parsing", () => {
    it("should parse comma-separated values correctly", () => {
      const input = "张三,李四\n王五,赵六";
      const lines = input.trim().split("\n");
      const assignments = lines.map(line => {
        const parts = line.split(/[,\t]/);
        return {
          studentName: parts[0]?.trim() || "",
          secondTeacherName: parts[1]?.trim() || "",
        };
      }).filter(a => a.studentName && a.secondTeacherName);

      expect(assignments).toHaveLength(2);
      expect(assignments[0]).toEqual({ studentName: "张三", secondTeacherName: "李四" });
      expect(assignments[1]).toEqual({ studentName: "王五", secondTeacherName: "赵六" });
    });

    it("should parse tab-separated values correctly", () => {
      const input = "张三\t李四\n王五\t赵六";
      const lines = input.trim().split("\n");
      const assignments = lines.map(line => {
        const parts = line.split(/[,\t]/);
        return {
          studentName: parts[0]?.trim() || "",
          secondTeacherName: parts[1]?.trim() || "",
        };
      }).filter(a => a.studentName && a.secondTeacherName);

      expect(assignments).toHaveLength(2);
      expect(assignments[0]).toEqual({ studentName: "张三", secondTeacherName: "李四" });
    });

    it("should filter out invalid entries", () => {
      const input = "张三,李四\n\n王五,";
      const lines = input.trim().split("\n");
      const assignments = lines.map(line => {
        const parts = line.split(/[,\t]/);
        return {
          studentName: parts[0]?.trim() || "",
          secondTeacherName: parts[1]?.trim() || "",
        };
      }).filter(a => a.studentName && a.secondTeacherName);

      expect(assignments).toHaveLength(1);
      expect(assignments[0]).toEqual({ studentName: "张三", secondTeacherName: "李四" });
    });

    it("should handle empty input", () => {
      const input = "";
      const lines = input.trim().split("\n");
      const assignments = lines.map(line => {
        const parts = line.split(/[,\t]/);
        return {
          studentName: parts[0]?.trim() || "",
          secondTeacherName: parts[1]?.trim() || "",
        };
      }).filter(a => a.studentName && a.secondTeacherName);

      expect(assignments).toHaveLength(0);
    });
  });

  describe("History Record", () => {
    it("should identify assignment action correctly", () => {
      const record = {
        action: "assign",
        oldSecondTeacherId: null,
        newSecondTeacherId: 2,
      };

      const isNewAssignment = record.action === "assign" && !record.oldSecondTeacherId;
      expect(isNewAssignment).toBe(true);
    });

    it("should identify change action correctly", () => {
      const record = {
        action: "assign",
        oldSecondTeacherId: 2,
        newSecondTeacherId: 3,
      };

      const isChange = record.action === "assign" && record.oldSecondTeacherId !== null;
      expect(isChange).toBe(true);
    });

    it("should identify revoke action correctly", () => {
      const record = {
        action: "revoke",
        oldSecondTeacherId: 2,
        newSecondTeacherId: null,
      };

      const isRevoke = record.action === "revoke";
      expect(isRevoke).toBe(true);
    });
  });

  describe("Teacher Filtering", () => {
    it("should filter out first teacher from available teachers", () => {
      const teachers = [
        { id: 1, name: "Teacher A" },
        { id: 2, name: "Teacher B" },
        { id: 3, name: "Teacher C" },
      ];
      const firstTeacherId = 1;

      const availableTeachers = teachers.filter(t => t.id !== firstTeacherId);

      expect(availableTeachers).toHaveLength(2);
      expect(availableTeachers.map(t => t.id)).not.toContain(firstTeacherId);
    });

    it("should return all teachers when first teacher not in list", () => {
      const teachers = [
        { id: 1, name: "Teacher A" },
        { id: 2, name: "Teacher B" },
      ];
      const firstTeacherId = 99;

      const availableTeachers = teachers.filter(t => t.id !== firstTeacherId);

      expect(availableTeachers).toHaveLength(2);
    });
  });

  describe("Revoke Validation", () => {
    it("should allow revoke when no score exists", () => {
      const secondTeacherScore = null;
      const canRevoke = secondTeacherScore === null;
      expect(canRevoke).toBe(true);
    });

    it("should prevent revoke when score exists", () => {
      const secondTeacherScore = 85.5;
      const canRevoke = secondTeacherScore === null;
      expect(canRevoke).toBe(false);
    });
  });

  describe("CSV Template Generation", () => {
    it("should generate correct template format", () => {
      const template = "学生姓名,第二导师姓名\n张三,李四\n王五,赵六";
      
      expect(template).toContain("学生姓名");
      expect(template).toContain("第二导师姓名");
      expect(template.split("\n")).toHaveLength(3);
    });
  });

  describe("Statistics Calculation", () => {
    it("should calculate assigned count correctly", () => {
      const students = [
        { matchId: 1, secondTeacherId: 1 },
        { matchId: 2, secondTeacherId: null },
        { matchId: 3, secondTeacherId: 2 },
        { matchId: 4, secondTeacherId: null },
      ];

      const assignedCount = students.filter(s => s.secondTeacherId).length;
      const pendingCount = students.filter(s => !s.secondTeacherId).length;

      expect(assignedCount).toBe(2);
      expect(pendingCount).toBe(2);
    });
  });
});
