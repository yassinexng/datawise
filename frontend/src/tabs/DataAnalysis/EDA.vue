<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const edaData = ref([])
const chartsData = ref([])

const datasetId = route.query.id

function parseJSON(data) {
  if (!data) return []

  let text = data

  if (typeof text === 'string') {
    text = text.replace(/```json/g, '').replace(/```/g, '').trim()
    try {
      text = JSON.parse(text)
    } catch {
      return []
    }
  }

  if (Array.isArray(text)) {
    const result = []
    for (const item of text) {
      if (item && typeof item === 'object' && !Array.isArray(item)) {
        const keys = Object.keys(item)
        if (keys.includes('key') && keys.includes('value')) {
          result.push(item)
        } else {
          for (const k of keys) {
            result.push({ key: k, value: item[k] })
          }
        }
      }
    }
    return result
  }

  if (typeof text === 'object' && text !== null) {
    const result = []
    for (const key in text) {
      result.push({ key: key, value: text[key] })
    }
    return result
  }

  return []
}

function goToClean() {
  router.push({ name: 'Clean', params: { id: datasetId } })
}

function fetchAnalysis() {
  if (!datasetId) {
    error.value = 'No dataset selected'
    loading.value = false
    return
  }

  const sessionKey = 'eda_' + datasetId

  const cached = sessionStorage.getItem(sessionKey)
  if (cached) {
    const parsed = JSON.parse(cached)
    edaData.value = parsed.edaData
    chartsData.value = parsed.chartsData
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  axios.get('http://localhost:8000/dataset/' + datasetId + '/analyze')
    .then(function(response) {
      edaData.value = parseJSON(response.data.initial_eda)
      chartsData.value = response.data.charts_v

      sessionStorage.setItem(sessionKey, JSON.stringify({
        edaData: edaData.value,
        chartsData: chartsData.value
      }))

      loading.value = false
    })
    .catch(function(err) {
      error.value = err.message
      loading.value = false
    })
}

function getChartType(chart) {
  if (chart.type === 'matrix') return 'heatmap'
  if (chart.type === 'scatter') return 'scatter'
  return 'bar'
}

function getChartOptions(chart) {
  const options = {}
  options.chart = { toolbar: { show: true } }
  options.title = { text: chart.title }
  options.xaxis = {}
  options.legend = { show: true }
  options.dataLabels = { enabled: false }
  if (chart.labels && chart.labels.length > 0) {
    options.xaxis.categories = chart.labels
  }
  return options
}

function getChartSeries(chart) {
  if (chart.type === 'matrix') return chart.data
  return [{ name: chart.title, data: chart.data }]
}

onMounted(fetchAnalysis)
</script>

<template>
  <div class="page">

    <div class="header">
      <h1>Dataset Analysis</h1>
      <p v-if="datasetId" class="subtitle">Dataset #{{ datasetId }}</p>
    </div>

    <div v-if="loading" class="state-box">
      Analyzing dataset, please wait...
    </div>

    <div v-if="error" class="state-box error-text">
      {{ error }}
    </div>

    <div v-if="!loading && !error">

      <div class="go-to-clean">
        <p>Analysis complete. clean your dataset?</p>
        <button @click="goToClean">Go to Clean:</button>
      </div>

      <div class="eda-section-wrapper">
        <h2 class="section-heading">EDA Summary</h2>

        <div v-if="edaData.length" class="eda-grid">
          <div v-for="(section, index) in edaData" :key="index" class="eda-card">
            <h3 class="eda-card-title">{{ section.key }}</h3>

            <div v-if="typeof section.value === 'object' && section.value !== null">
              <div v-for="(val, name) in section.value" :key="name" class="eda-row">
                <div class="eda-row-name">{{ name }}</div>
                <div class="eda-row-value">
                  <span v-if="typeof val === 'object'">
                    <div v-for="(metricVal, metricKey) in val" :key="metricKey" class="eda-metric">
                      <span class="eda-metric-key">{{ metricKey }}:</span> {{ metricVal }}
                    </div>
                  </span>
                  <span v-else>{{ val }}</span>
                </div>
              </div>
            </div>

            <div v-else class="eda-row-value">
              {{ section.value }}
            </div>
          </div>
        </div>

        <div v-else class="state-box">
          No EDA data available.
        </div>
      </div>

      <div class="charts-section-wrapper">
        <h2 class="section-heading">Charts</h2>

        <div class="charts-grid">
          <div v-for="(chart, i) in chartsData" :key="i" class="chart-card">
            <VueApexCharts
              :type="getChartType(chart)"
              :options="getChartOptions(chart)"
              :series="getChartSeries(chart)"
              height="380"
            />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #6366f1 0%, #1e1b4b 100%);
  padding: 40px 32px;
  box-sizing: border-box;
}

.header {
  margin-bottom: 32px;
}

.header h1 {
  color: white;
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  font-size: 0.95rem;
}

.go-to-clean {
  display: flex;
  align-items: center;
  gap: 20px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  padding: 18px 24px;
  margin-bottom: 36px;
  width: fit-content;
}

.go-to-clean p {
  color: white;
  margin: 0;
  font-size: 0.95rem;
}

.go-to-clean button {
  padding: 10px 22px;
  background: white;
  color: #4f46e5;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.go-to-clean button:hover {
  background: #e0e7ff;
}

.section-heading {
  color: white;
  font-size: 1.3rem;
  font-weight: 500;
  margin: 0 0 20px 0;
}

.eda-section-wrapper {
  margin-bottom: 48px;
}

.eda-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.eda-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.eda-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #312e81;
  margin: 0 0 14px 0;
  border-bottom: 2px solid #e0e7ff;
  padding-bottom: 8px;
}

.eda-row {
  margin-bottom: 10px;
}

.eda-row-name {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  margin-bottom: 4px;
}

.eda-row-value {
  background: #f3f4f6;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #4b5563;
  word-break: break-word;
}

.eda-metric {
  margin-bottom: 2px;
}

.eda-metric-key {
  font-weight: 600;
}

.charts-section-wrapper {
  margin-bottom: 48px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.state-box {
  color: white;
  padding: 24px;
  font-size: 1rem;
}

.error-text {
  color: #fca5a5;
}
</style>