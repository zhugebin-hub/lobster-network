import { initializeAdmin, initializeConfigs, getConfig, autoAssignOverdueWishes, checkTimePhase } from "./db";

// 自动逾期分配任务
async function runAutoAssignmentTask(): Promise<void> {
  try {
    const academicYear = await getConfig("currentAcademicYear") || "2024-2025";
    
    // 检查是否在导师确认时间段内
    const timePhase = await checkTimePhase();
    if (timePhase.phase !== "teacher_confirm") {
      return; // 不在导师确认时间段，不执行自动分配
    }
    
    // 获取逾期时限配置
    const overdueDaysStr = await getConfig("overdueDays") || "1";
    const overdueDays = parseFloat(overdueDaysStr);
    
    // 执行自动分配
    const result = await autoAssignOverdueWishes(academicYear, overdueDays);
    
    if (result.assigned > 0) {
      console.log(`[Auto-Assignment] Processed ${result.processed} wishes, assigned ${result.assigned}`);
    }
  } catch (error) {
    console.error("[Auto-Assignment] Error:", error);
  }
}

export async function initializeSystem(): Promise<void> {
  console.log("[Init] Starting system initialization...");
  await initializeAdmin();
  await initializeConfigs();
  
  // 启动自动逾期分配任务（每分钟检查一次）
  setInterval(runAutoAssignmentTask, 60 * 1000);
  console.log("[Auto-Assignment] Task started, checking every minute");
  
  console.log("[Init] System initialization complete.");
}
