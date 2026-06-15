<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl w-full">
      <!-- 头部 -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-primary-600 mb-4">🎭 性格测试</h1>
        <p class="text-xl text-gray-600">发现真实的自己，了解你的性格优势</p>
      </div>

      <!-- 介绍卡片 -->
      <div class="card mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">关于这个测试</h2>
        <div class="space-y-3 text-gray-600">
          <p>📊 基于经典的四维度性格模型，包含 <strong>40 道精选题目</strong></p>
          <p>⏱️ 预计耗时 <strong>5-8 分钟</strong></p>
          <p>🎯 你将获得 <strong>16 种性格类型</strong> 中的专属分析</p>
          <p>💡 包含性格特点、优势劣势和职业建议</p>
        </div>
      </div>

      <!-- 维度说明 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div class="card">
          <h3 class="font-bold text-primary-600 mb-2">⚡ 能量来源</h3>
          <p class="text-sm text-gray-600">外向 (E) ←→ 内向 (I)</p>
        </div>
        <div class="card">
          <h3 class="font-bold text-primary-600 mb-2">💭 信息处理</h3>
          <p class="text-sm text-gray-600">直觉 (N) ←→ 感觉 (S)</p>
        </div>
        <div class="card">
          <h3 class="font-bold text-primary-600 mb-2">🤔 决策方式</h3>
          <p class="text-sm text-gray-600">理性 (T) ←→ 感性 (F)</p>
        </div>
        <div class="card">
          <h3 class="font-bold text-primary-600 mb-2">📅 生活态度</h3>
          <p class="text-sm text-gray-600">计划 (J) ←→ 灵活 (P)</p>
        </div>
      </div>

      <!-- 开始按钮 -->
      <div class="text-center">
        <button @click="startTest" class="btn-primary text-lg px-12 py-4">
          🚀 开始测试
        </button>
      </div>

      <!-- 提示信息 -->
      <p class="text-center text-gray-500 text-sm mt-6">
        💡 提示：请根据第一反应作答，没有对错之分
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useTestStore } from '@/stores/test'

const router = useRouter()
const testStore = useTestStore()

async function startTest() {
  await testStore.fetchQuestions()
  router.push('/test')
}
</script>
