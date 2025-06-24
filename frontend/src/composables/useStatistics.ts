import { ref, computed } from 'vue';
import { todoListsApi } from '../services/api';
import type { Todo, TodoList } from '../services/api';

type TodoWithList = Omit<Todo, 'todolist'> & {
  todolist?: TodoList;
};

interface DayStats {
  date: string;
  completed: number;
  created: number;
  total: number;
}

interface PriorityStats {
  priority: number;
  count: number;
  completed: number;
  percentage: number;
}

interface TodoListStats {
  todolist: TodoList;
  totalTodos: number;
  completedTodos: number;
  completionRate: number;
  avgPriority: number;
}

interface ProductivityStats {
  todayCompleted: number;
  weekCompleted: number;
  monthCompleted: number;
  todayCreated: number;
  bestDay: { date: string; completed: number };
  streak: number;
}

const allTodos = ref<TodoWithList[]>([]);
const allTodoLists = ref<TodoList[]>([]);
const loading = ref(false);

export function useStatistics() {
  
  // Charger toutes les données pour les statistiques
  const loadAllData = async () => {
    loading.value = true;
    try {
      // Charger toutes les todolists
      allTodoLists.value = await todoListsApi.getAll();
      
      // Charger tous les todos
      const allTodosData: TodoWithList[] = [];
      
      for (const todolist of allTodoLists.value) {
        const todos = await todoListsApi.getTodos(todolist.id);
        const todosWithList = todos.map(todo => ({
          ...todo,
          todolist
        }));
        allTodosData.push(...todosWithList);
      }
      
      allTodos.value = allTodosData;
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      loading.value = false;
    }
  };

  // Statistiques générales
  const generalStats = computed(() => {
    const total = allTodos.value.length;
    const completed = allTodos.value.filter(t => t.completed).length;
    const pending = total - completed;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    const avgPriority = total > 0 
      ? Math.round(allTodos.value.reduce((sum, t) => sum + t.priority, 0) / total * 10) / 10
      : 0;

    return {
      total,
      completed,
      pending,
      completionRate,
      avgPriority,
      totalLists: allTodoLists.value.length
    };
  });

  // Statistiques par priorité
  const priorityStats = computed((): PriorityStats[] => {
    const priorities = new Map<number, { total: number; completed: number }>();
    
    allTodos.value.forEach(todo => {
      const priority = todo.priority;
      if (!priorities.has(priority)) {
        priorities.set(priority, { total: 0, completed: 0 });
      }
      
      const stats = priorities.get(priority)!;
      stats.total++;
      if (todo.completed) stats.completed++;
    });

    return Array.from(priorities.entries())
      .map(([priority, stats]) => ({
        priority,
        count: stats.total,
        completed: stats.completed,
        percentage: Math.round((stats.completed / stats.total) * 100)
      }))
      .sort((a, b) => a.priority - b.priority);
  });

  // Statistiques par TodoList
  const todoListStats = computed((): TodoListStats[] => {
    return allTodoLists.value.map(todolist => {
      const todos = allTodos.value.filter(t => t.todolist?.id === todolist.id);
      const completed = todos.filter(t => t.completed).length;
      const total = todos.length;
      const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
      const avgPriority = total > 0 
        ? Math.round(todos.reduce((sum, t) => sum + t.priority, 0) / total * 10) / 10
        : 0;

      return {
        todolist,
        totalTodos: total,
        completedTodos: completed,
        completionRate,
        avgPriority
      };
    }).sort((a, b) => b.completionRate - a.completionRate);
  });

  // Statistiques temporelles (simulées - dans la vraie vie on aurait des timestamps)
  const timeStats = computed((): DayStats[] => {
    // Simulation de données sur 7 jours
    const days = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Simulation basée sur les données existantes
      const totalTodos = allTodos.value.length;
      const completedTodos = allTodos.value.filter(t => t.completed).length;
      
      // Distribution simulée sur 7 jours
      const dayFactor = Math.random() * 0.5 + 0.5; // 0.5 à 1
      const completed = Math.round((completedTodos / 7) * dayFactor);
      const created = Math.round((totalTodos / 7) * dayFactor);
      
      days.push({
        date: date.toISOString().split('T')[0],
        completed,
        created,
        total: allTodos.value.length
      });
    }
    
    return days;
  });

  // Statistiques de productivité
  const productivityStats = computed((): ProductivityStats => {
    const timeData = timeStats.value;
    const today = timeData[timeData.length - 1];
    const thisWeek = timeData.slice(-7);
    
    const weekCompleted = thisWeek.reduce((sum, day) => sum + day.completed, 0);
    const monthCompleted = Math.round(weekCompleted * 4.3); // Estimation mensuelle
    
    const bestDay = timeData.reduce((best, day) => 
      day.completed > best.completed ? day : best, timeData[0]);

    // Simulation d'une streak
    let streak = 0;
    for (let i = timeData.length - 1; i >= 0; i--) {
      if (timeData[i].completed > 0) {
        streak++;
      } else {
        break;
      }
    }

    return {
      todayCompleted: today?.completed || 0,
      weekCompleted,
      monthCompleted,
      todayCreated: today?.created || 0,
      bestDay: {
        date: bestDay.date,
        completed: bestDay.completed
      },
      streak
    };
  });

  // Données pour les graphiques
  const chartData = computed(() => {
    return {
      // Graphique temporel (ligne)
      timeChart: {
        labels: timeStats.value.map(d => {
          const date = new Date(d.date);
          return date.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' });
        }),
        datasets: [
          {
            label: 'Todos complétés',
            data: timeStats.value.map(d => d.completed),
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: 'Todos créés',
            data: timeStats.value.map(d => d.created),
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      },

      // Graphique priorités (barres)
      priorityChart: {
        labels: priorityStats.value.map(p => `Priorité ${p.priority}`),
        datasets: [
          {
            label: 'Total',
            data: priorityStats.value.map(p => p.count),
            backgroundColor: 'rgba(99, 102, 241, 0.8)',
            borderColor: '#6366f1',
            borderWidth: 1
          },
          {
            label: 'Complétés',
            data: priorityStats.value.map(p => p.completed),
            backgroundColor: 'rgba(16, 185, 129, 0.8)',
            borderColor: '#10b981',
            borderWidth: 1
          }
        ]
      },

      // Graphique completion rate (doughnut)
      completionChart: {
        labels: ['Complétés', 'En cours'],
        datasets: [{
          data: [generalStats.value.completed, generalStats.value.pending],
          backgroundColor: [
            'rgba(16, 185, 129, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderColor: [
            '#10b981',
            '#ef4444'
          ],
          borderWidth: 2
        }]
      },

      // Graphique par TodoList (barres horizontales)
      todoListChart: {
        labels: todoListStats.value.map(tl => tl.todolist.name),
        datasets: [{
          label: 'Taux de completion (%)',
          data: todoListStats.value.map(tl => tl.completionRate),
          backgroundColor: todoListStats.value.map(tl => 
            tl.completionRate >= 80 ? 'rgba(16, 185, 129, 0.8)' :
            tl.completionRate >= 50 ? 'rgba(245, 158, 11, 0.8)' :
            'rgba(239, 68, 68, 0.8)'
          ),
          borderWidth: 1
        }]
      }
    };
  });

  // Export des données pour d'autres usages
  const exportStats = () => {
    const stats = {
      general: generalStats.value,
      priority: priorityStats.value,
      todoLists: todoListStats.value,
      productivity: productivityStats.value,
      timeData: timeStats.value,
      exportDate: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(stats, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `todo-stats-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return {
    // État
    allTodos,
    allTodoLists,
    loading,
    
    // Actions
    loadAllData,
    exportStats,
    
    // Statistiques calculées
    generalStats,
    priorityStats,
    todoListStats,
    timeStats,
    productivityStats,
    chartData
  };
}
