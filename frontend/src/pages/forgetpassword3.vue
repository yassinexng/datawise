<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const route = useRoute()
const router = useRouter()

const email = ref('')
const code = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')

function passwordHandling() {
  error.value = ""
  if (password.value.length < 6) {
    error.value = "Password must be at least 6 characters."
    return false
  }
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords don't match."
    return false
  }
  return true
}

onMounted(() => {
  email.value = route.query.email || ''
  code.value = route.query.code || '' 
})

async function confirm() {
  const isValid = passwordHandling()
  if (!isValid) return

  const response = await fetch('http://localhost:8000/forgetpassword3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      email: email.value, 
      password: password.value,
      code: code.value
    })
  })
  
  const data = await response.json()
  
  if (response.ok) {
    router.push('/login')
  } else {
    error.value = data.detail || "An unexpected error occurred"
  }
}
</script>

<template>
  <h1>Please enter your new password:</h1>
  
  <input 
    v-model="password" 
    type="password" 
    placeholder="Enter your Password." 
    @input="passwordHandling"
  >
  
  <input 
    v-model="confirmPassword" 
    type="password" 
    placeholder="Confirm your Password." 
    @input="passwordHandling"
  >
  
  <span class="error-message" v-if="error">{{ error }}</span>
  
  <button @click="confirm" class="button">Confirm</button>
  <router-link to="/login" class="button">Go back</router-link>
</template>

<style scoped>
h1 {
  color: black;
  font-size: 2rem;
  font-weight: 300;
  margin-bottom: 1rem;
}
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
.error-message { color: #ff6b6b; font-size: 0.85rem; display: block; margin: 0.5rem 0; text-align: center;}
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