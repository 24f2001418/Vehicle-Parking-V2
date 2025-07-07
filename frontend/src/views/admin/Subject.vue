<template>
  <div class="subject-page">
    <!-- Header -->
    <div class="header">
      <button @click="router.push('/admin')" class="back-btn">← Back</button>
      <h1>Manage Subjects</h1>
      <button @click="openAddModal" class="add-btn">+ Add Subject</button>
    </div>

    <!-- Subject / Chapter list -->
    <div class="subjects-list">
      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="!subjects.length" class="empty">
        <p>No subjects found. Add your first subject!</p>
        <button class="add-btn" @click="openAddModal">Add Subject</button>
      </div>

      <div v-else class="subjects-grid">
        <div v-for="subject in subjects" :key="subject.id" class="subject-card">
          <header class="subject-header">
            <h3>{{ subject.name }}</h3>
            <div class="actions">
              <button class="edit-btn"   @click="editSubject(subject)">Edit</button>
              <button class="delete-btn" @click="deleteSubject(subject)">Delete</button>
            </div>
          </header>

          <p class="description">{{ subject.description || 'No description' }}</p>

          <!-- Chapters -->
          <section class="chapters-section">
            <h4>Chapters ({{ subject.chapters.length }})</h4>
            <button class="add-chapter-btn" @click="addChapter(subject)">+ Add Chapter</button>

            <div v-if="subject.chapters.length" class="chapters-list">
              <div v-for="ch in subject.chapters" :key="ch.id" class="chapter-item">
                <span>{{ ch.name }}</span>
                <div class="chapter-actions">
                  <button class="small-btn"        @click="editChapter(ch)">Edit</button>
                  <button class="small-btn delete" @click="deleteChapter(ch)">Delete</button>
                  <button class="small-btn green"  @click="goToQuizzes(ch)">Quizzes →</button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>

    <!-- Add / Edit Subject modal -->
    <div v-if="showAddModal || showEditModal" class="modal">
      <div class="modal-content">
        <h2>{{ showEditModal ? 'Edit Subject' : 'Add Subject' }}</h2>
        <form @submit.prevent="saveSubject">
          <div class="form-group">
            <label>Name</label>
            <input v-model.trim="formData.name" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model.trim="formData.description" rows="3" />
          </div>
          <footer class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal">Cancel</button>
            <button class="save-btn" type="submit">Save</button>
          </footer>
        </form>
      </div>
    </div>

    <!-- Add / Edit Chapter modal -->
    <div v-if="showChapterModal" class="modal">
      <div class="modal-content">
        <h2>{{ editingChapter ? 'Edit Chapter' : 'Add Chapter' }}</h2>
        <form @submit.prevent="saveChapter">
          <div class="form-group">
            <label>Name</label>
            <input v-model.trim="chapterForm.name" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model.trim="chapterForm.description" rows="3" />
          </div>
          <footer class="modal-actions">
            <button class="cancel-btn" type="button" @click="closeChapterModal">Cancel</button>
            <button class="save-btn" type="submit">Save</button>
          </footer>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/* ── state ───────────────────────────────────────────── */
const subjects = ref([])
const loading  = ref(true)

/* modal flags & forms */
const showAddModal    = ref(false)
const showEditModal   = ref(false)
const showChapterModal= ref(false)
const editingSubject  = ref(null)
const editingChapter  = ref(null)
const selectedSubject = ref(null)

const formData    = ref({ name: '', description: '' })
const chapterForm = ref({ name: '', description: '' })

/* ── helpers ─────────────────────────────────────────── */
const auth = () => ({ Authorization: `Bearer ${localStorage.getItem('token')}` })

/* ── lifecycle ───────────────────────────────────────── */
onMounted(loadSubjects)

/* ── load Subjects & nested Chapters ─────────────────── */
async function loadSubjects () {
  loading.value = true
  const res = await fetch('/api/subjects', { headers: auth() })
  subjects.value = (await res.json()).subjects || []
  await Promise.all(subjects.value.map(loadChapters))
  loading.value = false
}
const loadChapters = async s => {
  const res = await fetch(`/api/subjects/${s.id}/chapters`, { headers: auth() })
  s.chapters = (await res.json()).chapters || []
}

/* ── navigation to quiz page ─────────────────────────── */
const goToQuizzes = ch => router.push(`/chapters/${ch.id}/quizzes`)

/* ── Subject CRUD  (save / delete) ───────────────────── */
function openAddModal () { showAddModal.value = true }
function editSubject(s)  { editingSubject.value = s; formData.value={name:s.name,description:s.description}; showEditModal.value=true }

async function saveSubject () {
  const payload = { ...formData.value }
  const url = editingSubject.value ? `/api/subjects/${editingSubject.value.id}` : '/api/subjects'
  const method = editingSubject.value ? 'PUT' : 'POST'
  const res = await fetch(url,{method,headers:{...auth(),'Content-Type':'application/json'},body:JSON.stringify(payload)})
  if (res.ok) { await loadSubjects(); closeModal() }
}

async function deleteSubject (s) {
  if (!confirm(`Delete "${s.name}"?`)) return
  await fetch(`/api/subjects/${s.id}`,{method:'DELETE',headers:auth()})
  await loadSubjects()
}

function closeModal () {
  showAddModal.value = showEditModal.value = false
  editingSubject.value = null
  formData.value = { name:'',description:'' }
}

/* ── Chapter CRUD ────────────────────────────────────── */
function addChapter (subj){ selectedSubject.value=subj; showChapterModal.value=true }
function editChapter(ch){ editingChapter.value=ch; chapterForm.value={name:ch.name,description:ch.description}; showChapterModal.value=true }

async function saveChapter () {
  const url = editingChapter.value
    ? `/api/chapters/${editingChapter.value.id}`
    : `/api/subjects/${selectedSubject.value.id}/chapters`
  const method = editingChapter.value ? 'PUT' : 'POST'
  await fetch(url,{method,headers:{...auth(),'Content-Type':'application/json'},body:JSON.stringify(chapterForm.value)})
  await loadSubjects()
  closeChapterModal()
}
async function deleteChapter (ch){
  if(confirm('Delete chapter?')){
    await fetch(`/api/chapters/${ch.id}`,{method:'DELETE',headers:auth()})
    await loadSubjects()
  }
}
function closeChapterModal(){
  showChapterModal.value=false; editingChapter.value=null; selectedSubject.value=null
  chapterForm.value={name:'',description:''}
}
</script>

<style scoped>
.subject-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.back-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.add-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.add-btn:hover {
  background: #1d4ed8;
}

.subjects-list {
  min-height: 400px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.empty {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.subject-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.subject-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.subject-header h3 {
  margin: 0;
  color: #1f2937;
}

.actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.edit-btn {
  background: #fbbf24;
  color: white;
}

.delete-btn {
  background: #ef4444;
  color: white;
}

.description {
  color: #6b7280;
  margin-bottom: 20px;
  font-size: 14px;
}

.chapters-section h4 {
  margin: 0 0 10px 0;
  color: #374151;
  font-size: 16px;
}

.add-chapter-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-bottom: 10px;
}

.chapters-list {
  border-top: 1px solid #f3f4f6;
  padding-top: 10px;
}

.chapter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f9fafb;
}

.chapter-item:last-child {
  border-bottom: none;
}

.chapter-actions {
  display: flex;
  gap: 4px;
}

.small-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  background: #f3f4f6;
  color: #374151;
}

.small-btn.delete {
  background: #fee2e2;
  color: #dc2626;
}

/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal-content h2 {
  margin: 0 0 20px 0;
  color: #1f2937;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background: #1d4ed8;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .subjects-grid {
    grid-template-columns: 1fr;
  }
  
  .subject-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .modal-content {
    margin: 20px;
    padding: 20px;
  }
}
</style>
