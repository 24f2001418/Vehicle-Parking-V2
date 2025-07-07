<template>
  <div class="quiz-admin-page">
    <!-- Header -->
    <div class="header">
      <button class="back-btn" @click="router.back()">← Back</button>
      <h1>Manage Quizzes</h1>
      <button class="add-btn" @click="startAdd">+ Add Quiz</button>
    </div>

    <!-- Inline add / edit form -->
    <div v-if="showForm" class="form-card">
      <h2>{{ editingQuiz ? 'Edit Quiz' : 'Add Quiz' }}</h2>
      <form @submit.prevent="saveQuiz">
        <input v-model.trim="quizForm.title" placeholder="Title" required />

        <div class="row">
          <input type="date" v-model="quizForm.date_of_quiz" />
          <input v-model.trim="quizForm.time_duration"
                 placeholder="Duration HH:MM" />
        </div>

        <textarea v-model.trim="quizForm.remarks"
                  rows="2" placeholder="Remarks" />

        <div class="actions">
          <button type="button" class="cancel-btn" @click="resetForm">Cancel</button>
          <button class="save-btn" type="submit">
            {{ editingQuiz ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Quiz list -->
    <div class="list-wrapper">
      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="!quizzes.length" class="empty">No quizzes yet.</div>

      <div v-else class="grid">
        <div v-for="q in quizzes" :key="q.id" class="quiz-card">
          <header class="quiz-head">
            <h3>{{ q.title || 'Untitled quiz' }}</h3>
            <div class="actions">
              <button class="small" @click="editQuiz(q)">Edit</button>
              <button class="small danger" @click="deleteQuiz(q)">Delete</button>
            </div>
          </header>

          <p class="meta">
            Duration {{ q.time_duration || '–' }}
            <span v-if="q.date_of_quiz">| {{ q.date_of_quiz }}</span>
          </p>

          <!-- Questions -->
          <h4>Questions ({{ q.questions.length }})</h4>
          <button class="small add" @click="openAddQuestion(q)">
            + Add Question
          </button>

          <div v-if="q.questions.length" class="question-list">
            <div v-for="que in q.questions" :key="que.id" class="question-item">
              <span>{{ que.question_statement }}</span>
              <div class="q-actions">
                <button class="tiny" @click="editQuestion(que, q)">Edit</button>
                <button class="tiny danger" @click="deleteQuestion(que)">
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Question modal (kept as modal for brevity) -->
    <Modal v-if="showQuestionModal" title="Question"
           :editing="!!editingQuestion"
           @close="closeQuestion"
           @save="saveQuestion">
      <textarea v-model.trim="questionForm.question_statement" rows="3" required />
      <input v-for="n in 4" :key="n" v-model.trim="questionForm['option'+n]"
             :placeholder="'Option '+n" required />
      <input type="number" min="1" max="4"
             v-model.number="questionForm.correct_option"
             placeholder="Correct (1‑4)" required />
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Modal from '@/components/BasicModal.vue'

const API   = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const route = useRoute()
const router= useRouter()
const chapterId = route.params.chapterId

/* quizzes */
const quizzes = ref([])
const loading = ref(true)

/* inline form state */
const showForm   = ref(false)
const editingQuiz= ref(null)
const quizForm   = ref({ title:'', date_of_quiz:'', time_duration:'', remarks:'' })

/* question modal */
const showQuestionModal = ref(false)
const editingQuestion   = ref(null)
const activeQuiz        = ref(null)
const questionForm      = ref({
  question_statement:'', option1:'', option2:'', option3:'', option4:'', correct_option:1
})

const auth = () => ({ Authorization:`Bearer ${localStorage.getItem('token')}` })

onMounted(loadQuizzes)

/* ── load quizzes for this chapter ── */
async function loadQuizzes () {
  loading.value = true
  const { data } = await axios.get(`${API}/chapters/${chapterId}/quizzes`,
                                   { headers: auth() })
  quizzes.value = data.quizzes || []
  for (const q of quizzes.value) {
    const resQ = await axios.get(`${API}/quizzes/${q.id}/questions`,
                                 { headers: auth() })
    q.questions = resQ.data.questions || []
  }
  loading.value = false
}

/* ── form helpers ── */
function resetForm () {
  showForm.value = false
  editingQuiz.value = null
  quizForm.value = { title:'', date_of_quiz:'', time_duration:'', remarks:'' }
}
function startAdd () { resetForm(); showForm.value = true }
function editQuiz (q) {
  editingQuiz.value = q
  quizForm.value = { ...q }
  showForm.value = true
}

async function saveQuiz () {
  const payload = { ...quizForm.value }
  const url     = editingQuiz.value
    ? `${API}/quizzes/${editingQuiz.value.id}`
    : `${API}/chapters/${chapterId}/quizzes`
  const method  = editingQuiz.value ? 'PUT' : 'POST'
  await axios({ url, method, data: payload,
                headers:{ ...auth(),'Content-Type':'application/json'} })
  await loadQuizzes()
  resetForm()
}
async function deleteQuiz (q) {
  if (confirm('Delete this quiz?')) {
    await axios.delete(`${API}/quizzes/${q.id}`, { headers: auth() })
    await loadQuizzes()
  }
}

/* ── Question helpers (modal) ── */
function openAddQuestion(q){ activeQuiz.value=q; editingQuestion.value=null
  questionForm.value={question_statement:'',option1:'',option2:'',option3:'',option4:'',correct_option:1}
  showQuestionModal.value=true }
function editQuestion(que,q){ activeQuiz.value=q; editingQuestion.value=que
  questionForm.value={...que}; showQuestionModal.value=true }
function closeQuestion(){ showQuestionModal.value=false; editingQuestion.value=null; activeQuiz.value=null }

async function saveQuestion(){
  const url = editingQuestion.value
    ? `${API}/questions/${editingQuestion.value.id}`
    : `${API}/quizzes/${activeQuiz.value.id}/questions`
  const method = editingQuestion.value?'PUT':'POST'
  await axios({url,method,data:{...questionForm.value},
               headers:{...auth(),'Content-Type':'application/json'}})
  await loadQuizzes(); closeQuestion()
}
async function deleteQuestion(que){
  if(confirm('Delete question?')){
    await axios.delete(`${API}/questions/${que.id}`,{headers:auth()})
    await loadQuizzes()
  }
}
</script>

<style scoped>
.quiz-admin-page{max-width:1100px;margin:auto;padding:20px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:25px}
.back-btn{background:#f3f4f6;border:1px solid #d1d5db;padding:8px 14px;border-radius:6px;cursor:pointer}
.add-btn{background:#2563eb;color:#fff;border:none;padding:10px 20px;border-radius:6px;cursor:pointer}

/* inline form card */
.form-card{border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin-bottom:25px;background:#f9fafb}
.form-card h2{margin-top:0}
.form-card input, .form-card textarea{width:100%;margin:6px 0;padding:8px;border:1px solid #d1d5db;border-radius:4px}
.row{display:flex;gap:10px}
.actions{margin-top:10px;display:flex;gap:8px;justify-content:flex-end}
.cancel-btn{background:#f3f4f6;border:1px solid #d1d5db;padding:8px 16px;border-radius:4px}
.save-btn{background:#2563eb;color:#fff;border:none;padding:8px 16px;border-radius:4px}

/* quiz list */
.list-wrapper{min-height:300px}.loading,.empty{text-align:center;padding:40px;color:#6b7280}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}
.quiz-card{border:1px solid #e5e7eb;border-radius:8px;padding:20px;background:#fff}
.quiz-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.small{padding:5px 10px;border:none;border-radius:4px;background:#fbbf24;font-size:12px;cursor:pointer}
.small.danger{background:#ef4444;color:#fff}
.add{background:#10b981!important;color:#fff;font-size:12px}
.meta{font-size:13px;color:#6b7280;margin-bottom:12px}
.question-item{display:flex;justify-content:space-between;align-items:center;padding:6px 0}
.tiny{padding:3px 6px;border:none;border-radius:3px;background:#e5e7eb;font-size:11px;cursor:pointer}
.tiny.danger{background:#dc2626;color:#fff}
</style>
