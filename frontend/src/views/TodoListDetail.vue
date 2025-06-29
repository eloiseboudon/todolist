<template>
  <div :class="styles.container">

    <BackButton v-if="route.name && route.name !== 'Home'" />

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

      <div :class="[styles.addToLink, 'divcontainer']">
        <label for="linkSelect">Ajouter à la todolist :</label>
        <select id="linkSelect" v-model="selectedListId">
          <option :value="null" disabled>Choisir une liste</option>
          <option v-for="list in todolists" :key="list.id" :value="list.id">
            {{ list.name }}
          </option>
        </select>
        <button @click="handleAddToLink" :disabled="!selectedListId">Ajouter</button>
      </div>



      <!-- LIENS VERS LES TODOLISTS ASSOCIÉES -->
      <div :class="[styles.link, 'divcontainer']">
        <h2>📝 Todolist associées</h2>
        <div v-if="currentLinks?.length === 0" :class="styles.noLinks">
          <p>Aucun lien associé.</p>
        </div>

        <div v-else :class="styles.linksList">
          <p>Cliquez sur une todolist pour la consulter.</p>
          <button @click="handlePopulateFromLinks" :class="['btnCompact', 'btnSecondary', styles.addLinkButton]">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
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


      <!-- 🎯 STATISTIQUES STYLISÉES EN CARRÉS -->
      <div :class="[styles.stats, 'divcontainer']">
        <!-- <div :class="styles.stats"> -->
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
import { onMounted, watch, ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import TodoList from '@/components/TodoList.vue';
import { useTodos } from '@/composables/useTodos';
import type { Todo, TodoList as TodoListType } from '@/services/api';
import styles from '@/styles/views/TodoListDetail.module.css';
import BackButton from '@/components/BackButton.vue'

const router = useRouter();
const route = useRoute();

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

// Charger les données au montage 
onMounted(() => {
  loadTodoList(parseInt(props.id));
  loadTodoLists();
  loadTodoListLinks(parseInt(props.id));
  console.log(router.currentRoute.value);
});

// Charger les données quand l'ID change
watch(() => props.id, (newId) => {
  loadTodoList(parseInt(newId));
  loadTodoListLinks(parseInt(newId));
});

const goToTodoList = (id: number) => {
  router.push(`/todolist/${id}`);
};

const selectedListId = ref<number | null>(null);


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

const handleAddToLink = async () => {
  if (!selectedListId.value) return;
  try {
    await addLinkBetweenTodolist(parseInt(props.id), selectedListId.value);
  } catch (err) {
    console.error('Erreur de création de lien:', err);
  }
};

const handlePopulateFromLinks = async () => {
  try {
    await populateFromLinks(parseInt(props.id));
  } catch (err) {
    console.error('Erreur lien:', err);
  }
};

const retry = () => {
  clearError();
  loadTodoList(parseInt(props.id));
};
</script>