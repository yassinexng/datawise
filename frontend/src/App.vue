<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
const headerClass = ref('maintitle')
const route = useRoute()

</script>

<template>
  <div class="app-container">
    
    <div v-if="route.path === '/'" class="home-content">
      <h1 :class="headerClass">Welcome to this ML Engine App!</h1>

      <nav>
        <router-link to="/login" class="button">Login</router-link>
        <router-link to="/register" class="button">Register</router-link>
      </nav>
    </div>

    <router-view />
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}


.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #6366f1 0%, #1e1b4b 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.maintitle {
  color: white;
  text-align: center;
  font-size: 2.5rem;
  font-weight: 300;
  letter-spacing: -0.5px;
  margin-bottom: 2.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  opacity: 0.95;
}

nav {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin: 2rem 0;
}

.button {
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

hr {
  width: 100px;
  margin: 2rem auto;
  border: none;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.router-view {
  width: 100%;
  max-width: 400px;
  margin-top: 2rem;
}
</style>