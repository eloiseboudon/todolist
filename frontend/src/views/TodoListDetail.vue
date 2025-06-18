<template>
  <div class="container">
    <!-- Bouton retour -->
    <div :class="styles.backButton">
      <router-link to="/" :class="styles.btnBack">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"
          class="size-6">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="m11.25 9-3 3m0 0 3 3m-3-3h7.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
        Retour
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

    <!-- Contenu principal -->
  <div v-if="!loading && currentTodolist" :class="styles.content">
      <!-- 🎯 MODIFIÉ : Ajout du paramètre priority dans l'événement -->
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
      <!-- Statistiques -->
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
import type { Todo,TodoList as TodoListType } from '@/services/api';
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

const handleAddTodoWithPriority = async (name: string, priority?: number) => {
  try {
    await addTodo(parseInt(props.id), name, priority);
  } catch (err) {
    console.error('Erreur ajout todo avec priorité - Détail complet:', err);
    if (err instanceof Error) {
      console.error('Message:', err.message);
      console.error('Stack:', err.stack);
    }
    console.error('Erreur complète:', JSON.stringify(err, null, 2));
  }
};

// Handlers
const handleAddTodo = async (name: string) => {
  try {
    await addTodo(parseInt(props.id), name);
  } catch (err) {
    console.error('Erreur ajout todo - Détail complet:', err);
    if (err instanceof Error) {
      console.error('Message:', err.message);
      console.error('Stack:', err.stack);
    }
    // Afficher l'objet complet
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

const handleEditTodo = async (todo: Todo) => {
  const newName = prompt('Nouveau nom:', todo.name);
  if (newName && newName.trim() !== todo.name) {
    try {
      await updateTodo(todo.id, {
        name: newName.trim(),
        completed: todo.completed,
        priority: todo.priority,
        todolist_id: parseInt(props.id)
      });
    } catch (err) {
      console.error('Erreur édition todo:', err);
    }
  }
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

const handleCategoryUpdated = async (updatedTodolist: TodoListType) => {
  console.log('📝 [TodoListDetail] Catégorie mise à jour, rechargement...');
  
  // Recharger la TodoList complète pour avoir les données à jour
  try {
    await loadTodoList(parseInt(props.id));
  } catch (err) {
    console.error('Erreur rechargement après mise à jour catégorie:', err);
  }
};

const retry = () => {
  clearError();
  loadTodoList(parseInt(props.id));
};
</script>