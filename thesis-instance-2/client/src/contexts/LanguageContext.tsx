import { createContext, useContext, useState, ReactNode } from "react";

type Language = "zh" | "en";

const translations = {
  zh: {
    appName: "人工智能学院毕业设计管理系统",
    login: "登录",
    register: "注册",
    logout: "退出登录",
    email: "邮箱/用户名",
    password: "密码",
    confirmPassword: "确认密码",
    name: "姓名",
    role: "身份",
    submit: "提交",
    cancel: "取消",
    save: "保存",
    delete: "删除",
    edit: "编辑",
    back: "返回",
    home: "首页",
    dashboard: "控制台",
    topics: "课题管理",
    wishes: "志愿填报",
    matches: "匹配结果",
    users: "用户管理",
    settings: "系统设置",
    roles: {
      admin: "管理员",
      teacher: "导师",
      student: "学生",
    },
    teacherTypes: {
      chinese: "中方导师",
      british: "英方导师",
    },
    studentTypes: {
      transfer: "分流学生",
      non_transfer: "非分流学生",
    },
    majors: {
      electronic_info: "电子信息工程",
      communication: "通信工程",
      both: "不限专业",
    },
    topicStatus: {
      draft: "草稿",
      published: "已发布",
      used: "已使用",
    },
    phases: {
      topic_collection: "课题征集阶段",
      wish_submission: "志愿填报阶段",
      matching: "匹配进行中",
      adjustment: "调剂阶段",
      completed: "已完成",
    },
  },
  en: {
    appName: "UG Individual Project System (Sussex AI Institute ZJSU)",
    login: "Login",
    register: "Register",
    logout: "Logout",
    email: "Email/Username",
    password: "Password",
    confirmPassword: "Confirm Password",
    name: "Name",
    role: "Role",
    submit: "Submit",
    cancel: "Cancel",
    save: "Save",
    delete: "Delete",
    edit: "Edit",
    back: "Back",
    home: "Home",
    dashboard: "Dashboard",
    topics: "Topics",
    wishes: "Wishes",
    matches: "Matches",
    users: "Users",
    settings: "Settings",
    roles: {
      admin: "Administrator",
      teacher: "Supervisor",
      student: "Student",
    },
    teacherTypes: {
      chinese: "ZJSU Supervisor",
      british: "Sussex Supervisor",
    },
    studentTypes: {
      transfer: "Single-Degree",
      non_transfer: "Dual-Degree",
    },
    majors: {
      electronic_info: "Robotics and Electrical Engineering",
      communication: "Communications Engineering",
      both: "All Majors",
    },
    topicStatus: {
      draft: "Draft",
      published: "Published",
      used: "Used",
    },
    phases: {
      topic_collection: "Topic Collection",
      wish_submission: "Wish Submission",
      matching: "Matching in Progress",
      adjustment: "Adjustment Phase",
      completed: "Completed",
    },
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: typeof translations.zh;
}

const LanguageContext = createContext<LanguageContextType | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>("zh");

  const value = {
    language,
    setLanguage,
    t: translations[language],
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
