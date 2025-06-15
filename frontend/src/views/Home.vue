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

    <!-- Formulaire de création -->
    <div v-if="showCreateForm" :class="styles.createForm">
      <input v-model="newTodoListName" type="text" placeholder="Nom de la TodoList..."
        @keyup.enter="handleCreateTodoList" :class="styles.nameInput" />
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
      <div v-for="todolist in todolists" :key="todolist.id" :class="styles.todolistCard"
        @click="goToTodoList(todolist.id)">
        <div :class="styles.cardHeader">
          <h3>{{ todolist.name }}</h3>
          <button @click.stop="handleDeleteTodoList(todolist.id)" :class="styles.btnDelete"
            title="Supprimer cette TodoList">
            🗑️
          </button>
        </div>

        <div :class="styles.cardInfo">
          <p>{{ todolist.todos?.length || 0 }} todo(s)</p>
          <p>Cliquez pour ouvrir →</p>
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTodos } from '@/composables/useTodos';
import styles from '@/styles/views/Home.module.css';

const router = useRouter();

const {
  todolists,
  loading,
  error,
  loadTodoLists,
  createTodoList,
  deleteTodoList,
  clearError,
  testConnection
} = useTodos();

// État local
const showCreateForm = ref(false);
const newTodoListName = ref('');

// Charger les TodoLists au montage
onMounted(() => {
  loadTodoLists();
});

// Actions
const handleCreateTodoList = async () => {
  if (!newTodoListName.value.trim()) return;

  try {
    const newTodoList = await createTodoList(newTodoListName.value.trim());
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

const goToTodoList = (id: number) => {
  router.push(`/todolist/${id}`);
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