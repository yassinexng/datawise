<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const route = useRoute()
const router = useRouter()

const datasetID = route.params.id || localStorage.getItem('datasetId')

const tableData = ref({ columns: [], rows: [] })

const fetchData1 = async () => {
    try {
        if (!datasetID) {
            console.error("No Dataset ID found in URL")
            return
        }
        const response = await fetch('http://localhost:8000/dataset/' + datasetID + '/data')
        if (!response.ok) throw new Error("Network response was not ok")
        const data = await response.json()
        tableData.value = data
    } catch (error) {
        console.error(error)
    }
}

const suggestions = ref([])

const fetchData2 = async () => {
    try {
        if (!datasetID) return
        const response = await fetch('http://localhost:8000/dataset/' + datasetID + '/suggestions')
        if (!response.ok) throw new Error("Network response was not ok")
        const data = await response.json()
        suggestions.value = data.suggestions
    } catch (error) {
        console.error("Error fetching suggestions:", error)
    }
}

const fixedSelections = ref([])
const selectedSuggestions = ref([])
const statusMessage = ref('')
const cleaningDone = ref(false)

const submit = async () => {
    try {
        const operations = [...fixedSelections.value, ...selectedSuggestions.value]
        if (operations.length === 0) return

        statusMessage.value = 'Applying...'
        cleaningDone.value = false

        const response = await fetch('http://localhost:8000/dataset/' + datasetID + '/clean', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operations })
        })
        if (!response.ok) throw new Error("Network response was not ok")

        statusMessage.value = 'Done!'
        cleaningDone.value = true
        await fetchData1()
    } catch (error) {
        console.error("Error applying cleaning:", error)
        statusMessage.value = 'Error applying changes.'
        cleaningDone.value = false
    }
}

function goToVisualize() {
    router.push({ name: 'Visualize', params: { id: datasetID } })
}

onMounted(() => {
    fetchData1()
    fetchData2()
})
</script>

<template>
    <h1> The actual dataset: </h1>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th v-for="col in tableData.columns" :key="col">
                        {{ col }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, index) in tableData.rows" :key="index">
                    <td v-for="(cell, cellIndex) in row" :key="cellIndex">
                        {{ cell }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <h1>Apply these changes: </h1>
    <form>
        <div id="input1">
            <input type="checkbox" id="item1" value="item1" v-model="fixedSelections">
            <label for="item1">Fix all data types (if any).</label>
        </div>
        <div id="input2">
            <input type="checkbox" id="item2" value="item2" v-model="fixedSelections">
            <label for="item2">Remove all duplicates.</label>
        </div>
        <div id="input3">
            <input type="checkbox" id="item3" value="item3" v-model="fixedSelections">
            <label for="item3">Replace the missing values with 0.</label>
        </div>
        <div id="input4" class="suggestions-wrapper">
            <label>Do the following:</label>
            <div v-for="(item, index) in suggestions" :key="index" class="suggestion-item">
                <input type="checkbox" :id="'suggest-' + index" :value="item.suggested_change" v-model="selectedSuggestions">
                <label :for="'suggest-' + index">{{ item.suggested_change }}</label>
            </div>
        </div>
        <div id="submit-row">
            <button type="button" @click="submit">Apply</button>
            <span v-if="statusMessage" class="status">{{ statusMessage }}</span>
        </div>
    </form>

    <div class="go-to-visualize">
        <p>Cleaning complete. Visualize your dataset?</p>
        <button @click="goToVisualize">Go to Visualize:</button>
      </div>
</template>

<style scoped>
h1 {
  color: black;
  font-size: 2rem;
  font-weight: 300;
  margin-bottom: 1rem;
}

.table-container {
  height: 500px;
  overflow-y: scroll;
  overflow-x: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  flex-shrink: 0 to
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  background: #ffffff;
  min-width: 400px;
}

th, td {
  border: 1px solid #e5e7eb;
  padding: 10px 14px;
  text-align: left;
  width: 20%;
  word-wrap: break-word;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  position: sticky;
  top: 0;
  z-index: 2;
  box-shadow: 0 1px 0 #ddd;
}

td {
  font-size: 0.9rem;
  color: #4b5563;
}

tr:nth-child(even) td {
  background-color: #f9fafb;
}

tr:hover td {
  background-color: #eff6ff;
  transition: background 0.15s ease;
}

form {
  max-width: 400px;
  background: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-family: sans-serif;
  margin-top: 20px;
}

div {
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

div:hover {
  background: #f0f4f8;
}

.suggestions-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.suggestion-item {
  display: flex;
  align-items: center;
  width: 100%;
}

input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #2563eb;
  flex-shrink: 0;
}

label {
  margin-left: 12px;
  cursor: pointer;
  font-size: 15px;
  color: #334155;
  user-select: none;
}

button {
  padding: 10px 24px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover {
  background: #1d4ed8;
}

.status {
  margin-left: 12px;
  font-size: 14px;
  color: #374151;
}

#submit-row {
  display: flex;
  align-items: center;
  padding: 10px;
}
.go-to-visualize {
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

.go-to-visualize p {
  color: white;
  margin: 0;
  font-size: 0.95rem;
}

.go-to-visualize button {
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

.go-to-visualize button:hover {
  background: #e0e7ff;
}
</style>