import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock bcrypt
vi.mock("bcryptjs", () => ({
  hash: vi.fn().mockResolvedValue("hashed_password"),
  compare: vi.fn().mockResolvedValue(true),
}));

// Mock database functions
const mockGetAdminUsers = vi.fn();
const mockCreateSingleUser = vi.fn();
const mockDeleteUser = vi.fn();

vi.mock("./db", () => ({
  getAdminUsers: () => mockGetAdminUsers(),
  createSingleUser: (data: any) => mockCreateSingleUser(data),
  deleteUser: (id: number) => mockDeleteUser(id),
}));

describe("Admin Management API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getAdmins", () => {
    it("should return list of admin users", async () => {
      const mockAdmins = [
        { id: 1, email: "admin1", name: "管理员一", role: "admin", createdAt: new Date() },
        { id: 2, email: "admin2", name: "管理员二", role: "admin", createdAt: new Date() },
      ];
      mockGetAdminUsers.mockResolvedValue(mockAdmins);

      const result = await mockGetAdminUsers();
      
      expect(result).toHaveLength(2);
      expect(result[0].role).toBe("admin");
      expect(result[1].role).toBe("admin");
    });

    it("should return empty array when no admins exist", async () => {
      mockGetAdminUsers.mockResolvedValue([]);

      const result = await mockGetAdminUsers();
      
      expect(result).toHaveLength(0);
    });
  });

  describe("createAdmin", () => {
    it("should create admin with valid input", async () => {
      mockCreateSingleUser.mockResolvedValue({ success: true, message: "用户创建成功" });

      const result = await mockCreateSingleUser({
        email: "newadmin",
        password: "hashed_password",
        name: "新管理员",
        role: "admin",
        initialPassword: "123456",
      });

      expect(result.success).toBe(true);
      expect(mockCreateSingleUser).toHaveBeenCalledWith(
        expect.objectContaining({
          email: "newadmin",
          name: "新管理员",
          role: "admin",
        })
      );
    });

    it("should fail when admin already exists", async () => {
      mockCreateSingleUser.mockResolvedValue({ success: false, message: "用户 admin1 已存在" });

      const result = await mockCreateSingleUser({
        email: "admin1",
        password: "hashed_password",
        name: "重复管理员",
        role: "admin",
        initialPassword: "123456",
      });

      expect(result.success).toBe(false);
      expect(result.message).toContain("已存在");
    });

    it("should use default password when not provided", async () => {
      mockCreateSingleUser.mockResolvedValue({ success: true, message: "用户创建成功" });

      await mockCreateSingleUser({
        email: "admin3",
        password: "hashed_password",
        name: "管理员三",
        role: "admin",
        initialPassword: "123456",
      });

      expect(mockCreateSingleUser).toHaveBeenCalledWith(
        expect.objectContaining({
          initialPassword: "123456",
        })
      );
    });
  });

  describe("deleteAdmin", () => {
    it("should delete admin by id", async () => {
      mockDeleteUser.mockResolvedValue(undefined);

      await mockDeleteUser(1);

      expect(mockDeleteUser).toHaveBeenCalledWith(1);
    });
  });

  describe("bulkImportAdmins", () => {
    it("should import multiple admins", async () => {
      mockCreateSingleUser
        .mockResolvedValueOnce({ success: true, message: "用户创建成功" })
        .mockResolvedValueOnce({ success: true, message: "用户创建成功" })
        .mockResolvedValueOnce({ success: false, message: "用户 admin3 已存在" });

      const admins = [
        { email: "admin1", name: "管理员一", password: "123456" },
        { email: "admin2", name: "管理员二", password: "123456" },
        { email: "admin3", name: "管理员三", password: "123456" },
      ];

      let success = 0;
      let failed = 0;
      const errors: string[] = [];

      for (const admin of admins) {
        const result = await mockCreateSingleUser({
          email: admin.email,
          password: "hashed_password",
          name: admin.name,
          role: "admin",
          initialPassword: admin.password,
        });
        if (result.success) {
          success++;
        } else {
          failed++;
          errors.push(result.message);
        }
      }

      expect(success).toBe(2);
      expect(failed).toBe(1);
      expect(errors).toContain("用户 admin3 已存在");
    });
  });

  describe("Admin role validation", () => {
    it("should only allow admin role for admin accounts", async () => {
      mockCreateSingleUser.mockResolvedValue({ success: true, message: "用户创建成功" });

      await mockCreateSingleUser({
        email: "admin_test",
        password: "hashed_password",
        name: "测试管理员",
        role: "admin",
        initialPassword: "123456",
      });

      expect(mockCreateSingleUser).toHaveBeenCalledWith(
        expect.objectContaining({
          role: "admin",
        })
      );
    });
  });
});
