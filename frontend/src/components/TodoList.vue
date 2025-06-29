<template>
  <div :class="[styles.todoList,'divcontainer']">
    <!-- 🎯 NOUVEAU : En-tête compact avec boutons fins sur la même ligne -->
    <div :class="styles.todoListHeader">
      <div :class="styles.titleSection">
        <div :class="styles.titleRow">
          <h2>{{ todolist.name }}</h2>
          <div :class="styles.headerBadges">
            <!-- Badge catégorie (si existe) -->
            <div v-if="todolist.category" :class="['categoryBadge']">
              <span :class="[styles.categoryIcon]">{{ getCategoryIcon(todolist.category.icon) }}</span>
              <span>{{ todolist.category.name }}</span>
            </div>
            <!-- Badge nombre de tâches -->
            <div :class="[styles.countBadge]">{{ todos.length }} tâche(s)</div>
          </div>
        </div>
      </div>

      <!-- 🎯 NOUVEAU : Boutons compacts alignés -->
      <div :class="[styles.headerActions]">
        <button @click="toggleAddForm" :class="['btnCompact']">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>Ajouter</span>
        </button>

        <!-- Tag/Catégorie -->
        <button @click="showCategoryForm = true" :class="['btnCompact', 'btnSecondary']">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h.008v.008H6V6Z" />
          </svg>
          <span>Tag</span>
        </button>

        <!-- Export -->
        <div :class="['exportDropdown']">
          <button @click="toggleExportMenu" :class="['btnCompact', 'btnTertiary']"
            :disabled="todos.length === 0">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="m9 13.5 3 3m0 0 3-3m-3 3v-6" />
            </svg>
            <span>Export</span>
            <span :class="['dropdownIcon', { ['dropdownOpen']: showExportMenu }]">▼</span>
          </button>

          <!-- Menu dropdown -->
          <div v-if="showExportMenu" :class="['exportMenu']">
            <button @click="handleExport('all')" :class="['exportMenuItem']">
              <span>📄</span> Export complet
            </button>
            <button @click="handleExport('pending')" :class="['exportMenuItem']">
              <span>🔄</span> Tâches en cours
            </button>
            <button @click="handleExport('completed')" :class="['exportMenuItem']">
              <span>✅</span> Tâches terminées
            </button>
            <button @click="handleExport('alphabetical')" :class="['exportMenuItem']">
              <span>🔤</span> Ordre alphabétique
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Formulaires (conservés) -->
    <SimpleTodoForm v-if="showAddForm" @add-todo="handleAddTodoWithPriority" :todolist="todolist" @cancel="cancelAddTodo" />

    <UpdateCategoryTodolistForm v-if="showCategoryForm" :todolist="todolist" @close="showCategoryForm = false"
      @updated="handleCategoryUpdated" />

    <!-- Instructions drag & drop (simplifiées) -->
    <div v-if="todos.length > 1" :class="['dragHint']">
      💡 Glissez-déposez pour réorganiser
    </div>

    <!-- 🎯 CORRIGÉ : Liste des todos avec largeur alignée -->
    <div v-if="todos.length > 0" :class="['todosContainer']">
      <div ref="sortableContainer" :class="['sortableList']">
        <div v-for="todo in sortedTodos" :key="`todo-${todo.id}`" :data-id="todo.id" :class="['draggableItem']">
          <TodoItem :todo="todo" @toggle="handleToggle" @edit="handleEdit" @delete="handleDelete" />
        </div>
      </div>
    </div>

    <!-- État vide -->
    <div v-else :class="['emptyState']">
      <div :class="['emptyIcon']">📝</div>
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
import UpdateCategoryTodolistForm from './UpdateCategoryTodolistForm.vue';
import { useNotifications } from '@/composables/useNotifications';
import styles from '@/styles/components/TodoList.module.css';
import { useTodos } from '@/composables/useTodos';
import type { ExportOptions } from '@/types';
import type { Todo, TodoList } from '@/services/api';
import { getCategoryIcon } from '@/composables/useCategory';


interface Props {
  todolist: TodoList;
  todos: Todo[];
}

interface Emits {
  addTodo: [name: string, priority?: number, quantity?: string];
  toggleTodo: [id: number];
  editTodo: [todo: Todo];
  deleteTodo: [id: number];
  reorderTodos: [todoIds: number[]];
  categoryUpdated: [todolist: TodoList]; // NOUVEAU}
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// État local
const showAddForm = ref(false);
const showExportMenu = ref(false);
const showCategoryForm = ref(false);
const sortableContainer = ref<HTMLElement>();
let sortableInstance: Sortable | null = null;

// Notifications
const {
  saving,
  todoSaved,
  apiError
} = useNotifications();

// État pour la gestion du scroll
const currentlyModifying = ref<number | null>(null);

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
    return;
  }

  try {
    sortableInstance = new Sortable(sortableContainer.value, {
      animation: 200,
      ghostClass: styles.sortableGhost,
      chosenClass: styles.sortableChosen,
      dragClass: styles.sortableDrag,

      // Options de scroll
      scroll: true,
      scrollSensitivity: 100,
      scrollSpeed: 20,

      // Gestionnaire principal
      onEnd: async (evt) => {
        try {
          const { oldIndex, newIndex } = evt;

          if (oldIndex === newIndex || oldIndex === undefined || newIndex === undefined) {
            return;
          }
          await handleReorder(oldIndex, newIndex);
        } catch (error) {
          console.error('❌ Erreur lors du réordonnement:', error);
        }
      },

      // Événements de debug
      onStart: () => {},

      onMove: () => {
        // Optionnel : log des mouvements
        return true; // Autoriser le mouvement
      }
    });
  } catch (error) {
    console.error('❌ Erreur lors de la création de Sortable:', error);
    sortableInstance = null;
  }
};

// 🎯 WATCHERS POUR RÉINITIALISER SORTABLE
watch(() => props.todos.length, (newLength) => {
  nextTick(() => {
    if (newLength > 1 && !sortableInstance) {
      initializeSortable();
    } else if (newLength <= 1 && sortableInstance) {
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
    const { exportPresets } = useTodos();

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

const handleAddTodoWithPriority = (
  name: string,
  priority?: number,
  quantity?: string,
) => {
  emit('addTodo', name, priority, quantity);
  showAddForm.value = false;
};

const handleCategoryUpdated = (updatedTodolist: TodoList) => {
  emit('categoryUpdated', updatedTodolist);
};

// 🎯 Gestionnaire de réorganisation
const handleReorder = async (oldIndex: number, newIndex: number) => {
  const movedTodo = sortedTodos.value[oldIndex];
  if (movedTodo) {
    currentlyModifying.value = movedTodo.id;
  }

  saving();

  try {
    // Créer le nouvel ordre
    const reorderedTodos = [...sortedTodos.value];
    const [movedTodoItem] = reorderedTodos.splice(oldIndex, 1);
    reorderedTodos.splice(newIndex, 0, movedTodoItem);

    // Extraire les IDs
    const newOrder = reorderedTodos.map(todo => todo.id);

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
let clickOutsideHandler: (event: Event) => void;

onMounted(() => {
  nextTick(() => {
    if (props.todos.length > 1) {
      initializeSortable();
    }
  });

  clickOutsideHandler = (event: Event) => {
    const target = event.target as Element;
    if (!target.closest(`.${styles.exportDropdown}`)) {
      closeExportMenu();
    }
  };

  document.addEventListener('click', clickOutsideHandler);
});

onUpdated(() => {
  if (!sortableContainer.value && sortableInstance) {
    destroySortableInstance();
  }
});

onBeforeUnmount(() => {
  destroySortableInstance();
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler);
  }
});
</script>
