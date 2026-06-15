/**
 * 国家重点研发计划项目申报书 - 官方模板工作流引擎
 * 严格按照官方模板结构定义17个填写项
 */

export interface SectionDef {
  key: string;
  title: string;
  part: string;
  wordLimit: number;
  description: string;
  dependencies: string[];
  order: number;
}

export type SectionStatus = "pending" | "generating" | "draft_ready" | "confirmed" | "revising";

/** 官方模板17个填写项定义 */
export const OFFICIAL_SECTIONS: SectionDef[] = [
  {
    key: "project_intro",
    title: "申报项目简介",
    part: "前置部分",
    wordLimit: 1500,
    description: "项目目标、主要研究内容、预期成果。限1500字以内。",
    dependencies: [],
    order: 1,
  },
  {
    key: "current_status",
    title: "国内外现状及趋势分析",
    part: "第一部分",
    wordLimit: 2000,
    description: "包括国内外总体研究情况和水平、最新进展和发展前景。分别列出国内、外各代表性的5家机构及典型成果。",
    dependencies: ["project_intro"],
    order: 2,
  },
  {
    key: "guide_relevance",
    title: "与指南方向的关联关系",
    part: "第二部分",
    wordLimit: 1500,
    description: "项目与所属指南方向的匹配性，对指南方向目标的支撑作用。限1500字以内。",
    dependencies: ["project_intro"],
    order: 3,
  },
  {
    key: "objectives_indicators",
    title: "项目目标及考核指标",
    part: "第二部分",
    wordLimit: 2000,
    description: "项目目标、预期成果、考核指标、考核方式/方法。限2000字以内。",
    dependencies: ["guide_relevance"],
    order: 4,
  },
  {
    key: "expected_outcomes",
    title: "预期成果呈现形式及描述",
    part: "第二部分",
    wordLimit: 1000,
    description: "限1000字以内。",
    dependencies: ["objectives_indicators"],
    order: 5,
  },
  {
    key: "research_content",
    title: "主要研究内容",
    part: "第二部分",
    wordLimit: 3000,
    description: "拟解决的关键科学问题、关键技术问题及主要研究内容。限3000字以内。",
    dependencies: ["objectives_indicators"],
    order: 6,
  },
  {
    key: "research_methods",
    title: "拟采取的研究方法",
    part: "第二部分",
    wordLimit: 2000,
    description: "拟采用的方法、原理、机理、算法、模型等。限2000字以内。",
    dependencies: ["research_content"],
    order: 7,
  },
  {
    key: "feasibility_analysis",
    title: "可行性、先进性分析",
    part: "第二部分",
    wordLimit: 2000,
    description: "研究方法（技术路线）的可行性、先进性分析。限2000字以内。",
    dependencies: ["research_methods"],
    order: 8,
  },
  {
    key: "task_decomposition",
    title: "课题分解情况",
    part: "第二部分",
    wordLimit: 2000,
    description: "对项目目标进行任务分解，说明各课题的具体作用和逻辑关系。限2000字以内。",
    dependencies: ["research_content"],
    order: 9,
  },
  {
    key: "subtask_details",
    title: "各课题内容",
    part: "第二部分",
    wordLimit: 3000,
    description: "逐项说明各课题的研究目标、主要研究内容、拟解决的问题、考核指标等。每课题限3000字。",
    dependencies: ["task_decomposition"],
    order: 10,
  },
  {
    key: "innovation_points",
    title: "主要创新点",
    part: "第二部分",
    wordLimit: 500,
    description: "简述项目的主要创新点。每项创新点限500字以内。",
    dependencies: ["research_content"],
    order: 11,
  },
  {
    key: "social_benefits",
    title: "预期经济社会效益",
    part: "第二部分",
    wordLimit: 1500,
    description: "科学、技术、产业预期指标及科学价值、社会、经济、生态效益。限1500字以内。",
    dependencies: ["objectives_indicators"],
    order: 12,
  },
  {
    key: "prior_achievements",
    title: "前期任务承担及研究成果",
    part: "第三部分",
    wordLimit: 1000,
    description: "牵头单位在该研究方向的前期任务承担及综合绩效评价情况、相关研究成果。限1000字以内。",
    dependencies: ["project_intro"],
    order: 13,
  },
  {
    key: "pi_qualifications",
    title: "负责人科研水平及主要成果",
    part: "第三部分",
    wordLimit: 2000,
    description: "项目及课题负责人的科研水平及主要成果。限2000字以内。",
    dependencies: ["prior_achievements"],
    order: 14,
  },
  {
    key: "research_conditions",
    title: "科研条件支撑状况",
    part: "第三部分",
    wordLimit: 1000,
    description: "国家重点实验室、国家工程中心、大型仪器设备等情况。限1000字以内。",
    dependencies: ["prior_achievements"],
    order: 15,
  },
  {
    key: "schedule",
    title: "进度安排",
    part: "第四部分",
    wordLimit: 1500,
    description: "各阶段的主要任务和时间节点。",
    dependencies: ["research_content", "task_decomposition"],
    order: 16,
  },
  {
    key: "organization_risk",
    title: "组织实施与风险分析",
    part: "第五部分",
    wordLimit: 2000,
    description: "组织管理方式、保障措施及风险分析。",
    dependencies: ["schedule"],
    order: 17,
  },
];

/** 获取章节定义 */
export function getSectionDef(key: string): SectionDef | undefined {
  return OFFICIAL_SECTIONS.find(s => s.key === key);
}

/** 检查前置依赖是否满足 */
export function checkDependencies(
  sectionKey: string,
  sectionStatuses: Record<string, SectionStatus>
): { canGenerate: boolean; missingDeps: string[] } {
  const def = getSectionDef(sectionKey);
  if (!def) return { canGenerate: false, missingDeps: [] };

  const missingDeps: string[] = [];
  for (const depKey of def.dependencies) {
    const status = sectionStatuses[depKey];
    if (status !== "confirmed" && status !== "draft_ready") {
      const depDef = getSectionDef(depKey);
      missingDeps.push(depDef?.title || depKey);
    }
  }

  return { canGenerate: missingDeps.length === 0, missingDeps };
}

/** 计算整体进度 */
export function calculateProgress(sectionStatuses: Record<string, SectionStatus>): number {
  const total = OFFICIAL_SECTIONS.length;
  let confirmed = 0;
  for (const section of OFFICIAL_SECTIONS) {
    if (sectionStatuses[section.key] === "confirmed") {
      confirmed++;
    }
  }
  return Math.round((confirmed / total) * 100);
}
