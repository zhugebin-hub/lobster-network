export { COOKIE_NAME, ONE_YEAR_MS } from "@shared/const";
import { getBasePath } from "@/lib/basePath";

// 登录跳转到本地 /login 页面（支持子路径部署）
export const getLoginUrl = () => {
  return `${window.location.origin}${getBasePath()}/login`;
};
