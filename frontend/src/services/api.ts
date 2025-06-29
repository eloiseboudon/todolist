// Types pour l'API


export interface Category {
  id: number;
  name: string;
  color: string;
  icon: string;
}


export interface Todo {
  id: number;
  name: string;
  completed: boolean;
  priority: number;
  quantity?: string;
  todolist_id?: number;
  todolist: TodoList;
}

export interface TodoList {
  id: number;
  name: string;
  todos?: Todo[];
  category_id?: number;
  category?: Category;
}

export interface CreateTodoRequest {
  name: string;
  completed?: boolean;
  priority?: number;
  quantity?: string;
}

export interface CreateTodoListRequest {
  name: string;
  todos?: CreateTodoRequest[];
  category_id?: number;
}

export interface UpdateTodoRequest {
  name: string;
  completed?: boolean;
  priority?: number;
  quantity?: string;
  todolist_id?: number;
}

// Configuration de base
const API_BASE_URL = 'http://localhost:8000';

// Classe d'erreur personnalisée
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }

  toString() {
    return `ApiError ${this.status}: ${this.message}`;
  }
}

// Fonction utilitaire pour les requêtes
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = await fetch(url, { ...defaultOptions, ...options });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    console.error('API Error Details:', {
      status: response.status,
      statusText: response.statusText,
      errorData
    });

    throw new ApiError(
      errorData?.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

// API TodoLists
export const todoListsApi = {
  // Récupérer toutes les todolists
  async getAll(): Promise<TodoList[]> {
    return apiRequest<TodoList[]>('/todolists/');
  },

  // Récupérer une todolist par ID
  async getById(id: number): Promise<TodoList> {
    return apiRequest<TodoList>(`/todolists/${id}`);
  },

  // Créer une nouvelle todolist
  async create(data: CreateTodoListRequest): Promise<TodoList> {
    return apiRequest<TodoList>('/todolists/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Mettre à jour une todolist
  async update(id: number, data: CreateTodoListRequest): Promise<TodoList> {
    return apiRequest<TodoList>(`/todolists/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Supprimer une todolist
  async delete(id: number): Promise<{ message: string }> {
    return apiRequest<{ message: string }>(`/todolists/${id}`, {
      method: 'DELETE',
    });
  },

  // Récupérer tous les todos d'une todolist
  async getTodos(todolistId: number): Promise<Todo[]> {
    return apiRequest<Todo[]>(`/todolists/${todolistId}/todos`);
  },

  // Ajouter un todo à une todolist
  async addTodo(todolistId: number, data: CreateTodoRequest): Promise<Todo> {
    return apiRequest<Todo>(`/todolists/${todolistId}/todos`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Réorganiser les todos
  async reorderTodos(todolistId: number, todoIds: number[]): Promise<{ message: string }> {
    return apiRequest<{ message: string }>(`/todolists/${todolistId}/todos/reorder`, {
      method: 'PUT',
      body: JSON.stringify(todoIds),
    });
  },

  // Ajouter tous les todos d'une enfant à une todolist parent
  async addLinkBetweenTodolist(childId: number, parentId: number): Promise<TodoList> {
    return apiRequest<TodoList>(`/todolists/${parentId}/add_link/${childId}`, {
      method: 'POST',
    });
  },

  async populateFromLinks(todolistId: number): Promise<TodoList> {
    return apiRequest<TodoList>(`/todolists/${todolistId}/populate_from_links`, {
      method: 'POST',
    });
  },

  // Supprimer le lien entre une todolist parent et enfent
  async removeLinkBetweenTodolist(childId: number, parentId: number): Promise<TodoList> {
    return apiRequest<TodoList>(`/todolists/${parentId}/remove_link/${childId}`, {
      method: 'DELETE',
    });
  },

  // Récupérer les liens entre une todolist et des recettes
  async getLinksbyTodolistId(todolistId: number): Promise<TodoList[]> {
    return apiRequest<TodoList[]>(`/todolists/${todolistId}/links`);
  },
};



// API Categories (nouveau)
export const categoriesApi = {
  // Récupérer toutes les catégories
  async getAll(): Promise<Category[]> {
    return apiRequest<Category[]>('/categories/');
  },

  // Récupérer les catégories actives
  async getActive(): Promise<Category[]> {
    return apiRequest<Category[]>('/categories/active');
  },

  // Récupérer une catégorie par ID
  async getById(id: number): Promise<Category> {
    return apiRequest<Category>(`/categories/${id}`);
  },

  async updateCategory(data: CreateTodoListRequest): Promise<Category> {
    return apiRequest<Category>('/categories/addTodoList', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// API Todos
export const todosApi = {
  // Récupérer tous les todos
  async getAll(): Promise<Todo[]> {
    return apiRequest<Todo[]>('/todos/');
  },

  // Mettre à jour un todo
  async update(id: number, data: UpdateTodoRequest): Promise<Todo> {
    return apiRequest<Todo>(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Supprimer un todo
  async delete(id: number): Promise<{ message: string }> {
    return apiRequest<{ message: string }>(`/todos/${id}`, {
      method: 'DELETE',
    });
  },

  // Toggle le statut completed d'un todo
  async toggle(id: number): Promise<Todo> {
    return apiRequest<Todo>(`/todos/${id}/toggle`, {
      method: 'PATCH',
    });
  },
};

// Fonctions utilitaires
export const apiUtils = {
  // Test de connexion à l'API
  async healthCheck(): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/');
  },

  // Gestion d'erreur globale
  handleError(error: unknown): string {
    if (error instanceof ApiError) {
      return error.message;
    }
    if (error instanceof Error) {
      return error.message;
    }
    return 'Une erreur inconnue s\'est produite';
  },
};
