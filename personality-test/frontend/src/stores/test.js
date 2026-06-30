import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useTestStore = defineStore('test', () => {
  const questions = ref([])
  const currentQuestionIndex = ref(0)
  const answers = ref({})
  const sessionId = ref('')
  const result = ref(null)
  const isLoading = ref(false)

  // 计算分数
  const scores = computed(() => {
    const dimensionScores = {
      E: 0, I: 0,
      N: 0, S: 0,
      T: 0, F: 0,
      J: 0, P: 0
    }

    questions.value.forEach((q, index) => {
      const answer = answers.value[q.id]
      if (answer !== undefined) {
        const [dim1, dim2] = q.dimension.split('')
        if (q.direction === 1) {
          dimensionScores[dim1] += answer
          dimensionScores[dim2] += (5 - answer)
        } else {
          dimensionScores[dim2] += answer
          dimensionScores[dim1] += (5 - answer)
        }
      }
    })

    return dimensionScores
  })

  // 计算结果类型
  const resultType = computed(() => {
    const s = scores.value
    return [
      s.E >= s.I ? 'E' : 'I',
      s.N >= s.S ? 'N' : 'S',
      s.T >= s.F ? 'T' : 'F',
      s.J >= s.P ? 'J' : 'P'
    ].join('')
  })

  // 获取题目
  async function fetchQuestions() {
    isLoading.value = true
    try {
      const res = await axios.get('/api/questions')
      questions.value = res.data.data
      sessionId.value = uuidv4()
    } catch (error) {
      console.error('获取题目失败:', error)
    } finally {
      isLoading.value = false
    }
  }

  // 保存答案
  function saveAnswer(questionId, answer) {
    answers.value[questionId] = answer
  }

  // 提交测试
  async function submitTest() {
    isLoading.value = true
    try {
      const res = await axios.post('/api/submit', {
        sessionId: sessionId.value,
        answers: answers.value,
        scores: scores.value,
        resultType: resultType.value
      })
      result.value = res.data.data
      return result.value
    } catch (error) {
      console.error('提交失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 重置测试
  function reset() {
    currentQuestionIndex.value = 0
    answers.value = {}
    sessionId.value = ''
    result.value = null
  }

  // 生成 UUID
  function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0
      const v = c === 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
  }

  return {
    questions,
    currentQuestionIndex,
    answers,
    sessionId,
    result,
    isLoading,
    scores,
    resultType,
    fetchQuestions,
    saveAnswer,
    submitTest,
    reset
  }
})
