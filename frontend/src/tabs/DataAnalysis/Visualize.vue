<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()

const datasetID = route.params.id

const loading = ref(true)
const error = ref(null)
const preview = ref({ columns: [], rows: [] })
const charts = ref([])

function fetchData() {
    if (!datasetID) {
        error.value = 'No dataset ID found in URL'
        loading.value = false
        return
    }

    loading.value = true
    error.value = null

    axios.get('http://localhost:8000/dataset/' + datasetID + '/visualize')
        .then(function(response) {
            preview.value = response.data.preview
            charts.value = response.data.charts
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
    const options = {
        chart: {
            toolbar: { show: true },
            background: '#ffffff'
        },
        title: {
            text: chart.title,
            style: { fontSize: '14px', color: '#1e1b4b' }
        },
        xaxis: {},
        legend: { show: true },
        dataLabels: { enabled: false },
        colors: ['#6366f1']
    }

    if (chart.labels && chart.labels.length > 0) {
        options.xaxis.categories = chart.labels
        options.xaxis.labels = {
            rotate: -45,
            style: { fontSize: '11px' }
        }
    }

    if (chart.type === 'matrix') {
        options.colors = ['#6366f1']
        options.xaxis.categories = chart.labels
        options.dataLabels = {
            enabled: true,
            formatter: function(val) {
                return val !== null ? val.toFixed(2) : ''
            },
            style: { fontSize: '10px' }
        }
    }

    return options
}

function getChartSeries(chart) {
    if (chart.type === 'matrix') return chart.data
    return [{ name: chart.title, data: chart.data }]
}

function downloadDataset() {
    const url = 'http://localhost:8000/dataset/' + datasetID + '/download'
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'cleaned_dataset.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
}

onMounted(fetchData)
</script>

<template>
    <div class="page">

        <div class="header">
            <h1>Visualize Dataset</h1>
            <button class="download-btn" @click="downloadDataset">Download Cleaned Dataset</button>
        </div>

        <div v-if="loading" class="state-box">
            Loading charts, please wait...
        </div>

        <div v-if="error" class="state-box error-text">
            {{ error }}
        </div>

        <div v-if="!loading && !error">

            <div class="section">
                <h2 class="section-title">Dataset Preview</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th v-for="col in preview.columns" :key="col">{{ col }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, rowIndex) in preview.rows" :key="rowIndex">
                                <td v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Charts</h2>

                <div v-if="charts.length === 0" class="state-box">
                    No charts could be generated for this dataset.
                </div>

                <div class="charts-grid">
                    <div v-for="(chart, index) in charts" :key="index" class="chart-card">
                        <VueApexCharts
                            :type="getChartType(chart)"
                            :options="getChartOptions(chart)"
                            :series="getChartSeries(chart)"
                            height="350"
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
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 36px;
    flex-wrap: wrap;
    gap: 16px;
}

.header h1 {
    color: white;
    font-size: 2rem;
    font-weight: 600;
    margin: 0;
}

.download-btn {
    padding: 12px 24px;
    background: white;
    color: #4f46e5;
    border: none;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}

.download-btn:hover {
    background: #e0e7ff;
}

.section {
    margin-bottom: 48px;
}

.section-title {
    color: white;
    font-size: 1.3rem;
    font-weight: 500;
    margin: 0 0 20px 0;
}

.table-container {
    height: 280px;
    overflow-y: scroll;
    overflow-x: auto;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    flex-shrink: 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    min-width: 400px;
    table-layout: fixed;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
    font-size: 0.85rem;
    color: #374151;
    padding: 10px 14px;
    border: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 2;
    box-shadow: 0 1px 0 #ddd;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

td {
    padding: 10px 14px;
    border: 1px solid #e5e7eb;
    font-size: 0.9rem;
    color: #4b5563;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

tr:nth-child(even) td {
    background-color: #f9fafb;
}

tr:hover td {
    background-color: #eff6ff;
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
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