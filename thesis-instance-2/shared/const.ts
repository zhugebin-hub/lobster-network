// Cookie名称支持环境变量配置，解决同域双实例部署时的Cookie冲突
// 在浏览器端 process.env 不可用，所以使用 typeof 安全检查
export const COOKIE_NAME = (typeof process !== 'undefined' && process.env?.COOKIE_NAME) || "app_session_id";
export const ONE_YEAR_MS = 1000 * 60 * 60 * 24 * 365;
export const AXIOS_TIMEOUT_MS = 30_000;
export const UNAUTHED_ERR_MSG = 'Please login (10001)';
export const NOT_ADMIN_ERR_MSG = 'You do not have required permission (10002)';
