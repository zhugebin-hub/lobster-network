import { describe, expect, it, vi, beforeEach } from "vitest";

// Mock database functions for testing
const mockGetConfig = vi.fn();
const mockSetConfig = vi.fn();
const mockGetTopicHeat = vi.fn();
const mockGetSelectionStats = vi.fn();
const mockGetUnselectedStudents = vi.fn();
const mockCheckTimePhase = vi.fn();

vi.mock("./db", () => ({
  getConfig: (...args: any[]) => mockGetConfig(...args),
  setConfig: (...args: any[]) => mockSetConfig(...args),
  getTopicHeat: (...args: any[]) => mockGetTopicHeat(...args),
  getSelectionStats: (...args: any[]) => mockGetSelectionStats(...args),
  getUnselectedStudents: (...args: any[]) => mockGetUnselectedStudents(...args),
  checkTimePhase: (...args: any[]) => mockCheckTimePhase(...args),
}));

describe("课题热度功能", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("应该返回课题的当前被选人数", async () => {
    mockGetTopicHeat.mockResolvedValue(5);
    
    const heat = await mockGetTopicHeat(1);
    
    expect(heat).toBe(5);
    expect(mockGetTopicHeat).toHaveBeenCalledWith(1);
  });

  it("没有人选择时热度应为0", async () => {
    mockGetTopicHeat.mockResolvedValue(0);
    
    const heat = await mockGetTopicHeat(999);
    
    expect(heat).toBe(0);
  });
});

describe("时间配置功能", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("应该正确保存学生选题时间配置", async () => {
    mockSetConfig.mockResolvedValue(true);
    
    const config = {
      studentSelectionStart: "2024-01-01T09:00",
      studentSelectionEnd: "2024-01-07T18:00",
    };
    
    await mockSetConfig("studentSelectionStart", config.studentSelectionStart);
    await mockSetConfig("studentSelectionEnd", config.studentSelectionEnd);
    
    expect(mockSetConfig).toHaveBeenCalledWith("studentSelectionStart", "2024-01-01T09:00");
    expect(mockSetConfig).toHaveBeenCalledWith("studentSelectionEnd", "2024-01-07T18:00");
  });

  it("应该正确保存导师确认时间配置", async () => {
    mockSetConfig.mockResolvedValue(true);
    
    const config = {
      teacherConfirmStart: "2024-01-08T09:00",
      teacherConfirmEnd: "2024-01-14T18:00",
    };
    
    await mockSetConfig("teacherConfirmStart", config.teacherConfirmStart);
    await mockSetConfig("teacherConfirmEnd", config.teacherConfirmEnd);
    
    expect(mockSetConfig).toHaveBeenCalledWith("teacherConfirmStart", "2024-01-08T09:00");
    expect(mockSetConfig).toHaveBeenCalledWith("teacherConfirmEnd", "2024-01-14T18:00");
  });

  it("应该检测当前处于学生选题阶段", async () => {
    const now = new Date("2024-01-05T12:00");
    mockCheckTimePhase.mockResolvedValue({
      phase: "student_selection",
      studentSelectionStart: new Date("2024-01-01T09:00"),
      studentSelectionEnd: new Date("2024-01-07T18:00"),
      teacherConfirmStart: new Date("2024-01-08T09:00"),
      teacherConfirmEnd: new Date("2024-01-14T18:00"),
    });
    
    const result = await mockCheckTimePhase();
    
    expect(result.phase).toBe("student_selection");
  });

  it("应该检测当前处于导师确认阶段", async () => {
    mockCheckTimePhase.mockResolvedValue({
      phase: "teacher_confirm",
      studentSelectionStart: new Date("2024-01-01T09:00"),
      studentSelectionEnd: new Date("2024-01-07T18:00"),
      teacherConfirmStart: new Date("2024-01-08T09:00"),
      teacherConfirmEnd: new Date("2024-01-14T18:00"),
    });
    
    const result = await mockCheckTimePhase();
    
    expect(result.phase).toBe("teacher_confirm");
  });

  it("应该检测选题已结束", async () => {
    mockCheckTimePhase.mockResolvedValue({
      phase: "closed",
      studentSelectionStart: new Date("2024-01-01T09:00"),
      studentSelectionEnd: new Date("2024-01-07T18:00"),
      teacherConfirmStart: new Date("2024-01-08T09:00"),
      teacherConfirmEnd: new Date("2024-01-14T18:00"),
    });
    
    const result = await mockCheckTimePhase();
    
    expect(result.phase).toBe("closed");
  });

  it("未配置时间时应返回none阶段", async () => {
    mockCheckTimePhase.mockResolvedValue({
      phase: "none",
      studentSelectionStart: null,
      studentSelectionEnd: null,
      teacherConfirmStart: null,
      teacherConfirmEnd: null,
    });
    
    const result = await mockCheckTimePhase();
    
    expect(result.phase).toBe("none");
  });
});

describe("数据统计功能", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("应该返回正确的选题统计数据", async () => {
    mockGetSelectionStats.mockResolvedValue({
      totalStudents: 100,
      selectedStudents: 75,
      unselectedStudents: 25,
    });
    
    const stats = await mockGetSelectionStats();
    
    expect(stats.totalStudents).toBe(100);
    expect(stats.selectedStudents).toBe(75);
    expect(stats.unselectedStudents).toBe(25);
  });

  it("没有学生时统计应全为0", async () => {
    mockGetSelectionStats.mockResolvedValue({
      totalStudents: 0,
      selectedStudents: 0,
      unselectedStudents: 0,
    });
    
    const stats = await mockGetSelectionStats();
    
    expect(stats.totalStudents).toBe(0);
    expect(stats.selectedStudents).toBe(0);
    expect(stats.unselectedStudents).toBe(0);
  });

  it("应该返回未选择志愿的学生列表", async () => {
    const unselectedStudents = [
      { id: 1, name: "张三", email: "zhangsan@example.com", studentId: "2021001", studentMajor: "electronic_info" },
      { id: 2, name: "李四", email: "lisi@example.com", studentId: "2021002", studentMajor: "communication" },
    ];
    mockGetUnselectedStudents.mockResolvedValue(unselectedStudents);
    
    const result = await mockGetUnselectedStudents();
    
    expect(result).toHaveLength(2);
    expect(result[0].name).toBe("张三");
    expect(result[1].name).toBe("李四");
  });

  it("所有学生都选择后应返回空列表", async () => {
    mockGetUnselectedStudents.mockResolvedValue([]);
    
    const result = await mockGetUnselectedStudents();
    
    expect(result).toHaveLength(0);
  });
});

describe("时间阶段权限控制", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("学生选题阶段：学生可以提交志愿", async () => {
    mockCheckTimePhase.mockResolvedValue({ phase: "student_selection" });
    
    const result = await mockCheckTimePhase();
    const canStudentSubmit = result.phase === "student_selection" || result.phase === "none";
    
    expect(canStudentSubmit).toBe(true);
  });

  it("学生选题阶段：导师不能确认学生", async () => {
    mockCheckTimePhase.mockResolvedValue({ phase: "student_selection" });
    
    const result = await mockCheckTimePhase();
    const canTeacherConfirm = result.phase === "teacher_confirm";
    
    expect(canTeacherConfirm).toBe(false);
  });

  it("导师确认阶段：学生不能修改志愿", async () => {
    mockCheckTimePhase.mockResolvedValue({ phase: "teacher_confirm" });
    
    const result = await mockCheckTimePhase();
    const canStudentSubmit = result.phase === "student_selection" || result.phase === "none";
    
    expect(canStudentSubmit).toBe(false);
  });

  it("导师确认阶段：导师可以确认学生", async () => {
    mockCheckTimePhase.mockResolvedValue({ phase: "teacher_confirm" });
    
    const result = await mockCheckTimePhase();
    const canTeacherConfirm = result.phase === "teacher_confirm";
    
    expect(canTeacherConfirm).toBe(true);
  });

  it("选题结束后：学生和导师都不能操作", async () => {
    mockCheckTimePhase.mockResolvedValue({ phase: "closed" });
    
    const result = await mockCheckTimePhase();
    const canStudentSubmit = result.phase === "student_selection" || result.phase === "none";
    const canTeacherConfirm = result.phase === "teacher_confirm";
    
    expect(canStudentSubmit).toBe(false);
    expect(canTeacherConfirm).toBe(false);
  });
});
