<template>
  <div :class="styles.todoList">
    <!-- En-tête avec titre et actions principales -->
    <div :class="styles.todoListHeader">
      <div :class="styles.titleSection">
        <h2>{{ todolist.name }}</h2>
        <span :class="styles.todoCount">{{ todos.length }} tâche(s)</span>
      </div>

      <div :class="styles.mainActions">
        <button @click="toggleAddForm" :class="styles.btnAdd">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg> 
          Nouvelle tâche
        </button>

        <!-- Menu d'export avec dropdown -->
        <div :class="styles.exportDropdown">
          <button @click="toggleExportMenu" :class="[styles.btnExport, styles.btnExportMain]"
            :disabled="todos.length === 0">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="m9 13.5 3 3m0 0 3-3m-3 3v-6m1.06-4.19-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z" />
            </svg>
            Export
            <span :class="[styles.dropdownIcon, { [styles.dropdownOpen]: showExportMenu }]">▼</span>
          </button>

          <!-- Menu dropdown -->
          <div v-if="showExportMenu" :class="styles.exportMenu">
            <button @click="handleExport('all')" :class="styles.exportMenuItem">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M7.5 7.5h-.75A2.25 2.25 0 0 0 4.5 9.75v7.5a2.25 2.25 0 0 0 2.25 2.25h7.5a2.25 2.25 0 0 0 2.25-2.25v-7.5a2.25 2.25 0 0 0-2.25-2.25h-.75m-6 3.75 3 3m0 0 3-3m-3 3V1.5m6 9h.75a2.25 2.25 0 0 1 2.25 2.25v7.5a2.25 2.25 0 0 1-2.25 2.25h-7.5a2.25 2.25 0 0 1-2.25-2.25v-.75" />
              </svg>
              Export complet
            </button>

            <button @click="handleExport('pending')" :class="styles.exportMenuItem"
              :disabled="todos.filter(t => !t.completed).length === 0">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              Todos en cours
            </button>

            <button @click="handleExport('completed')" :class="styles.exportMenuItem"
              :disabled="todos.filter(t => t.completed).length === 0">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              Todos terminés
            </button>

            <button @click="handleExport('alphabetical')" :class="styles.exportMenuItem">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75" />
              </svg>
              Export alphabétique
            </button>

            <button @click="handleExport('custom')" :class="styles.exportMenuItem">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
              Export personnalisé
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 🎯 NOUVEAU : Formulaire simple avec priorité -->
    <div v-if="showAddForm" :class="styles.addTodoForm">
      <div :class="styles.formRow">
        <!-- Champ nom principal -->
        <input 
          ref="todoInputRef" 
          v-model="newTodoName" 
          type="text" 
          placeholder="Nom de la tâche..." 
          :class="styles.todoInput" 
          @keydown.enter="addTodo"
          @keydown.escape="cancelAdd" 
          maxlength="200"
          required
        />
        
        <!-- Champ priorité compact -->
        <input
          v-model.number="customPriority"
          type="number"
          min="1"
          max="999"
          placeholder="Priorité"
          :class="styles.priorityInput"
          title="Priorité optionnelle (ex: 1 = urgent)"
          @keydown.enter="addTodo"
          @keydown.escape="cancelAdd"
        />
        
        <!-- Boutons d'action -->
        <button 
          @click="addTodo" 
          :disabled="!newTodoName.trim()"
          :class="styles.btnConfirm"
          title="Ajouter la tâche"
        >
          ✓
        </button>
        
        <button 
          @click="cancelAdd" 
          :class="styles.btnCancel"
          title="Annuler"
        >
          ✕
        </button>
      </div>
      
      <!-- Aide discrète -->
      <div :class="styles.formHint">
        💡 <strong>Astuce :</strong> Laissez la priorité vide pour ajouter en fin de liste, ou indiquez un chiffre (1 = urgent).
      </div>
    </div>

    <!-- Instructions drag & drop -->
    <div v-if="todos.length > 1" :class="styles.dragHint">
      💡 <strong>Astuce :</strong> Glissez-déposez les todos pour les réorganiser !
    </div>

    <!-- Liste des todos avec drag & drop -->
    <div v-if="todos.length > 0" :class="styles.todosContainer">
      <div ref="sortableContainer" :class="styles.sortableList">
        <TodoItem v-for="todo in sortedTodos" :key="todo.id" :todo="todo" :data-id="todo.id"
          :class="styles.draggableItem" @toggle="handleToggle" @edit="handleEdit" @delete="handleDelete" />
      </div>
    </div>

    <!-- État vide -->
    <div v-else :class="styles.emptyState">
      <div :class="styles.emptyIcon">📝</div>
      <p><strong>Aucun todo dans cette liste</strong></p>
      <p>Cliquez sur "Ajouter" pour commencer !</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, onUpdated, nextTick, watch } from 'vue';
import Sortable from 'sortablejs';
import TodoItem from './TodoItem.vue';
import { useNotifications } from '@/composables/useNotifications';
import styles from '@/styles/components/TodoList.module.css';
import { useTodos } from '@/composables/useTodos';
import type { ExportOptions } from '@/types';
// 🎯 CORRECTION : Utiliser les types de l'API au lieu d'interfaces locales
import type { Todo, TodoList } from '@/services/api';

interface Props {
  todolist: TodoList;
  todos: Todo[];
}

interface Emits {
  addTodo: [name: string, priority?: number]; // 🎯 AJOUTÉ : Support de la priorité
  toggleTodo: [id: number];
  editTodo: [todo: Todo];
  deleteTodo: [id: number];
  reorderTodos: [todoIds: number[]];
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Notifications
const { saving, todoSaved, apiError } = useNotifications();

// Refs
const sortableContainer = ref<HTMLElement>();
const todoInputRef = ref<HTMLInputElement>();
let sortableInstance: Sortable | null = null;

// État local
const showAddForm = ref(false);
const newTodoName = ref('');
const customPriority = ref<number | null>(null); // 🎯 NOUVEAU : Priorité personnalisée
const showExportMenu = ref(false);

// 🎯 GESTION DU SCROLL - Refs existants
const lastScrollPosition = ref(0);
const currentlyModifying = ref<number | null>(null);
const shouldPreserveScroll = ref(false);

// Export functions
const { downloadTodoListWithOptions, exportPresets } = useTodos();

// 🎯 FONCTIONS DE GESTION DU SCROLL
const saveScrollPosition = () => {
  lastScrollPosition.value = window.pageYOffset || document.documentElement.scrollTop;
};

const restoreScrollPosition = () => {
  if (lastScrollPosition.value > 0) {
    setTimeout(() => {
      window.scrollTo({
        top: lastScrollPosition.value,
        behavior: 'instant'
      });
    }, 150);
  }
};

const scrollToTodo = (todoId: number, behavior: 'smooth' | 'instant' = 'smooth') => {
  setTimeout(() => {
    const todoElement = document.querySelector(`[data-id="${todoId}"]`);
    if (todoElement) {
      todoElement.scrollIntoView({
        behavior,
        block: 'center', // Centrer l'élément dans la vue
        inline: 'nearest'
      });
    } else {
      console.warn(`⚠️ Élément todo ${todoId} non trouvé pour scroll`);
    }
  }, 200);
};

const withScrollPreservation = async (todoId: number | null, operation: () => Promise<void>) => {
  try {
    // Sauvegarder la position
    if (!todoId) {
      saveScrollPosition();
      shouldPreserveScroll.value = true;
    } else {
      currentlyModifying.value = todoId;
      shouldPreserveScroll.value = false;
    }

    // Exécuter l'opération
    await operation();

    // Attendre que l'opération parent se termine
    await new Promise(resolve => setTimeout(resolve, 300));

    // Restaurer position ou scroller vers l'élément
    if (todoId && currentlyModifying.value === todoId) {
      scrollToTodo(todoId, 'instant');
    } else if (shouldPreserveScroll.value) {
      restoreScrollPosition();
    }

  } finally {
    currentlyModifying.value = null;
    shouldPreserveScroll.value = false;
  }
};

// Computed - todos triés par priorité
const sortedTodos = computed(() => {
  return [...props.todos].sort((a, b) => a.priority - b.priority);
});

// 🛡️ FONCTION DE DESTRUCTION SÉCURISÉE
const destroySortableInstance = () => {
  if (sortableInstance) {
    try {
      // Vérifier que l'élément existe encore avant de détruire
      if (sortableContainer.value && sortableInstance.el) {
        sortableInstance.destroy();
      } else {
        console.log('🧹 Sortable déjà détruit ou élément absent');
      }
    } catch (error: unknown) { // 🎯 CORRECTION : Type explicite
      console.warn('⚠️ Erreur lors de la destruction de Sortable:', error);
    } finally {
      sortableInstance = null;
    }
  }
};

// 🛡️ FONCTION D'INITIALISATION SÉCURISÉE
const initializeSortable = () => {
  // Détruire l'instance précédente de manière sécurisée
  destroySortableInstance();

  // Vérifier que l'élément existe et qu'il y a assez de todos
  if (!sortableContainer.value || props.todos.length <= 1) {
    console.log('🚫 Pas assez de todos pour Sortable ou élément manquant');
    return;
  }

  try {
    // Créer une nouvelle instance
    sortableInstance = new Sortable(sortableContainer.value, {
      animation: 200,
      ghostClass: styles.sortableGhost,
      chosenClass: styles.sortableChosen,
      dragClass: styles.sortableDrag,

      // Gérer le déplacement
      onEnd: async (evt) => {
        const { oldIndex, newIndex } = evt;

        if (oldIndex === newIndex || oldIndex === undefined || newIndex === undefined) {
          return;
        }

        await handleReorder(oldIndex, newIndex);
      },

      // Personnalisation
      handle: `.${styles.draggableItem}`,
      scroll: true,
      scrollSensitivity: 100,
      scrollSpeed: 20,
    });

  } catch (error: unknown) { // 🎯 CORRECTION : Type explicite
    console.error('❌ Erreur lors de la création de Sortable:', error);
    sortableInstance = null;
  }
};

// 🎯 WATCHERS POUR RÉINITIALISER SORTABLE ET GÉRER LE SCROLL
watch(() => props.todos.length, (newLength, oldLength) => {
  // Réinitialiser Sortable seulement si nécessaire
  nextTick(() => {
    if (newLength > 1 && !sortableInstance) {
      initializeSortable();
    } else if (newLength <= 1 && sortableInstance) {
      destroySortableInstance();
    }
  });
});

// 🎯 WATCHER POUR DÉTECTER LES MODIFICATIONS ET GÉRER LE SCROLL
watch(() => props.todos, (newTodos, oldTodos) => {
  if (oldTodos && currentlyModifying.value) {
    // Une todo spécifique est en cours de modification
    const modifiedTodo = newTodos.find(t => t.id === currentlyModifying.value);
    if (modifiedTodo) {
      scrollToTodo(currentlyModifying.value, 'instant');
    }
  } else if (oldTodos && shouldPreserveScroll.value) {
    // Préserver la position de scroll pour les autres opérations
    restoreScrollPosition();
  }
}, { deep: true, flush: 'post' });

// 🎯 Toggle export menu
const toggleExportMenu = () => {
  showExportMenu.value = !showExportMenu.value;
};

// 🎯 Fermer le menu d'export au clic extérieur
const closeExportMenu = () => {
  showExportMenu.value = false;
};

// 🎯 Gestionnaire d'export unifié
const handleExport = async (type: string) => {
  closeExportMenu();

  try {
    switch (type) {
      case 'all':
        await exportPresets.all(props.todolist, props.todos);
        break;
      case 'pending':
        await exportPresets.pendingOnly(props.todolist, props.todos);
        break;
      case 'completed':
        await exportPresets.completedOnly(props.todolist, props.todos);
        break;
      case 'alphabetical':
        await exportPresets.alphabetical(props.todolist, props.todos);
        break;
      case 'custom':
        await exportWithOptions();
        break;
    }
  } catch (error: unknown) { // 🎯 CORRECTION : Type explicite
    console.error('Erreur export:', error);
    apiError('Erreur lors de l\'export');
  }
};

// 🎯 Export avec options personnalisées
const exportWithOptions = async () => {
  const options: ExportOptions = {
    includeMetadata: true,
    includeCompleted: true,
    includePending: true,
    sortBy: 'name',
    format: 'pretty'
  };

  await downloadTodoListWithOptions(props.todolist, props.todos, options);
};

// 🎯 Fonction pour afficher le formulaire et focus l'input
const toggleAddForm = async () => {
  showAddForm.value = !showAddForm.value;

  if (showAddForm.value) {
    // Fermer le menu d'export s'il est ouvert
    closeExportMenu();

    // Attendre que le DOM soit mis à jour
    await nextTick();
    // Mettre le focus sur l'input
    todoInputRef.value?.focus();
  } else {
    // Réinitialiser les champs si on ferme le formulaire
    newTodoName.value = '';
    customPriority.value = null; // 🎯 NOUVEAU : Reset priorité
  }
};

// 🎯 NOUVEAU : Ajouter un todo avec priorité optionnelle
const addTodo = async () => {
  const todoName = newTodoName.value.trim();

  if (!todoName) {
    // Si vide, juste remettre le focus
    todoInputRef.value?.focus();
    return;
  }

  try {
    // Sauvegarder la position de scroll avant ajout
    saveScrollPosition();
    shouldPreserveScroll.value = true;

    // 🎯 NOUVEAU : Récupérer la priorité personnalisée
    const priority = customPriority.value && customPriority.value > 0 ? customPriority.value : undefined;

    console.log('📝 [TodoList] Ajout todo avec priorité:', { name: todoName, priority });

    // Émettre l'événement vers le parent avec la priorité
    emit('addTodo', todoName, priority);

    // Réinitialiser et garder le focus pour ajouter rapidement
    newTodoName.value = '';
    customPriority.value = null; // 🎯 NOUVEAU : Reset priorité
    await nextTick();
    todoInputRef.value?.focus();

    // Réinitialiser Sortable après ajout avec sécurité
    await nextTick();
    if (sortableContainer.value) {
      initializeSortable();
    }

  } catch (error: unknown) { // 🎯 CORRECTION : Type explicite
    console.error('Erreur ajout todo:', error);
    // Remettre le focus même en cas d'erreur
    await nextTick();
    todoInputRef.value?.focus();
  }
};

// 🎯 Annuler l'ajout
const cancelAdd = () => {
  showAddForm.value = false;
  newTodoName.value = '';
  customPriority.value = null; // 🎯 NOUVEAU : Reset priorité
};

// Gérer la réorganisation avec préservation du scroll
const handleReorder = async (oldIndex: number, newIndex: number) => {
  // Identifier la todo qui a été déplacée
  const movedTodo = sortedTodos.value[oldIndex];
  if (movedTodo) {
    currentlyModifying.value = movedTodo.id;
    console.log(`🔀 Réorganisation: todo ${movedTodo.id} de ${oldIndex} vers ${newIndex}`);
  }

  // Afficher notification de sauvegarde
  const savingId = saving();

  try {
    // Créer le nouvel ordre
    const reorderedTodos = [...sortedTodos.value];
    const [movedTodoItem] = reorderedTodos.splice(oldIndex, 1);
    reorderedTodos.splice(newIndex, 0, movedTodoItem);

    // Extraire les IDs dans le bon ordre
    const newOrder = reorderedTodos.map(todo => todo.id);

    // Émettre l'événement
    emit('reorderTodos', newOrder);

    // Notification de succès
    setTimeout(() => {
      todoSaved();
    }, 500);

    // Scroller vers la todo déplacée après un délai
    if (movedTodo) {
      setTimeout(() => {
        scrollToTodo(movedTodo.id, 'smooth');
        currentlyModifying.value = null;
      }, 600);
    }

  } catch (error: unknown) { // 🎯 CORRECTION : Type explicite
    console.error('Erreur lors de la réorganisation:', error);
    apiError('Impossible de sauvegarder l\'ordre des todos');
    currentlyModifying.value = null;
  }
};

// 🛡️ GESTIONNAIRES D'ÉVÉNEMENTS AVEC PRÉSERVATION DU SCROLL
const handleToggle = async (id: number) => {
  await withScrollPreservation(id, async () => {
    emit('toggleTodo', id);
  });

  // Réinitialiser Sortable après toggle avec sécurité
  setTimeout(() => {
    if (sortableContainer.value) {
      initializeSortable();
    }
  }, 400);
};

const handleEdit = (todo: Todo) => {
  // Sauvegarder position pour l'édition
  saveScrollPosition();
  emit('editTodo', todo);
};

const handleDelete = async (id: number) => {
  await withScrollPreservation(null, async () => {
    emit('deleteTodo', id);
  });

  // Réinitialiser Sortable après suppression avec sécurité
  setTimeout(() => {
    if (sortableContainer.value) {
      initializeSortable();
    }
  }, 400);
};

// Initialiser Sortable après le montage
onMounted(async () => {
  await nextTick();
  initializeSortable();

  // Fermer le menu d'export au clic extérieur
  document.addEventListener('click', (event: Event) => { // 🎯 CORRECTION : Type explicite
    const target = event.target as Element;
    if (!target.closest(`.${styles.exportDropdown}`)) {
      closeExportMenu();
    }
  });
});

// 🛡️ DESTRUCTION SÉCURISÉE lors des mises à jour
onUpdated(() => {
  // Si l'élément container n'existe plus, nettoyer Sortable
  if (!sortableContainer.value && sortableInstance) {
    console.log('🧹 Élément container supprimé, nettoyage de Sortable...');
    destroySortableInstance();
  }
});

// 🛡️ DESTRUCTION SÉCURISÉE lors du démontage
onBeforeUnmount(() => {
  destroySortableInstance();
});
</script>