<template>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div>
        <h1>📊 Statistiques</h1>
        <p>Analysez votre productivité et vos habitudes</p>
      </div>
      <div class="header-actions">
        <button @click="loadAllData" :disabled="loading" class="btn-refresh">
          <span :class="{ spinning: loading }">🔄</span>
          Actualiser
        </button>
        <button @click="exportStats" class="btn-export">
          📥 Exporter
        </button>
      </div>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="loading">
      <div class="spinner">⏳</div>
      <p>Chargement des statistiques...</p>
    </div>

    <!-- Contenu principal -->
    <div v-else class="dashboard">
      
      <!-- Métriques principales -->
      <section class="metrics-section">
        <h2>📈 Vue d'ensemble</h2>
        <div class="metrics-grid">
          
          <!-- Total todos -->
          <div class="metric-card primary">
            <div class="metric-icon">📝</div>
            <div class="metric-content">
              <div class="metric-value">{{ generalStats.total }}</div>
              <div class="metric-label">Todos au total</div>
            </div>
          </div>

          <!-- Taux de completion -->
          <div class="metric-card success">
            <div class="metric-icon">✅</div>
            <div class="metric-content">
              <div class="metric-value">{{ generalStats.completionRate }}%</div>
              <div class="metric-label">Taux de completion</div>
            </div>
          </div>

          <!-- TodoLists -->
          <div class="metric-card info">
            <div class="metric-icon">📋</div>
            <div class="metric-content">
              <div class="metric-value">{{ generalStats.totalLists }}</div>
              <div class="metric-label">TodoLists</div>
            </div>
          </div>

          <!-- Priorité moyenne -->
          <div class="metric-card warning">
            <div class="metric-icon">⭐</div>
            <div class="metric-content">
              <div class="metric-value">{{ generalStats.avgPriority }}</div>
              <div class="metric-label">Priorité moyenne</div>
            </div>
          </div>

        </div>
      </section>

      <!-- Graphiques -->
      <section class="charts-section">
        <h2>📊 Graphiques</h2>
        
        <div class="charts-grid">
          
          <!-- Répartition completion -->
          <div class="chart-card">
            <h3>🎯 Répartition des todos</h3>
            <div class="chart-container">
              <Doughnut 
                :data="chartData.completionChart" 
                :options="chartOptions.doughnut"
              />
            </div>
          </div>

          <!-- Statistiques par priorité -->
          <div class="chart-card">
            <h3>⭐ Todos par priorité</h3>
            <div class="chart-container">
              <Bar 
                :data="chartData.priorityChart" 
                :options="chartOptions.bar"
              />
            </div>
          </div>

          <!-- Performance par TodoList -->
          <div class="chart-card">
            <h3>📋 Performance par liste</h3>
            <div class="chart-container">
              <Bar 
                :data="chartData.todoListChart" 
                :options="chartOptions.horizontalBar"
              />
            </div>
          </div>

        </div>
      </section>

      <!-- Tableaux détaillés -->
      <section class="tables-section">
        <h2>📝 Détails</h2>
        
        <div class="tables-grid">
          
          <!-- TodoLists performance -->
          <div class="table-card">
            <h3>📋 Performance des TodoLists</h3>
            <div class="table-container">
              <table class="table">
                <thead>
                  <tr>
                    <th>Liste</th>
                    <th>Total</th>
                    <th>Complétés</th>
                    <th>Taux</th>
                    <th>Priorité moy.</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="stat in todoListStats" :key="stat.todolist.id">
                    <td class="todolist-name">{{ stat.todolist.name }}</td>
                    <td>{{ stat.totalTodos }}</td>
                    <td>{{ stat.completedTodos }}</td>
                    <td>
                      <span :class="getCompletionRateClass(stat.completionRate)">
                        {{ stat.completionRate }}%
                      </span>
                    </td>
                    <td>{{ stat.avgPriority }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Priorités breakdown -->
          <div class="table-card">
            <h3>⭐ Répartition par priorité</h3>
            <div class="table-container">
              <table class="table">
                <thead>
                  <tr>
                    <th>Priorité</th>
                    <th>Total</th>
                    <th>Complétés</th>
                    <th>Pourcentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="stat in priorityStats" :key="stat.priority">
                    <td>
                      <span class="priority-badge">
                        {{ stat.priority }}
                      </span>
                    </td>
                    <td>{{ stat.count }}</td>
                    <td>{{ stat.completed }}</td>
                    <td>
                      <div class="progress-bar">
                        <div 
                          class="progress-fill"
                          :style="{ width: `${stat.percentage}%` }"
                        ></div>
                        <span class="progress-text">{{ stat.percentage }}%</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useStatistics } from '@/composables/useStatistics';
import { useNotifications } from '@/composables/useNotifications';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'vue-chartjs';

// Configuration Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const {
  loading,
  loadAllData,
  exportStats,
  generalStats,
  priorityStats,
  todoListStats,
  chartData
} = useStatistics();

const { success } = useNotifications();

// Charger les données au montage
onMounted(() => {
  loadAllData();
});

// Options des graphiques
const chartOptions = {
  bar: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  },
  horizontalBar: {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100
      }
    }
  },
  doughnut: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      }
    }
  }
};

// Utilitaires
const getCompletionRateClass = (rate: number) => {
  if (rate >= 80) return 'rate-excellent';
  if (rate >= 50) return 'rate-good';
  return 'rate-poor';
};
</script>

<style scoped>
/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.header p {
  color: #6b7280;
  font-size: 1.1rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-refresh, .btn-export {
  background: white;
  border: 2px solid #e5e7eb;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-refresh:hover, .btn-export:hover {
  border-color: #4f46e5;
  color: #4f46e5;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

.btn-export {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

.btn-export:hover {
  background: #4338ca;
  border-color: #4338ca;
  color: white;
}

/* Loading */
.loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.spinner {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: spin 1s linear infinite;
}

/* Dashboard */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

/* Sections */
.metrics-section h2,
.charts-section h2,
.tables-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Métriques principales */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  font-size: 2.5rem;
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  flex-shrink: 0;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-label {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Types de métriques */
.metric-card.primary .metric-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.metric-card.primary .metric-value {
  color: #667eea;
}

.metric-card.success .metric-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.metric-card.success .metric-value {
  color: #10b981;
}

.metric-card.info .metric-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.metric-card.info .metric-value {
  color: #3b82f6;
}

.metric-card.warning .metric-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.metric-card.warning .metric-value {
  color: #f59e0b;
}

/* Graphiques */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.chart-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-container {
  height: 300px;
  position: relative;
}

/* Tableaux */
.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.table-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.table-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.table th {
  background: #f9fafb;
  color: #374151;
  font-weight: 600;
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  color: #1f2937;
}

.table tr:hover {
  background: #f9fafb;
}

.todolist-name {
  font-weight: 500;
  color: #1f2937;
}

.priority-badge {
  background: #4f46e5;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Taux de completion */
.rate-excellent {
  color: #10b981;
  font-weight: 600;
}

.rate-good {
  color: #f59e0b;
  font-weight: 600;
}

.rate-poor {
  color: #ef4444;
  font-weight: 600;
}

/* Barre de progression */
.progress-bar {
  position: relative;
  background: #f3f4f6;
  border-radius: 0.5rem;
  height: 1.5rem;
  overflow: hidden;
  display: flex;
  align-items: center;
  min-width: 100px;
}

.progress-fill {
  background: linear-gradient(90deg, #10b981, #059669);
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 0.5rem;
}

.progress-text {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #1f2937;
  z-index: 1;
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .tables-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .btn-refresh, .btn-export {
    flex: 1;
    justify-content: center;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card {
    padding: 1rem;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .tables-grid {
    grid-template-columns: 1fr;
  }
}
</style>