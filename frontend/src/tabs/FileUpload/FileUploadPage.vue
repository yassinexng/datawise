<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedFile = ref(null)
const fileInput = ref(null)

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const Upload = async () => {
  if (!selectedFile.value) {
    alert("Please select a file.")
    return
  }

  const username = localStorage.getItem('username')
  if (!username) {
    alert("Session expired. Please login again.")
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('username', username)

  try {
    const response = await fetch("http://localhost:8000/api/upload", {
      method: 'POST',
      body: formData,
    })

    if (response.ok) {
      const data = await response.json()
      alert("Upload successful!")
      localStorage.setItem('datasetId', data.id)
      router.push(`/mainpage/DataAnalysis/EDA?id=${data.id}`)
    } else {
      const errorData = await response.json()
      alert("Upload failed: " + (errorData.detail || "Unknown error"))
    }
  } catch (error) {
    alert("Network error occurred.")
  }
}
</script>

<template>
  <div class="upload-container">

    <input type="file" ref="fileInput"  @change="handleFileChange" style="display: none">

    <button @click="triggerFileInput" class="button-c">
      {{ selectedFile ? selectedFile.name : 'Select File' }}
    </button>

    <button @click="Upload" class="button-c upload-btn" v-if="selectedFile">
      Confirm Upload
    </button>
  </div>
</template>

<style scoped>
.upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}

.text-input {
  width: 100%;
  max-width: 320px;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 0.5px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  color: white;
  outline: none;
}

.button-c {
  all: unset;
  cursor: pointer;
  padding: 0.85rem 2rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  transition: 0.3s ease;
  border: 0.5px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.button-c:hover {
  background: rgba(255, 255, 255, 0.15);
}

.upload-btn {
  background: #42b883;
  font-weight: bold;
}

.text-input:first-of-type {
  margin-top: 50px;
}
</style>