<template>
  <div class="container">
    <!-- Header de la page -->
    <!-- Header de la page -->
    <div :class="styles.pageHeader">
      <div>
        <h1>Mes TodoLists</h1>
        <p>Gérez vos tâches et analysez votre productivité</p>
      </div>
      <div :class="styles.headerActions">
        <router-link to="/statistics" :class="styles.btnStats">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
          </svg>Voir les statistiques
        </router-link>

        <button @click="showCreateForm = !showCreateForm" :class="styles.btnCreate">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Nouvelle TodoList
        </button>
      </div>
    </div>

<!-- ✨ BARRE DE RECHERCHE COMPACTE -->
<div :class="styles.searchBar">
  <div :class="styles.searchInputWrapper">
    <svg :class="styles.searchIcon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
    </svg>
    <input 
      v-model="searchTerm" 
      type="text" 
      placeholder="Rechercher..." 
      :class="styles.searchInput"
    />
    <button 
      v-if="searchTerm.length > 0" 
      @click="searchTerm = ''"
      :class="styles.clearButton"
      title="Effacer"
    >
      ×
    </button>
  </div>
</div>

<!-- 🎯 RÉSULTATS DE RECHERCHE COMPACTS -->
<div v-if="searchTerm.length >= 2" :class="styles.searchResults">
  <div :class="styles.searchHeader">
    <span :class="styles.searchTitle">{{ totalMatchingTodos }} résultat(s) dans {{ todoListsWithMatches.length }} liste(s)</span>
  </div>

  <div v-if="todoListsWithMatches.length === 0" :class="styles.noResults">
    <span>🤷‍♀️ Aucun résultat</span>
  </div>

  <div v-else :class="styles.searchResultsList">
    <div 
      v-for="result in todoListsWithMatches" 
      :key="result.todolist.id"
      :class="styles.searchResultCard"
      @click="goToTodoList(result.todolist.id)"
    >
      <!-- En-tête compact -->
      <div :class="styles.resultHeader">
        <span :class="styles.resultTitle">{{ result.todolist.name }}</span>
        <span v-if="result.todolist.category" :class="styles.resultCategoryBadge">
          {{ getCategoryIcon(result.todolist.category.icon) }} {{ result.todolist.category.name }}
        </span>
        <span :class="styles.resultCount">{{ result.matchingTodos.length }}</span>
      </div>

      <!-- Liste compacte des todos trouvés -->
      <div :class="styles.resultTodos">
        <span 
          v-for="todo in result.matchingTodos.slice(0, 3)" 
          :key="todo.id"
          :class="[styles.resultTodo, { [styles.completed]: todo.completed }]"
        >
          {{ todo.completed ? '✓' : '•' }} <span v-html="highlightMatch(todo.name)"></span>
        </span>
        <span v-if="result.matchingTodos.length > 3" :class="styles.moreResults">
          +{{ result.matchingTodos.length - 3 }} autres...
        </span>
      </div>
    </div>
  </div>
</div>
    <!-- Formulaire de création -->
    <div v-if="showCreateForm" :class="styles.createForm">
      <input v-model="newTodoListName" type="text" placeholder="Nom de la TodoList..."
        @keyup.enter="handleCreateTodoList" :class="styles.nameInput" />
      <select id="category-select" v-model="selectedCategoryId" :class="styles.categorySelect">
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ getCategoryIcon(category.icon) }} {{ category.name }}
        </option>
      </select>
      <button @click="handleCreateTodoList" :class="styles.btnConfirm">
        Créer
      </button>
      <button @click="cancelCreate" :class="styles.btnCancel">
        Annuler
      </button>
    </div>

    <!-- État de chargement -->
    <div v-if="loading" :class="styles.loading">
      <div :class="styles.spinner">⏳</div>
      <p>Chargement des TodoLists...</p>
    </div>

    <!-- Affichage des erreurs -->
    <div v-if="error" :class="styles.error">
      <p>❌ {{ error }}</p>
      <button @click="clearError" :class="styles.btnDismiss">Fermer</button>
    </div>

    <!-- Liste des TodoLists -->
    <div v-if="!loading && todolists.length > 0" :class="styles.todolistsGrid">

      <div v-for="todolist in todolists" :key="todolist.id" :class="[
        styles.todolistCard,
        todolist.category ? styles.todolistCardWithCategory : styles.todolistCardDefault
      ]" :style="todolist.category ? {
        '--category-color': todolist.category.color,
        '--category-color-light': todolist.category.color + '15',
        '--category-color-hover': todolist.category.color + '25'
      } : {}" @click="goToTodoList(todolist.id)">

        <div :class="styles.cardHeader">
          <h3>{{ todolist.name }}</h3>
          <button @click.stop="handleDeleteTodoList(todolist.id)" :class="styles.btnDelete"
            title="Supprimer cette TodoList">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
          </button>
        </div>

        <div :class="styles.cardInfo">
          <p>{{ todolist.todos?.length || 0 }} todo(s)</p>
          <p>Cliquez pour ouvrir →</p>
        </div>

        <div v-if="todolist.category" :class="styles.categoryBadge">
          <span :class="styles.categoryIcon" :style="{ color: todolist.category.color }">
            {{ getCategoryIcon(todolist.category.icon) }}
          </span>
          <!-- <span :class="styles.categoryName">{{ todolist.category.name }}</span> -->
        </div>
        <div v-else :class="styles.noCategoryBadge">
          <span :class="styles.categoryIcon">📁</span>
          <span :class="styles.categoryName">Aucune catégorie</span>
        </div>
      </div>
    </div>



    <!-- État vide -->
    <div v-if="!loading && todolists.length === 0" :class="styles.emptyState">
      <div :class="styles.emptyIcon">📝</div>
      <h2>Aucune TodoList</h2>
      <p>Créez votre première TodoList pour commencer à organiser vos tâches !</p>
      <button @click="showCreateForm = true" :class="styles.btnCreateFirst">
        ➕ Créer ma première TodoList
      </button>
    </div>

    <!-- Test de connexion -->
    <div :class="styles.footer">
      <button @click="testApiConnection" :class="styles.btnTest">
        🔍 Tester la connexion API
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useTodos } from '@/composables/useTodos';
import styles from '@/styles/views/Home.module.css';
import { getCategoryIcon } from '@/composables/useCategory';
import { categoriesApi } from '@/services/api';
import type { TodoList, Category } from '@/services/api';
const router = useRouter();


const {
  todolists,
  loading,
  error,
  loadTodoLists,
  createTodoList,
  deleteTodoList,
  clearError,
  testConnection, 
  loadAllTodos, 
  allTodos
} = useTodos();


// État local
const showCreateForm = ref(false);
const newTodoListName = ref('');
const searchTerm = ref('');

const categories = ref<Category[]>([]);
const selectedCategoryId = ref<number | ''>('');

const saving = ref(false);
// Charger les TodoLists au montage
onMounted(() => {
  loadTodoLists();
  loadAllTodos();
});


// Actions
const handleCreateTodoList = async () => {
  if (!newTodoListName.value.trim()) return;
  if (!selectedCategoryId.value) return;

  try {
    const newTodoList = await createTodoList(newTodoListName.value.trim(), selectedCategoryId.value);
    newTodoListName.value = '';
    showCreateForm.value = false;

    // Rediriger vers la nouvelle TodoList
    router.push(`/todolist/${newTodoList.id}`);
  } catch (err) {
    console.error('Erreur création TodoList:', err);
  }
};

const cancelCreate = () => {
  newTodoListName.value = '';
  showCreateForm.value = false;
};

const handleDeleteTodoList = async (id: number) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette TodoList ?')) {
    return;
  }

  try {
    await deleteTodoList(id);
  } catch (err) {
    console.error('Erreur suppression TodoList:', err);
  }
};

const loadCategories = async () => {
  loading.value = true;
  error.value = null;
  try {
    categories.value = await categoriesApi.getActive();

  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erreur lors du chargement des catégories';
    console.error('Erreur chargement catégories:', err);
  } finally {
    loading.value = false;
  }
};

const goToTodoList = (id: number) => {
  router.push(`/todolist/${id}`);
};
// Lifecycle
onMounted(() => {
  loadCategories();
});

const filteredTodos = computed(() => {
  if (!searchTerm.value || searchTerm.value.length < 2) {
    return [];
  }
  return allTodos.value.filter(todo => {
    // Vérification de sécurité pour éviter les erreurs
    const todoName = todo.name || '';
    return todoName.toLowerCase().includes(searchTerm.value.toLowerCase());
  });
});

const todoListsWithMatches = computed(() => {
  if (!searchTerm.value || searchTerm.value.length < 2) {
    return [];
  }

  const searchQuery = searchTerm.value.toLowerCase();
  const results: { todolist: TodoList; matchingTodos: any[] }[] = [];

  // Grouper les todos par TodoList
  const todosByList = new Map();
  
  allTodos.value.forEach(todo => {
    if (!todo.todolist) return;
    
    const listId = todo.todolist.id;
    if (!todosByList.has(listId)) {
      todosByList.set(listId, {
        todolist: todo.todolist,
        matchingTodos: []
      });
    }
    
    // Vérifier si le todo correspond à la recherche
    if (todo.name && todo.name.toLowerCase().includes(searchQuery)) {
      todosByList.get(listId).matchingTodos.push(todo);
    }
  });

  // Convertir en array et filtrer les listes sans résultats
  todosByList.forEach((listData, listId) => {
    if (listData.matchingTodos.length > 0) {
      // Trier les todos par priorité
      listData.matchingTodos.sort((a: any, b: any) => a.priority - b.priority);
      results.push(listData);
    }
  });

  // Trier les TodoLists par nombre de résultats (plus de résultats en premier)
  return results.sort((a, b) => b.matchingTodos.length - a.matchingTodos.length);
});

const totalMatchingTodos = computed(() => {
  return todoListsWithMatches.value.reduce((total, result) => 
    total + result.matchingTodos.length, 0
  );
});

// ✨ FONCTION POUR SURLIGNER LES CORRESPONDANCES
const highlightMatch = (text: string) => {
  if (!searchTerm.value || searchTerm.value.length < 2) {
    return text;
  }
  
  const query = searchTerm.value.toLowerCase();
  const lowerText = text.toLowerCase();
  const index = lowerText.indexOf(query);
  
  if (index === -1) {
    return text;
  }
  
  return text.substring(0, index) + 
         '<mark class="search-highlight">' + 
         text.substring(index, index + query.length) + 
         '</mark>' + 
         text.substring(index + query.length);
};

const testApiConnection = async () => {
  const isConnected = await testConnection();
  if (isConnected) {
    alert('✅ Connexion API réussie !');
  } else {
    alert('❌ Erreur de connexion API. Vérifiez que le backend est lancé.');
  }
};
</script>