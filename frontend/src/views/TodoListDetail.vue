<template>
  <div :class="styles.container">
    <!-- Bouton retour stylisé -->
    <div :class="styles.backButton">
      <router-link to="/" :class="styles.btnBack">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="m11.25 9-3 3m0 0 3 3m-3-3h7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
        Retour à l'accueil
      </router-link>
    </div>

    <!-- État de chargement -->
    <div v-if="loading" :class="styles.loading">
      <div :class="styles.spinner">⏳</div>
      <p>Chargement de la TodoList...</p>
    </div>

    <!-- Affichage des erreurs -->
    <div v-if="error" :class="styles.error">
      <p>❌ {{ error }}</p>
      <button @click="clearError" :class="styles.btnDismiss">Fermer</button>
      <button @click="retry" :class="styles.btnRetry">Réessayer</button>
    </div>

    <!-- TodoList non trouvée -->
    <div v-if="!loading && !currentTodolist && !error" :class="styles.notFound">
      <h2>TodoList non trouvée</h2>
      <p>La TodoList avec l'ID {{ id }} n'existe pas.</p>
      <router-link to="/" :class="styles.btnBack">
        ← Retour à l'accueil
      </router-link>
    </div>

    <!-- 🎯 CONTENU PRINCIPAL AVEC LAYOUT AMÉLIORÉ -->
    <div v-if="!loading && currentTodolist" :class="styles.content">
      <!-- TodoList avec header compact et liste alignée -->
      <TodoList 
        :todolist="currentTodolist" 
        :todos="sortedTodos" 
        @addTodo="handleAddTodoWithPriority"
        @toggleTodo="handleToggleTodo"
        @editTodo="handleEditTodo" 
        @deleteTodo="handleDeleteTodo" 
        @reorderTodos="handleReorderTodos" 
        @categoryUpdated="handleCategoryUpdated"
      />
      
      <!-- 🎯 STATISTIQUES STYLISÉES EN CARRÉS -->
      <div :class="styles.stats">
        <div :class="styles.statCard">
          <span :class="styles.statNumber">{{ currentTodos.length }}</span>
          <span :class="styles.statLabel">Total</span>
        </div>
        
        <div :class="styles.statCard">
          <span :class="styles.statNumber">{{ completedTodos.length }}</span>
          <span :class="styles.statLabel">Terminées</span>
        </div>
        
        <div :class="styles.statCard">
          <span :class="styles.statNumber">{{ pendingTodos.length }}</span>
          <span :class="styles.statLabel">En cours</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import TodoList from '@/components/TodoList.vue';
import { useTodos } from '@/composables/useTodos';
import type { Todo, TodoList as TodoListType } from '@/services/api';
import styles from '@/styles/views/TodoListDetail.module.css';

interface Props {
  id: string;
}

const props = defineProps<Props>();

const {
  currentTodolist,
  currentTodos,
  sortedTodos,
  completedTodos,
  pendingTodos,
  loading,
  error,
  loadTodoList,
  addTodo,
  toggleTodo,
  updateTodo,
  deleteTodo,
  reorderTodos,
  clearError
} = useTodos();

// Charger les données au montage et quand l'ID change
onMounted(() => {
  loadTodoList(parseInt(props.id));
});

watch(() => props.id, (newId) => {
  loadTodoList(parseInt(newId));
});

const handleAddTodoWithPriority = async (
  name: string,
  priority?: number,
  quantity?: string,
) => {
  try {
    await addTodo(parseInt(props.id), name, priority, quantity);
  } catch (err) {
    console.error('Erreur ajout todo avec priorité - Détail complet:', err);
    if (err instanceof Error) {
      console.error('Message:', err.message);
      console.error('Stack:', err.stack);
    }
    console.error('Erreur complète:', JSON.stringify(err, null, 2));
  }
};

const handleToggleTodo = async (id: number) => {
  const todo = currentTodos.value.find(t => t.id === id);
  if (todo) {
    try {
      await toggleTodo(todo);
    } catch (err) {
      console.error('Erreur toggle todo:', err);
    }
  }
};

// 🎯 CORRIGÉ : Fonction handleEditTodo avec todolist_id
const handleEditTodo = async (todo: Todo) => {
  const newName = prompt('Nouveau nom:', todo.name);
  if (newName && newName.trim() !== todo.name) {
    try {
      await updateTodo(todo.id, {
        name: newName.trim(),
        completed: todo.completed,
        priority: todo.priority,
        todolist_id: parseInt(props.id) // 🎯 Ajout du todolist_id requis
      });
    } catch (err) {
      console.error('Erreur édition todo:', err);
    }
  }
};

// NOUVEAU : Gestionnaire de mise à jour de catégorie
const handleCategoryUpdated = (updatedTodolist: TodoListType) => {
  currentTodolist.value = updatedTodolist; // Direct et simple
};

const handleDeleteTodo = async (id: number) => {
  try {
    await deleteTodo(id);
  } catch (err) {
    console.error('🎯 [TodoListDetail] Erreur suppression todo:', err);
  }
};

const handleReorderTodos = async (todoIds: number[]) => {
  try {
    await reorderTodos(parseInt(props.id), todoIds);
  } catch (err) {
    console.error('Erreur réorganisation todos:', err);
  }
};

const retry = () => {
  clearError();
  loadTodoList(parseInt(props.id));
};
</script>