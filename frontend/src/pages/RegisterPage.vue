<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const usernameError = ref('')
const emailError = ref('')


function checkPasswordMatch() {
  if (confirmPassword.value && password.value !== confirmPassword.value) {
    passwordError.value = "Passwords don't match"
  } else {
    passwordError.value = ""
  }
}

function checkPassword(){
  if(password.value.length < 6) {
    passwordError.value = "Password value must be at least 6 characters."
  }
}

const passwordHandling = () => {
checkPasswordMatch();
checkPassword();
}

function usernameHandling() {
  if((username.value.length > 0 && username.value.length < 2)){
    usernameError.value = "Enter a valid username."
  }
  else{
    usernameError.value =  ""
  }
}

function checkEmail() {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value) {
    emailError.value = 'Email is required'
  } else if (!emailRegex.test(email.value)) {
    emailError.value = 'Please enter a valid email address'
  } else {
    emailError.value = ''
  }
}
function showRegisterButton() {
  return email.value && 
         username.value && 
         password.value && 
         confirmPassword.value && 
         password.value === confirmPassword.value
}

async function register() {
  const response = await fetch('http://localhost:8000/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email.value,
      username: username.value,
      password: password.value,
      confirmPassword: confirmPassword.value
    })
  })
  if (response.ok) {
    router.push(`/confirmemail?email=${encodeURIComponent(email.value)}`)
  } else {
    const data = await response.json()
    emailError.value = data.detail
  }
}
</script>

<template>
<h1>Register</h1>
<input v-model="email" @input="checkEmail" placeholder="Email">
<span class="error-message" v-if="emailError">{{ emailError }}</span>
<input v-model="username" placeholder="Username" @input="usernameHandling">
<span class="error-message" v-if="usernameError">{{ usernameError }}</span>
<input v-model="password" type="password" placeholder="Password" @input="passwordHandling">
<input v-model="confirmPassword" type="password" placeholder="Confirm Password" @input="passwordHandling">
<span class="error-message" v-if="passwordError">{{ passwordError }}</span>
<button v-if="showRegisterButton()" @click="register" class="button">Register</button>
<router-link to="/" class="button">Go back</router-link>
</template>

<style scoped>
h1 {
  color: white;
  text-align: center;
  font-size: 2.5rem;
  font-weight: 300;
  letter-spacing: -0.5px;
  margin-bottom: 2.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  opacity: 0.95;
}

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

input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 300;
  letter-spacing: 0.3px;
}

input:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

input:focus {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.2);
}

input:first-of-type {
  margin-top: 0;
}

.button {
  display: inline-block;
  margin: 2rem 0.5rem 0.5rem;
  padding: 0.875rem 2.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.button:active {
  transform: translateY(0);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.15);
}

.error-message {
  color: red;
  font-size: 12px;
  margin-left: 10px;
}
</style>