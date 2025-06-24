import { ref, computed } from 'vue';
import {
  todoListsApi, todosApi, apiUtils,
  type Todo,
  type TodoList,
  type CreateTodoRequest,
  type UpdateTodoRequest,
  type Category
} from '../services/api';
import { useNotifications } from './useNotifications';
import type { ExportOptions, ExportData, ExportMetadata } from '@/types/export';



const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  operation = 'opération'
): Promise<T> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      console.log(`⚠️ Tentative ${i + 1}/${maxRetries} échouée pour ${operation}:`, error);

      if (i === maxRetries - 1) {
        console.error(`❌ Échec définitif après ${maxRetries} tentatives pour ${operation}`);
        throw error;
      }

      // Délai progressif : 1s, 2s, 3s...
      const delay = 1000 * (i + 1);
      console.log(`⏳ Nouvelle tentative dans ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Unexpected error in withRetry');
};

// État global (ou tu peux utiliser Pinia)
const todolists = ref<TodoList[]>([]);
const currentTodolist = ref<TodoList | null>(null);
const currentTodos = ref<Todo[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const allTodos = ref<Todo[]>([]);


const loadAllTodos = async () => {
  loading.value = true;
  try {
    allTodos.value = await todosApi.getAll();
  } catch (err) {
    error.value = 'Erreur lors du chargement des todos';
  } finally {
    loading.value = false;
  }
};

// 🎯 NOUVELLES FONCTIONS pour gérer le scroll
const preserveScrollPosition = async (operation: () => Promise<any>) => {
  // Sauvegarder la position de scroll
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

  try {
    // Exécuter l'opération
    await operation();

    // Attendre que le DOM soit mis à jour
    await new Promise(resolve => setTimeout(resolve, 100));

    // Restaurer la position
    window.scrollTo({
      top: scrollTop,
      left: scrollLeft,
      behavior: 'instant' // Pas d'animation pour être discret
    });
  } catch (error) {
    // Restaurer même en cas d'erreur
    window.scrollTo({
      top: scrollTop,
      left: scrollLeft,
      behavior: 'instant'
    });
    throw error;
  }
};


const exportTodoListWithOptions = (
  todolist: TodoList,
  todos: Todo[],
  options: ExportOptions = {}
): ExportData => {
  const {
    includeMetadata = true,
    includeCompleted = true,
    includePending = true,
    sortBy = 'priority',
    format = 'pretty'
  } = options;

  console.log(`📥 Export de "${todolist.name}" avec options:`, options);

  // 🔍 1. FILTRAGE DES TODOS selon les options
  let filteredTodos = [...todos];

  if (!includeCompleted && !includePending) {
    console.warn('⚠️ Aucun todo ne sera exporté (completed et pending désactivés)');
    filteredTodos = [];
  } else {
    if (!includeCompleted) {
      filteredTodos = filteredTodos.filter(t => !t.completed);
      console.log(`🔴 Exclusion des todos terminés: ${todos.filter(t => t.completed).length} exclus`);
    }

    if (!includePending) {
      filteredTodos = filteredTodos.filter(t => t.completed);
      console.log(`🔴 Exclusion des todos en cours: ${todos.filter(t => !t.completed).length} exclus`);
    }
  }

  // 📊 2. TRI DES TODOS selon l'option
  const sortFunctions = {
    priority: (a: Todo, b: Todo) => a.priority - b.priority,
    name: (a: Todo, b: Todo) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' }),
    completed: (a: Todo, b: Todo) => {
      // Trier par statut : en cours d'abord (false), puis terminés (true)
      if (a.completed === b.completed) {
        return a.priority - b.priority; // Tri secondaire par priorité
      }
      return a.completed ? 1 : -1;
    }
  };

  filteredTodos.sort(sortFunctions[sortBy]);
  console.log(`🔄 Todos triés par: ${sortBy} (${filteredTodos.length} todos)`);

  // 🏗️ 3. CONSTRUCTION DE L'OBJET D'EXPORT
  const exportData: ExportData = {
    todolist: {
      id: todolist.id,
      name: todolist.name,
    },
    todos: filteredTodos.map((todo, index) => ({
      id: todo.id,
      name: todo.name,
      completed: todo.completed,
      priority: todo.priority,
      // Ajouter des champs utiles pour l'export
      export_order: index + 1,
      status: todo.completed ? 'completed' : 'pending',
      status_emoji: todo.completed ? '✅' : '⏳'
    }))
  };

  // 📋 4. AJOUT DES MÉTADONNÉES si demandées
  if (includeMetadata) {
    const metadata: ExportMetadata = {
      exported_at: new Date().toISOString(),
      export_options: {
        includeMetadata,
        includeCompleted,
        includePending,
        sortBy,
        format
      },
      total_todos: filteredTodos.length,
      completed_todos: filteredTodos.filter(t => t.completed).length,
      pending_todos: filteredTodos.filter(t => !t.completed).length,
      version: '1.0',
      // Statistiques supplémentaires
      original_total: todos.length,
      completion_rate: todos.length > 0 ? Math.round((todos.filter(t => t.completed).length / todos.length) * 100) : 0,
      export_info: {
        excluded_completed: !includeCompleted ? todos.filter(t => t.completed).length : 0,
        excluded_pending: !includePending ? todos.filter(t => !t.completed).length : 0,
        sorted_by: sortBy
      }
    };

    exportData.metadata = metadata;
  }

  console.log('✅ Données d\'export préparées:', {
    todolist: exportData.todolist.name,
    todos_count: exportData.todos.length,
    has_metadata: !!exportData.metadata
  });

  return exportData;
};

/**
 * Télécharge une TodoList en JSON avec options personnalisées
 */
const downloadTodoListWithOptions = async (
  todolist: TodoList,
  todos: Todo[],
  options: ExportOptions = {}
): Promise<void> => {
  try {
    console.log(`🚀 Début du téléchargement de "${todolist.name}"`);

    // 1. Préparer les données d'export
    const exportData = exportTodoListWithOptions(todolist, todos, options);

    // 2. Convertir en JSON selon le format
    const spacing = options.format === 'compact' ? 0 : 2;
    const jsonContent = JSON.stringify(exportData, null, spacing);

    // 3. Créer le blob
    const blob = new Blob([jsonContent], {
      type: 'application/json;charset=utf-8'
    });
    const url = URL.createObjectURL(blob);

    // 4. Générer un nom de fichier intelligent
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const safeName = todolist.name
      .replace(/[^a-zA-Z0-9\s]/g, '') // Supprimer caractères spéciaux
      .replace(/\s+/g, '_') // Remplacer espaces par underscore
      .substring(0, 50); // Limiter la longueur

    // Ajouter suffixes selon les options
    const suffixes = [];
    if (!options.includeCompleted) suffixes.push('pending-only');
    if (!options.includePending) suffixes.push('completed-only');
    if (options.sortBy && options.sortBy !== 'priority') suffixes.push(`sorted-by-${options.sortBy}`);

    const suffixString = suffixes.length > 0 ? `_${suffixes.join('_')}` : '';
    const filename = `todolist_${safeName}${suffixString}_${timestamp}.json`;

    console.log(`📁 Nom de fichier généré: ${filename}`);

    // 5. Déclencher le téléchargement
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();

    // 6. Nettoyer
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);

    // 7. Notification de succès avec détails
    const { success } = useNotifications();
    const todoCount = exportData.todos.length;
    const totalCount = todos.length;

    let message = `${todoCount} todo(s) exporté(s)`;
    if (todoCount !== totalCount) {
      message += ` sur ${totalCount} total`;
    }

    success('Export réussi', `"${todolist.name}" - ${message}`);

    console.log('✅ Export terminé avec succès:', {
      filename,
      size: `${(blob.size / 1024).toFixed(1)} KB`,
      todos_exported: todoCount,
      format: options.format
    });

  } catch (error) {
    console.error('❌ Erreur lors de l\'export:', error);

    const { apiError } = useNotifications();
    apiError(`Erreur lors de l'export de "${todolist.name}"`);

    throw error;
  }
};

/**
 * Exporter la TodoList courante avec options
 */
const exportCurrentTodoListWithOptions = async (options: ExportOptions = {}): Promise<void> => {
  if (!currentTodolist.value) {
    const { warning } = useNotifications();
    warning('Aucune TodoList', 'Veuillez d\'abord sélectionner une TodoList');
    return;
  }

  if (currentTodos.value.length === 0) {
    const { warning } = useNotifications();
    warning('Liste vide', 'Cette TodoList ne contient aucun todo à exporter');
    return;
  }

  await downloadTodoListWithOptions(
    currentTodolist.value,
    currentTodos.value,
    options
  );
};

/**
 * Export rapide avec options prédéfinies
 */
const exportPresets = {
  // Tout exporter (par défaut)
  all: (todolist: TodoList, todos: Todo[]) =>
    downloadTodoListWithOptions(todolist, todos, {
      includeMetadata: true,
      includeCompleted: true,
      includePending: true,
      sortBy: 'priority',
      format: 'pretty'
    }),

  // Seulement les todos en cours
  pendingOnly: (todolist: TodoList, todos: Todo[]) =>
    downloadTodoListWithOptions(todolist, todos, {
      includeMetadata: true,
      includeCompleted: false,
      includePending: true,
      sortBy: 'priority',
      format: 'pretty'
    }),

  // Seulement les todos terminés
  completedOnly: (todolist: TodoList, todos: Todo[]) =>
    downloadTodoListWithOptions(todolist, todos, {
      includeMetadata: true,
      includeCompleted: true,
      includePending: false,
      sortBy: 'priority',
      format: 'pretty'
    }),

  // Export compact (sans métadonnées, format minimal)
  compact: (todolist: TodoList, todos: Todo[]) =>
    downloadTodoListWithOptions(todolist, todos, {
      includeMetadata: false,
      includeCompleted: true,
      includePending: true,
      sortBy: 'priority',
      format: 'compact'
    }),

  // Export trié par nom
  alphabetical: (todolist: TodoList, todos: Todo[]) =>
    downloadTodoListWithOptions(todolist, todos, {
      includeMetadata: true,
      includeCompleted: true,
      includePending: true,
      sortBy: 'name',
      format: 'pretty'
    })
};


export function useTodos() {
  // Notifications
  const {
    apiError,
    todoAdded,
    todoDeleted,
    todoCompleted,
    todoUncompleted,
    todolistDeleted
  } = useNotifications();
  // Actions pour les TodoLists
  const loadTodoLists = async () => {
    loading.value = true;
    error.value = null;

    try {
      todolists.value = await todoListsApi.getAll();
    } catch (err) {
      error.value = apiUtils.handleError(err);
      console.error('Erreur lors du chargement des todolists:', err);
    } finally {
      loading.value = false;
    }
  };

  const loadTodoList = async (id: number) => {
    loading.value = true;
    error.value = null;

    try {
      currentTodolist.value = await todoListsApi.getById(id);
      currentTodos.value = await todoListsApi.getTodos(id);
    } catch (err) {
      error.value = apiUtils.handleError(err);
      console.error('Erreur lors du chargement de la todolist:', err);
    } finally {
      loading.value = false;
    }
  };

  const createTodoList = async (name: string, category_id: number) => {
    loading.value = true;
    error.value = null;

    try {
      const newTodoList = await todoListsApi.create({ name, category_id });
      todolists.value.push(newTodoList);
      return newTodoList;
    } catch (err) {
      error.value = apiUtils.handleError(err);
      console.error('Erreur lors de la création de la todolist:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteTodoList = async (id: number) => {
    loading.value = true;
    error.value = null;

    // Validation de l'ID
    if (!id || id <= 0) {
      error.value = "ID de TodoList invalide";
      loading.value = false;
      return;
    }

    // Trouver la todolist à supprimer
    const todolistToDelete = todolists.value.find(t => t.id === id);

    if (!todolistToDelete) {
      error.value = "TodoList introuvable";
      loading.value = false;
      return;
    }

    const todolistName = todolistToDelete.name;

    try {
      await withRetry(
        () => todoListsApi.delete(id),
        3,
        `suppression todolist "${todolistName}"`
      );

      // Mise à jour de l'état local
      todolists.value = todolists.value.filter(t => t.id !== id);

      // Gestion de la todolist courante
      if (currentTodolist.value?.id === id) {
        currentTodolist.value = null;
        currentTodos.value = [];
      }

      todolistDeleted(todolistName);

    } catch (err) {
      const errorMessage = apiUtils.handleError(err);
      error.value = errorMessage;
      apiError(errorMessage);
      console.error('Erreur lors de la suppression de la todolist:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteTodo = async (id: number) => {
    await preserveScrollPosition(async () => {
      loading.value = true;
      error.value = null;

      // Récupérer le nom avant suppression pour la notification
      const todoToDelete = currentTodos.value.find(t => t.id === id);
      const todoName = todoToDelete?.name || 'Todo';

      try {
        await todosApi.delete(id);

        // 🎯 CORRECTION : Recharger toute la TodoList pour avoir les priorités à jour
        if (currentTodolist.value) {
          await loadTodoList(currentTodolist.value.id);
        }

        todoDeleted(todoName);
      } catch (err) {
        const errorMessage = apiUtils.handleError(err);
        error.value = errorMessage;
        apiError(errorMessage);
        console.error('Erreur lors de la suppression du todo:', err);
        throw err;
      } finally {
        loading.value = false;
      }
    });
  };

  // Actions pour les Todos
  const addTodo = async (todolistId: number, name: string, priority?: number) => {
    await preserveScrollPosition(async () => {

      loading.value = true;
      error.value = null;

      try {
        const todoData: CreateTodoRequest = { name };
        if (priority !== undefined && priority > 0) {
          todoData.priority = priority;
        }
        const newTodo = await todoListsApi.addTodo(todolistId, todoData);

        if (currentTodolist.value) {
          await loadTodoList(currentTodolist.value.id);
        }

        todoAdded(name);
        return newTodo;
      } catch (err) {
        const errorMessage = apiUtils.handleError(err);
        error.value = errorMessage;
        apiError(errorMessage);
        console.error('Erreur lors de l\'ajout du todo:', err);
        throw err;
      } finally {
        loading.value = false;
      }
    });
  };

  const updateTodo = async (id: number, data: UpdateTodoRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const updatedTodo = await todosApi.update(id, data);
      const index = currentTodos.value.findIndex(t => t.id === id);
      if (index !== -1) {
        currentTodos.value[index] = updatedTodo;
      }
      return updatedTodo;
    } catch (err) {
      error.value = apiUtils.handleError(err);
      console.error('Erreur lors de la mise à jour du todo:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const toggleTodo = async (todo: Todo) => {
    await preserveScrollPosition(async () => {

      const originalTodo = { ...todo };
      const wasCompleted = todo.completed;

      // Optimistic update
      const index = currentTodos.value.findIndex(t => t.id === todo.id);
      if (index !== -1) {
        currentTodos.value[index].completed = !todo.completed;
      }

      try {
        const updatedTodo = await todosApi.toggle(todo.id, originalTodo);

        // 🎯 CORRECTION : Recharger toute la TodoList pour avoir les priorités à jour
        if (currentTodolist.value) {
          await loadTodoList(currentTodolist.value.id);
        }

        // Notifications intelligentes
        if (updatedTodo.completed && !wasCompleted) {
          todoCompleted(updatedTodo.name);
          setTimeout(() => {
            useNotifications().info(
              'Réorganisation automatique',
              `"${updatedTodo.name}" a été déplacé en fin de liste`
            );
          }, 500);
        } else if (!updatedTodo.completed && wasCompleted) {
          todoUncompleted(updatedTodo.name);
          setTimeout(() => {
            useNotifications().info(
              'Position mise à jour',
              `"${updatedTodo.name}" a retrouvé sa place dans les actifs`
            );
          }, 500);
        }
      } catch (err) {
        // Rollback en cas d'erreur
        if (index !== -1) {
          currentTodos.value[index] = originalTodo;
        }
        const errorMessage = apiUtils.handleError(err);
        error.value = errorMessage;
        apiError(errorMessage);
        throw err;
      }
    });
  };

  const reorderTodos = async (todolistId: number, todoIds: number[]) => {
    const originalTodos = [...currentTodos.value];

    // Optimistic update
    const reorderedTodos = todoIds.map(id =>
      currentTodos.value.find(todo => todo.id === id)!
    ).filter(Boolean);
    currentTodos.value = reorderedTodos;

    try {
      await todoListsApi.reorderTodos(todolistId, todoIds);
      // Recharger pour avoir les bonnes priorités
      await loadTodoList(todolistId);
    } catch (err) {
      // Rollback
      currentTodos.value = originalTodos;
      error.value = apiUtils.handleError(err);
      console.error('Erreur lors de la réorganisation:', err);
      throw err;
    }
  };

  // Computed
  const sortedTodos = computed(() => {
    return [...currentTodos.value].sort((a, b) => a.priority - b.priority);
  });

  const completedTodos = computed(() => {
    return currentTodos.value.filter(todo => todo.completed);
  });

  const pendingTodos = computed(() => {
    return currentTodos.value.filter(todo => !todo.completed);
  });


  // Fonction de nettoyage des erreurs
  const clearError = () => {
    error.value = null;
  };

  // Test de connexion
  const testConnection = async () => {
    try {
      await apiUtils.healthCheck();
      return true;
    } catch (err) {
      error.value = apiUtils.handleError(err);
      return false;
    }
  };

  return {
    // État
    todolists,
    currentTodolist,
    currentTodos,
    loading,
    error,

    // Computed
    sortedTodos,
    completedTodos,
    pendingTodos,

    // Actions TodoLists
    loadTodoLists,
    loadTodoList,
    createTodoList,
    deleteTodoList,

    // Actions Todos
    addTodo,
    toggleTodo,
    updateTodo,
    deleteTodo,
    reorderTodos,

    // 🎯 FONCTIONS D'EXPORT - Vérifiez qu'elles sont toutes là
    exportTodoListWithOptions,
    downloadTodoListWithOptions,
    exportCurrentTodoListWithOptions,
    exportPresets,
    // Utilitaires
    clearError,
    testConnection,

    //Actions de recherche
    allTodos,
    loadAllTodos
  };
}