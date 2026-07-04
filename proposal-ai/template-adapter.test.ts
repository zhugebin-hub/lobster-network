import { describe, it, expect } from "vitest";
import { OFFICIAL_SECTIONS } from "./workflow_official";
import { generateLLMPrompt } from "./llmPrompts";

describe("Template Adapter - New Template Structure", () => {
  it("should have correct number of sections", () => {
    expect(OFFICIAL_SECTIONS.length).toBeGreaterThan(0);
    console.log(`Total sections: ${OFFICIAL_SECTIONS.length}`);
  });

  it("should have all sections with required fields", () => {
    for (const section of OFFICIAL_SECTIONS) {
      expect(section).toHaveProperty("key");
      expect(section).toHaveProperty("title");
      expect(section).toHaveProperty("description");
      expect(section).toHaveProperty("wordLimit");
      expect(section.wordLimit).toBeGreaterThan(0);
    }
  });

  it("should generate valid LLM prompts for each section", () => {
    for (const section of OFFICIAL_SECTIONS) {
      const prompt = generateLLMPrompt(section.key, {
        title: "测试项目",
        researchField: "信息技术",
        applicantUnit: "测试大学",
      });
      expect(prompt).toBeTruthy();
      expect(prompt.length).toBeGreaterThan(0);
      console.log(`✓ Prompt for ${section.title}: ${prompt.substring(0, 50)}...`);
    }
  });

  it("should have sections organized by parts", () => {
    const parts = new Set<string>();
    for (const section of OFFICIAL_SECTIONS) {
      if (section.part) {
        parts.add(section.part);
      }
    }
    console.log(`Sections organized in ${parts.size} parts`);
    expect(parts.size).toBeGreaterThan(0);
  });

  it("should have proper word limits for each section", () => {
    const wordLimits = OFFICIAL_SECTIONS.map((s) => ({
      title: s.title,
      limit: s.wordLimit,
    }));
    console.log("Word limits by section:");
    wordLimits.forEach((w) => {
      console.log(`  ${w.title}: ${w.limit}字`);
    });
    
    // 验证总字数合理
    const totalWords = OFFICIAL_SECTIONS.reduce((sum, s) => sum + s.wordLimit, 0);
    expect(totalWords).toBeGreaterThan(10000);
    console.log(`Total word limit: ${totalWords}字`);
  });

  it("should have dependencies properly defined", () => {
    for (const section of OFFICIAL_SECTIONS) {
      if (section.dependencies && section.dependencies.length > 0) {
        for (const dep of section.dependencies) {
          const depSection = OFFICIAL_SECTIONS.find((s) => s.key === dep);
          expect(depSection).toBeDefined();
        }
      }
    }
    console.log("✓ All section dependencies are valid");
  });
});
