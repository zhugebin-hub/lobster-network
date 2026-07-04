/**
 * 环境变量配置文件
 * 支持从 .env 文件或系统环境变量读取配置
 * 迁移到第三方服务器时，只需修改 .env 文件即可
 */

// 数据库配置
export const DATABASE_CONFIG = {
  url: process.env.DATABASE_URL ?? "",
  // 可选：单独配置数据库连接参数
  host: process.env.DB_HOST ?? "localhost",
  port: parseInt(process.env.DB_PORT ?? "3306"),
  user: process.env.DB_USER ?? "root",
  password: process.env.DB_PASSWORD ?? "",
  database: process.env.DB_NAME ?? "thesis_system",
  // SSL配置（阿里云RDS等需要）
  ssl: process.env.DB_SSL === "true",
};

// JWT认证配置
export const AUTH_CONFIG = {
  jwtSecret: process.env.JWT_SECRET ?? "your-jwt-secret-key-change-in-production",
  jwtExpiresIn: process.env.JWT_EXPIRES_IN ?? "7d",
  cookieName: process.env.COOKIE_NAME ?? "thesis_session",
  cookieMaxAge: parseInt(process.env.COOKIE_MAX_AGE ?? String(7 * 24 * 60 * 60 * 1000)), // 7天
};

// 存储配置（支持阿里云OSS或AWS S3）
export const STORAGE_CONFIG = {
  provider: process.env.STORAGE_PROVIDER ?? "s3", // "s3" | "oss" | "local"
  
  // S3/OSS通用配置
  endpoint: process.env.STORAGE_ENDPOINT ?? "",
  region: process.env.STORAGE_REGION ?? "cn-hangzhou",
  bucket: process.env.STORAGE_BUCKET ?? "",
  accessKeyId: process.env.STORAGE_ACCESS_KEY_ID ?? "",
  accessKeySecret: process.env.STORAGE_ACCESS_KEY_SECRET ?? "",
  
  // 公开访问URL前缀
  publicUrlPrefix: process.env.STORAGE_PUBLIC_URL ?? "",
  
  // 本地存储路径（当provider为local时使用）
  localPath: process.env.STORAGE_LOCAL_PATH ?? "./uploads",
};

// 服务器配置
export const SERVER_CONFIG = {
  port: parseInt(process.env.PORT ?? "3000"),
  host: process.env.HOST ?? "0.0.0.0",
  nodeEnv: process.env.NODE_ENV ?? "development",
  isProduction: process.env.NODE_ENV === "production",
  
  // CORS配置
  corsOrigins: process.env.CORS_ORIGINS?.split(",") ?? ["http://localhost:3000"],
  
  // 文件上传限制
  maxFileSize: parseInt(process.env.MAX_FILE_SIZE ?? String(50 * 1024 * 1024)), // 50MB
};

// 应用配置
export const APP_CONFIG = {
  appName: process.env.VITE_APP_TITLE ?? "人工智能学院毕业设计管理系统",
  appLogo: process.env.VITE_APP_LOGO ?? "",
  defaultLanguage: process.env.DEFAULT_LANGUAGE ?? "zh",
  
  // 初始管理员账号
  adminEmail: process.env.ADMIN_EMAIL ?? "root",
  adminPassword: process.env.ADMIN_PASSWORD ?? "xd-zjgsu",
};

// LLM配置（可选，用于AI辅助功能）
export const LLM_CONFIG = {
  enabled: process.env.LLM_ENABLED === "true",
  apiUrl: process.env.LLM_API_URL ?? "",
  apiKey: process.env.LLM_API_KEY ?? "",
  model: process.env.LLM_MODEL ?? "gpt-3.5-turbo",
};

// 导出统一的ENV对象（兼容现有代码）
export const ENV = {
  appId: process.env.VITE_APP_ID ?? "",
  cookieSecret: AUTH_CONFIG.jwtSecret,
  databaseUrl: DATABASE_CONFIG.url,
  oAuthServerUrl: process.env.OAUTH_SERVER_URL ?? "",
  ownerOpenId: process.env.OWNER_OPEN_ID ?? "",
  isProduction: SERVER_CONFIG.isProduction,
  forgeApiUrl: process.env.BUILT_IN_FORGE_API_URL ?? "",
  forgeApiKey: process.env.BUILT_IN_FORGE_API_KEY ?? "",
};

// 验证必要的环境变量
export function validateEnv(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (!DATABASE_CONFIG.url && !DATABASE_CONFIG.host) {
    errors.push("DATABASE_URL or DB_HOST is required");
  }
  
  if (SERVER_CONFIG.isProduction) {
    if (AUTH_CONFIG.jwtSecret === "your-jwt-secret-key-change-in-production") {
      errors.push("JWT_SECRET must be set in production");
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}
