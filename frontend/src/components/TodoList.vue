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
                  d="M9 12h3.75M9 15h3.75M9 18h3.75m3-7.036A11.959 11.959 0 0 1 3.75 12M3.75 12A11.959 11.959 0 0 1 15.75 4.5h.75m0 0v4.5m0-4.5h-4.5" />
              </svg>
              Export complet
            </button>

            <button @click="handleExport('pending')" :class="styles.exportMenuItem">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              Tâches en cours
            </button>

            <button @click="handleExport('completed')" :class="styles.exportMenuItem">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                stroke="currentColor" class="size-6">
                <path stroke-linecap="round" stroke-linejoin="round"
                  d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              Tâches terminées
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

    <!-- 🎯 NOUVEAU : Utilisation du composant SimpleTodoForm amélioré -->
    <SimpleTodoForm 
      v-if="showAddForm"
      @add-todo="handleAddTodoWithPriority"
      @cancel="cancelAddTodo"
    />

    <!-- Instructions drag & drop -->
    <div v-if="todos.length > 1" :class="styles.dragHint">
      💡 <strong>Astuce :</strong> Glissez-déposez les todos pour les réorganiser !
    </div>

    <!-- 🎯 CORRIGÉ : Liste des todos avec drag & drop -->
    <div v-if="todos.length > 0" :class="styles.todosContainer">
      <div ref="sortableContainer" :class="styles.sortableList">
        <!-- 🎯 CORRECTION : Structure simplifiée pour le drag and drop -->
        <div 
          v-for="todo in sortedTodos" 
          :key="`todo-${todo.id}`" 
          :data-id="todo.id" 
          :class="styles.draggableItem"
        >
          <TodoItem 
            :todo="todo" 
            @toggle="handleToggle" 
            @edit="handleEdit" 
            @delete="handleDelete" 
          />
        </div>
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
import SimpleTodoForm from './SimpleTodoForm.vue';
import { useNotifications } from '@/composables/useNotifications';
import styles from '@/styles/components/TodoList.module.css';
import { useTodos } from '@/composables/useTodos';
import type { ExportOptions } from '@/types';
import type { Todo, TodoList } from '@/services/api';

interface Props {
  todolist: TodoList;
  todos: Todo[];
}

interface Emits {
  addTodo: [name: string, priority?: number];
  toggleTodo: [id: number];
  editTodo: [todo: Todo];
  deleteTodo: [id: number];
  reorderTodos: [todoIds: number[]];
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// État local
const showAddForm = ref(false);
const showExportMenu = ref(false);
const sortableContainer = ref<HTMLElement>();
let sortableInstance: Sortable | null = null;

// Notifications
const { 
  saving, 
  todoSaved, 
  todoAdded, 
  todoDeleted, 
  apiError,
  todolistDeleted 
} = useNotifications();

// État pour la gestion du scroll
const currentlyModifying = ref<number | null>(null);
const shouldPreserveScroll = ref(false);

// Fonctions de gestion du scroll
const saveScrollPosition = () => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('scrollPosition', window.pageYOffset.toString());
  }
};

const restoreScrollPosition = () => {
  if (typeof window !== 'undefined') {
    const position = sessionStorage.getItem('scrollPosition');
    if (position) {
      window.scrollTo(0, parseInt(position));
      sessionStorage.removeItem('scrollPosition');
    }
  }
};

const scrollToTodo = (todoId: number, behavior: ScrollBehavior = 'smooth') => {
  if (typeof window !== 'undefined') {
    const element = document.querySelector(`[data-id="${todoId}"]`);
    if (element) {
      element.scrollIntoView({ behavior, block: 'center' });
    }
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
      if (sortableContainer.value && sortableInstance.el) {
        sortableInstance.destroy();
      }
      console.log('🧹 Sortable détruit');
    } catch (error) {
      console.warn('⚠️ Erreur lors de la destruction de Sortable:', error);
    } finally {
      sortableInstance = null;
    }
  }
};

// 🛡️ FONCTION D'INITIALISATION CORRIGÉE
const initializeSortable = () => {
  // Détruire l'instance précédente
  destroySortableInstance();

  // Vérifier les conditions
  if (!sortableContainer.value || props.todos.length <= 1) {
    console.log('🚫 Conditions non remplies pour Sortable');
    return;
  }

  try {
    console.log('🎯 Initialisation de Sortable...');
    
    // 🎯 CORRECTION : Configuration simplifiée et corrigée
    sortableInstance = new Sortable(sortableContainer.value, {
      animation: 200,
      ghostClass: styles.sortableGhost,
      chosenClass: styles.sortableChosen,
      dragClass: styles.sortableDrag,
      
      // 🎯 CORRECTION : Supprimer ou corriger le handle
      // handle: `.${styles.draggableItem}`, // ❌ Peut causer des problèmes
      // Soit on l'enlève complètement, soit on utilise un selector plus spécifique
      
      // Options de scroll
      scroll: true,
      scrollSensitivity: 100,
      scrollSpeed: 20,
      
      // Gestionnaire principal
      onEnd: async (evt) => {
        try {
          console.log('🔄 Drag end event:', evt);
          const { oldIndex, newIndex } = evt;

          if (oldIndex === newIndex || oldIndex === undefined || newIndex === undefined) {
            console.log('🚫 Pas de changement d\'ordre');
            return;
          }

          console.log(`🎯 Réorganisation: ${oldIndex} → ${newIndex}`);
          await handleReorder(oldIndex, newIndex);
        } catch (error) {
          console.error('❌ Erreur lors du réordonnement:', error);
        }
      },
      
      // Événements de debug
      onStart: (evt) => {
        console.log('🎯 Début du drag:', evt.oldIndex);
      },
      
      onMove: (evt) => {
        // Optionnel : log des mouvements
        return true; // Autoriser le mouvement
      }
    });

    console.log('✅ Sortable initialisé avec succès');
  } catch (error) {
    console.error('❌ Erreur lors de la création de Sortable:', error);
    sortableInstance = null;
  }
};

// 🎯 WATCHERS POUR RÉINITIALISER SORTABLE
watch(() => props.todos.length, (newLength) => {
  console.log(`📊 Changement nombre de todos: ${newLength}`);
  nextTick(() => {
    if (newLength > 1 && !sortableInstance) {
      console.log('🔄 Réinitialisation de Sortable (ajout)');
      initializeSortable();
    } else if (newLength <= 1 && sortableInstance) {
      console.log('🧹 Destruction de Sortable (suppression)');
      destroySortableInstance();
    }
  });
});

// 🎯 Gestionnaires d'événements du menu
const toggleExportMenu = () => {
  showExportMenu.value = !showExportMenu.value;
};

const closeExportMenu = () => {
  showExportMenu.value = false;
};

// 🎯 Gestionnaire d'export
const handleExport = async (type: string) => {
  closeExportMenu();
  try {
    const { exportTodoListWithOptions, downloadTodoListWithOptions, exportPresets } = useTodos();
    
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
  } catch (error) {
    console.error('Erreur export:', error);
    apiError('Erreur lors de l\'export');
  }
};

const exportWithOptions = async () => {
  const { downloadTodoListWithOptions } = useTodos();
  const options: ExportOptions = {
    includeMetadata: true,
    includeCompleted: true,
    includePending: true,
    sortBy: 'name',
    format: 'pretty'
  };
  await downloadTodoListWithOptions(props.todolist, props.todos, options);
};

// 🎯 Gestion du formulaire
const toggleAddForm = () => {
  showAddForm.value = !showAddForm.value;
  if (showAddForm.value) {
    closeExportMenu();
  }
};

const cancelAddTodo = () => {
  showAddForm.value = false;
};

const handleAddTodoWithPriority = (name: string, priority?: number) => {
  console.log('📝 [TodoList] Ajout todo:', { name, priority });
  emit('addTodo', name, priority);
  showAddForm.value = false;
};

// 🎯 Gestionnaire de réorganisation
const handleReorder = async (oldIndex: number, newIndex: number) => {
  const movedTodo = sortedTodos.value[oldIndex];
  if (movedTodo) {
    currentlyModifying.value = movedTodo.id;
    console.log(`🔀 Todo déplacée: ${movedTodo.name} (${oldIndex} → ${newIndex})`);
  }

  const savingId = saving();

  try {
    // Créer le nouvel ordre
    const reorderedTodos = [...sortedTodos.value];
    const [movedTodoItem] = reorderedTodos.splice(oldIndex, 1);
    reorderedTodos.splice(newIndex, 0, movedTodoItem);

    // Extraire les IDs
    const newOrder = reorderedTodos.map(todo => todo.id);
    console.log('📋 Nouvel ordre:', newOrder);

    // Émettre l'événement
    emit('reorderTodos', newOrder);

    // Notification de succès
    setTimeout(() => {
      todoSaved();
    }, 500);

    // Scroller vers la todo déplacée
    if (movedTodo) {
      setTimeout(() => {
        scrollToTodo(movedTodo.id, 'smooth');
        currentlyModifying.value = null;
      }, 600);
    }

  } catch (error) {
    console.error('❌ Erreur lors de la réorganisation:', error);
    apiError('Impossible de sauvegarder l\'ordre des todos');
    currentlyModifying.value = null;
  }
};

// Gestionnaires d'événements des todos
const handleToggle = (id: number) => {
  emit('toggleTodo', id);
};

const handleEdit = (todo: Todo) => {
  emit('editTodo', todo);
};

const handleDelete = (id: number) => {
  emit('deleteTodo', id);
};

// 🎯 Lifecycle hooks
onMounted(() => {
  console.log('📝 [TodoList] Composant monté');
  nextTick(() => {
    if (props.todos.length > 1) {
      console.log('🎯 Initialisation initiale de Sortable');
      initializeSortable();
    }
  });

  // Fermer le menu d'export au clic extérieur
  document.addEventListener('click', (event: Event) => {
    const target = event.target as Element;
    if (!target.closest(`.${styles.exportDropdown}`)) {
      closeExportMenu();
    }
  });
});

onUpdated(() => {
  // Vérifier la cohérence après mise à jour
  if (!sortableContainer.value && sortableInstance) {
    console.log('🧹 Container supprimé, nettoyage...');
    destroySortableInstance();
  }
});

onBeforeUnmount(() => {
  console.log('📝 [TodoList] Nettoyage avant démontage');
  destroySortableInstance();
});
</script>