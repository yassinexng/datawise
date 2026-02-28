<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

async function login() {
  const response = await fetch('http://localhost:8000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: username.value, password: password.value })
  })
  const data = await response.json()
  if (response.ok) {
    localStorage.setItem('username', username.value)
    router.push('/mainpage')
  } else {
    error.value = data.detail || 'Login failed'
  }
}
</script>

<template>
  <h1>Login</h1>
  <input v-model="username" placeholder="Username">
  <input v-model="password" type="password" placeholder="Password">
  <span class="error-message" v-if="error">{{ error }}</span>

  <div class="button-container">
  <button @click="login" class="button">Login</button>
  <router-link to="/" class="button">Go back</router-link>
  </div>
   <router-link to ="/forgetpassword1" class="button">Forget Password?</router-link>
 
</template>

<style scoped>
input {
  width: 100%;
  max-width: 320px;
  padding: 1rem 1.5rem;
  margin: 0.5rem auto;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  color: white;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: block;
}
input::placeholder { color: rgba(255, 255, 255, 0.6); font-weight: 300; letter-spacing: 0.3px; }
input:hover { background: rgba(255, 255, 255, 0.15); border-color: rgba(255, 255, 255, 0.3); }
input:focus { background: rgba(255, 255, 255, 0.2); border-color: rgba(255, 255, 255, 0.5); box-shadow: 0 4px 25px rgba(0, 0, 0, 0.2); }
input:first-of-type { margin-top: 0; }
.button {
  display: inline-block;
  margin: 0;
  padding: 0.875rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 120px;
  cursor: pointer;
  margin-top: 8px;       

}
.button-container {
  display: flex;            
  justify-content: center;  
  gap: 1rem;               
  margin-top: 0px;       
}
.button:hover { background: rgba(255, 255, 255, 0.2); transform: translateY(-2px); box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2); border-color: rgba(255, 255, 255, 0.4); }
.button:active { transform: translateY(0); box-shadow: 0 2px 15px rgba(0, 0, 0, 0.15); }
.error-message { color: #ff6b6b; font-size: 0.85rem; margin: 0.25rem 0; display: block; }
</style>