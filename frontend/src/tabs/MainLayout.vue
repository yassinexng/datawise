<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = ref(null)
const isSidebarExpanded = ref(true)
const datasetId = ref(null)

onMounted(() => {
  datasetId.value = localStorage.getItem('datasetId')
})

function toggleTab(tabName) {
  if (activeTab.value === tabName) {
    activeTab.value = null
  } else {
    activeTab.value = tabName
  }
}

function toggleSidebar() {
  isSidebarExpanded.value = !isSidebarExpanded.value
}
</script>

<template>
  <div class="layout-wrapper">
    <aside class="sidebar-nav" :class="{ 'collapsed': !isSidebarExpanded }">
      <div class="sidebar-header">
        <button @click="toggleSidebar" class="toggle-btn">
          <span>☰</span>
        </button>
        <h3 v-if="isSidebarExpanded">ML Engine</h3>
      </div>
      
      <div v-if="isSidebarExpanded" class="nav-links">
        <router-link to="/mainpage/upload" class="button main-tab">File Upload</router-link>

        <div class="menu-group">
          <button @click="toggleTab('analysis')" class="button main-tab">
            Data Analysis 
            <span class="arrow">{{ activeTab === 'analysis' ? '▼' : '▶' }}</span>
          </button>
          
          <div v-if="activeTab === 'analysis'" class="sub-links">
            <router-link :to="datasetId ? '/mainpage/DataAnalysis/EDA?id=' + datasetId : '/mainpage/DataAnalysis/EDA'" class="button sub-item">Exploratory Data</router-link>
            <router-link :to="datasetId ? '/mainpage/DataAnalysis/Clean/' + datasetId : '#'" class="button sub-item">Data Cleaning</router-link>
            <router-link to="/mainpage/DataAnalysis/Visualize" class="button sub-item">Visualization</router-link>
          </div>
        </div>
      </div>
      
      <div v-if="isSidebarExpanded" class="sidebar-footer">
        <hr />
        <router-link to="/mainpage" class="button back">Main Menu</router-link>
        <router-link to="/" class="button logout">Logout</router-link>
      </div>
    </aside>

    <main class="main-content">
      <div v-if="route.path === '/mainpage'" class="welcome-container">
        <h2 class="maintitle">ML Dashboard</h2>
        <p class="subtitle">Upload a file to start.</p>
      </div>
      
      <router-view />
    </main>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.layout-wrapper {
  display: flex;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #6366f1 0%, #1e1b4b 100%);
  overflow: hidden;
  font-family: sans-serif;
}

.sidebar-nav {
  width: 300px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  padding: 2rem 1.2rem;
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.sidebar-nav.collapsed {
  width: 60px;
  padding: 2rem 0.5rem;
}

.sidebar-header {
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-btn {
  background: #000000;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-header h3 {
  color: white;
  border-left: 3px solid #6366f1;
  padding-left: 1rem;
  font-weight: 300;
  letter-spacing: 1px;
  white-space: nowrap;
}

.nav-links {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.button {
  all: unset;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 0.85rem 1.2rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  transition: 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.sub-links {
  margin-top: 5px;
  padding-left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.sub-item {
  font-size: 0.85rem;
  opacity: 0.7;
  background: rgba(255, 255, 255, 0.03);
}

.router-link-active {
  background: rgba(99, 102, 241, 0.4) !important;
  border-color: #6366f1 !important;
  opacity: 1;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
}

hr {
  border: none;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
}

.back { background: rgba(99, 102, 241, 0.2); }
.logout { background: rgba(239, 68, 68, 0.1); }

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 3rem;
  display: flex;
  flex-direction: column;
}

.welcome-container {
  margin: auto;
  text-align: center;
}

.maintitle {
  color: white;
  font-size: 3.5rem;
  font-weight: 200;
}

.subtitle {
  color: rgba(255, 255, 255, 0.5);
  margin-top: 1rem;
}

.arrow {
  font-size: 0.8rem;
}
</style>