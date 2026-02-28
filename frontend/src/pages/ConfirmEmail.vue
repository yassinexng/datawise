<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const code = ref('')
const error = ref('')
const email = ref('')

onMounted(() => {
  email.value = route.query.email
})

async function confirm() {
  const response = await fetch('http://localhost:8000/confirmemail', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.value, code: code.value })
  })
  const data = await response.json()
  if (response.ok) {
    router.push('/login')
  } else {
    error.value = data.detail
  }
}
</script>

<template>
  <h1>Email Confirmation</h1>
  <p>Code sent to <strong>{{ email }}</strong></p>
  <input v-model="code" placeholder="Enter your code">
  <span class="error-message" v-if="error">{{ error }}</span>
  <button @click="confirm" class="button">Confirm</button>
  <router-link to="/register" class="button">Go back</router-link>
</template>

<style scoped>
h1 {
  color: black;
  font-size: 2rem;
  font-weight: 300;
  margin-bottom: 1rem;
}
p { color: rgba(255,255,255,0.7); margin-bottom: 1rem; }
input {
  width: 100%;
  max-width: 320px;
  padding: 1rem 1.5rem;
  margin: 0.5rem auto;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50px;
  color: white;
  font-size: 1rem;
  outline: none;
  display: block;
  backdrop-filter: blur(10px);
}
input::placeholder { color: rgba(255,255,255,0.5); }
input:focus { background: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.5); }
.error-message { color: #ff6b6b; font-size: 0.85rem; display: block; margin: 0.5rem 0; }
.button {
  display: inline-block;
  margin: 1rem 0.5rem;
  padding: 0.875rem 2.5rem;
  background: rgba(255,255,255,0.1);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}
.button:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px); }
</style>