<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-3xl mx-auto">
      <!-- 返回按钮 -->
      <button @click="goHome" class="text-primary-500 hover:text-primary-600 mb-6">
        ← 返回首页
      </button>

      <div v-if="result" class="space-y-8">
        <!-- 结果头部 -->
        <div class="card text-center">
          <h1 class="text-6xl font-bold text-primary-600 mb-4">{{ result.type }}</h1>
          <h2 class="text-3xl font-bold text-gray-800 mb-4">{{ result.type_name }}</h2>
          <p class="text-lg text-gray-600">{{ result.description }}</p>
        </div>

        <!-- 维度得分 -->
        <div class="card">
          <h3 class="text-xl font-bold text-gray-800 mb-6">📊 你的维度得分</h3>
          <div class="space-y-4">
            <div class="dimension-bar">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>能量来源</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm w-20 text-right">外向 (E)</span>
                <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-500"
                    :style="{ width: (result.scores.E / (result.scores.E + result.scores.I) * 100) + '%' }"
                  ></div>
                </div>
                <span class="text-sm w-20">内向 (I)</span>
              </div>
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>{{ result.scores.E }}</span>
                <span>{{ result.scores.I }}</span>
              </div>
            </div>

            <div class="dimension-bar">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>信息处理</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm w-20 text-right">直觉 (N)</span>
                <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-500"
                    :style="{ width: (result.scores.N / (result.scores.N + result.scores.S) * 100) + '%' }"
                  ></div>
                </div>
                <span class="text-sm w-20">感觉 (S)</span>
              </div>
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>{{ result.scores.N }}</span>
                <span>{{ result.scores.S }}</span>
              </div>
            </div>

            <div class="dimension-bar">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>决策方式</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm w-20 text-right">理性 (T)</span>
                <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-500"
                    :style="{ width: (result.scores.T / (result.scores.T + result.scores.F) * 100) + '%' }"
                  ></div>
                </div>
                <span class="text-sm w-20">感性 (F)</span>
              </div>
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>{{ result.scores.T }}</span>
                <span>{{ result.scores.F }}</span>
              </div>
            </div>

            <div class="dimension-bar">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>生活态度</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm w-20 text-right">计划 (J)</span>
                <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-500"
                    :style="{ width: (result.scores.J / (result.scores.J + result.scores.P) * 100) + '%' }"
                  ></div>
                </div>
                <span class="text-sm w-20">灵活 (P)</span>
              </div>
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>{{ result.scores.J }}</span>
                <span>{{ result.scores.P }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 优势 -->
        <div class="card">
          <h3 class="text-xl font-bold text-gray-800 mb-4">✨ 你的优势</h3>
          <p class="text-gray-600">{{ result.strengths }}</p>
        </div>

        <!-- 劣势 -->
        <div class="card">
          <h3 class="text-xl font-bold text-gray-800 mb-4">⚠️ 需要注意</h3>
          <p class="text-gray-600">{{ result.weaknesses }}</p>
        </div>

        <!-- 职业建议 -->
        <div class="card">
          <h3 class="text-xl font-bold text-gray-800 mb-4">💼 职业建议</h3>
          <p class="text-gray-600">{{ result.career_suggestions }}</p>
        </div>

        <!-- 分享按钮 -->
        <div class="text-center">
          <button @click="shareResult" class="btn-primary">
            📤 分享结果
          </button>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-else class="text-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mx-auto"></div>
        <p class="text-gray-600 mt-4">加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTestStore } from '@/stores/test'

const router = useRouter()
const testStore = useTestStore()

const result = computed(() => testStore.result)

function goHome() {
  testStore.reset()
  router.push('/')
}

function shareResult() {
  const text = `我的性格类型是 ${result.value.type} - ${result.value.type_name}！来测测你的性格吧～`
  if (navigator.share) {
    navigator.share({
      title: '性格测试结果',
      text: text,
      url: window.location.origin
    })
  } else {
    navigator.clipboard.writeText(text)
    alert('结果已复制到剪贴板！')
  }
}
</script>
