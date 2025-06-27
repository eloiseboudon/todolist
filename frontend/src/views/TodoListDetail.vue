<template>
  <div :class="styles.container">
    <!-- Bouton retour stylisé -->
    <div :class="styles.backButton">
      <router-link to="/" :class="styles.btnBack">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
          stroke="currentColor">
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
      <TodoList :todolist="currentTodolist" :todos="sortedTodos" @addTodo="handleAddTodoWithPriority"
        @toggleTodo="handleToggleTodo" @editTodo="handleEditTodo" @deleteTodo="handleDeleteTodo"
        @reorderTodos="handleReorderTodos" @categoryUpdated="handleCategoryUpdated" />

      <div
        v-if="currentTodolist.category && currentTodolist.category.name.toLowerCase() === 'recette' && courseLists.length"
        :class="styles.addToCourses">
        <label for="courseSelect">Ajouter aux courses :</label>
        <select id="courseSelect" v-model="selectedCourseId">
          <option :value="null" disabled>Choisir une liste</option>
          <option v-for="list in courseLists" :key="list.id" :value="list.id">
            {{ list.name }}
          </option>
        </select>
        <button @click="handleAddToCourse" :disabled="!selectedCourseId">Ajouter</button>
      </div>

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
    <div :class="styles.link">
      <!-- à variabiliser pour les autres catégories que les recettes -->
      <h2>👨‍🍳 Recettes associées</h2>
      <div v-if="currentLinks?.length === 0" :class="styles.noLinks">
        <p>Aucun lien associé.</p>
      </div>

      <div v-else :class="styles.linksList">
        <p>Cliquez sur une recette pour la consulter.</p>
        <button
          v-if="currentTodolist?.category && currentTodolist.category.name.toLowerCase() === 'courses'"
          @click="handlePopulateFromLinks"
          :class="['btnCompact', 'btnSecondary', styles.addLinkButton]"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6m3.75-9a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm10.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
          </svg>
          Ajouter les éléments de la liste
        </button>
        <div :class="styles.linksContainer">
          <div v-for="link in currentLinks" :key="link.id" :class="[
            styles.todolistCard,
            link.category ? styles.todolistCardWithCategory : styles.todolistCardDefault
          ]" :style="link.category ? {
          '--category-color': link.category.color,
          '--category-color-light': link.category.color + '15',
          '--category-color-hover': link.category.color + '25'
        } : {}" @click="goToTodoList(link.id)">
            <div :class="styles.cardHeader">
              <h3>{{ link.name }}</h3>
            </div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import TodoList from '@/components/TodoList.vue';
import { useTodos } from '@/composables/useTodos';
import type { Todo, TodoList as TodoListType } from '@/services/api';
import styles from '@/styles/views/TodoListDetail.module.css';

const router = useRouter();

interface Props {
  id: string;
}

const props = defineProps<Props>();

const {
  todolists,
  currentTodolist,
  currentTodos,
  currentLinks,
  sortedTodos,
  completedTodos,
  pendingTodos,
  loading,
  error,
  loadTodoList,
  loadTodoLists,
  loadTodoListLinks,
  addTodo,
  toggleTodo,
  updateTodo,
  deleteTodo,
  reorderTodos,
  addLinkBetweenTodolist,
  populateFromLinks,
  clearError
} = useTodos();

// Charger les données au montage et quand l'ID change
onMounted(() => {
  loadTodoList(parseInt(props.id));
  loadTodoLists();
  loadTodoListLinks(parseInt(props.id));
});

watch(() => props.id, (newId) => {
  loadTodoList(parseInt(newId));
});
const goToTodoList = (id: number) => {
  router.push(`/todolist/${id}`);
};

const selectedCourseId = ref<number | null>(null);
const courseLists = computed(() => {
  return todolists.value.filter(
    (t) => t.category && t.category.name.toLowerCase() === 'courses'
  );
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

const handleAddToCourse = async () => {
  if (!selectedCourseId.value) return;
  try {
    await addLinkBetweenTodolist(parseInt(props.id), selectedCourseId.value);
  } catch (err) {
    console.error('Erreur ajout aux courses:', err);
  }
};

const handlePopulateFromLinks = async () => {
  try {
    await populateFromLinks(parseInt(props.id));
  } catch (err) {
    console.error('Erreur population courses:', err);
  }
};

const retry = () => {
  clearError();
  loadTodoList(parseInt(props.id));
};
</script>