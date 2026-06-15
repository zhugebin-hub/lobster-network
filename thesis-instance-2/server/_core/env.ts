export const ENV = {
  appId: process.env.VITE_APP_ID ?? "thesis-topic-system",
  cookieSecret: process.env.JWT_SECRET ?? "thesis-secret-key",
  databaseUrl: process.env.DATABASE_URL ?? "",
  oAuthServerUrl: process.env.OAUTH_SERVER_URL ?? "",
  ownerOpenId: process.env.OWNER_OPEN_ID ?? "",
  isProduction: process.env.NODE_ENV === "production",
  forgeApiUrl: process.env.LLM_API_URL || process.env.BUILT_IN_FORGE_API_URL || "",
  forgeApiKey: process.env.LLM_API_KEY || process.env.BUILT_IN_FORGE_API_KEY || "",
  localStorageDir: process.env.LOCAL_STORAGE_DIR ?? "",
};
