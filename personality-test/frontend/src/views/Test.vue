<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl w-full">
      <!-- 进度条 -->
      <div class="mb-8">
        <div class="flex justify-between text-sm text-gray-600 mb-2">
          <span>进度</span>
          <span>{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
      </div>

      <!-- 题目卡片 -->
      <div v-if="currentQuestion" class="card mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">
          {{ currentQuestion.content }}
        </h2>

        <!-- 选项 -->
        <div class="space-y-3">
          <label 
            v-for="option in options" 
            :key="option.value"
            class="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all"
            :class="getAnswerClass(option.value)"
            @click="selectAnswer(option.value)"
          >
            <input 
              type="radio" 
              :value="option.value"
              :checked="currentAnswer === option.value"
              class="w-5 h-5 text-primary-500"
            >
            <span class="ml-3 text-lg">{{ option.label }}</span>
          </label>
        </div>
      </div>

      <!-- 导航按钮 -->
      <div class="flex justify-between">
        <button 
          @click="prevQuestion"
          :disabled="currentQuestionIndex === 0"
          class="btn-secondary"
        >
          ← 上一题
        </button>
        
        <button 
          v-if="currentQuestionIndex < questions.length - 1"
          @click="nextQuestion"
          :disabled="currentAnswer === undefined"
          class="btn-primary"
        >
          下一题 →
        </button>
        
        <button 
          v-else
          @click="submitTest"
          :disabled="currentAnswer === undefined || isLoading"
          class="btn-primary"
        >
          {{ isLoading ? '提交中...' : '完成测试 🎉' }}
        </button>
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

const questions = computed(() => testStore.questions)
const currentQuestionIndex = computed(() => testStore.currentQuestionIndex)
const answers = computed(() => testStore.answers)
const isLoading = computed(() => testStore.isLoading)

const currentQuestion = computed(() => 
  questions.value[currentQuestionIndex.value]
)

const currentAnswer = computed(() => 
  answers.value[currentQuestion.value?.id]
)

const progressPercent = computed(() => 
  ((currentQuestionIndex.value + 1) / questions.value.length) * 100
)

const options = [
  { value: 1, label: '非常不同意' },
  { value: 2, label: '不同意' },
  { value: 3, label: '不确定' },
  { value: 4, label: '同意' },
  { value: 5, label: '非常同意' }
]

function getAnswerClass(value) {
  if (currentAnswer.value === value) {
    return 'border-primary-500 bg-primary-50'
  }
  return 'border-gray-200 hover:border-primary-300'
}

function selectAnswer(value) {
  testStore.saveAnswer(currentQuestion.value.id, value)
}

function nextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    testStore.currentQuestionIndex++
  }
}

function prevQuestion() {
  if (currentQuestionIndex.value > 0) {
    testStore.currentQuestionIndex--
  }
}

async function submitTest() {
  try {
    await testStore.submitTest()
    router.push('/result')
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请重试')
  }
}
</script>
