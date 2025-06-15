// types/export.ts

/**
 * Options de configuration pour l'export d'une TodoList
 */
export interface ExportOptions {
  /** Inclure les métadonnées dans l'export (statistiques, date, etc.) */
  includeMetadata?: boolean;
  
  /** Inclure les todos terminés dans l'export */
  includeCompleted?: boolean;
  
  /** Inclure les todos en cours dans l'export */
  includePending?: boolean;
  
  /** Critère de tri des todos dans l'export */
  sortBy?: 'priority' | 'name' | 'completed';
  
  /** Format du JSON exporté */
  format?: 'pretty' | 'compact';
}

/**
 * Métadonnées incluses dans l'export
 */
export interface ExportMetadata {
  /** Date et heure de l'export au format ISO */
  exported_at: string;
  
  /** Options utilisées pour cet export */
  export_options: ExportOptions;
  
  /** Nombre total de todos exportés */
  total_todos: number;
  
  /** Nombre de todos terminés dans l'export */
  completed_todos: number;
  
  /** Nombre de todos en cours dans l'export */
  pending_todos: number;
  
  /** Version du format d'export */
  version: string;
  
  /** Nombre total de todos dans la liste originale */
  original_total: number;
  
  /** Taux de completion en pourcentage */
  completion_rate: number;
  
  /** Informations détaillées sur l'export */
  export_info: {
    /** Nombre de todos terminés exclus */
    excluded_completed: number;
    
    /** Nombre de todos en cours exclus */
    excluded_pending: number;
    
    /** Critère de tri appliqué */
    sorted_by: string;
  };
}

/**
 * Structure d'un todo dans l'export
 */
export interface ExportedTodo {
  /** ID unique du todo */
  id: number;
  
  /** Nom/description du todo */
  name: string;
  
  /** Statut de completion */
  completed: boolean;
  
  /** Priorité/ordre dans la liste */
  priority: number;
  
  /** Ordre dans l'export (1, 2, 3...) */
  export_order: number;
  
  /** Statut en texte lisible */
  status: 'completed' | 'pending';
  
  /** Emoji représentant le statut */
  status_emoji: '✅' | '⏳';
}

/**
 * Structure complète des données exportées
 */
export interface ExportData {
  /** Informations sur la TodoList */
  todolist: {
    /** ID de la TodoList */
    id: number;
    
    /** Nom de la TodoList */
    name: string;
  };
  
  /** Liste des todos exportés */
  todos: ExportedTodo[];
  
  /** Métadonnées (optionnel selon les options) */
  metadata?: ExportMetadata;
}

/**
 * Presets d'export prédéfinis
 */
export type ExportPreset = 'all' | 'pendingOnly' | 'completedOnly' | 'compact' | 'alphabetical';

/**
 * Configuration d'un preset d'export
 */
export interface ExportPresetConfig {
  /** Nom du preset */
  name: string;
  
  /** Description du preset */
  description: string;
  
  /** Icône du preset */
  icon: string;
  
  /** Options d'export du preset */
  options: ExportOptions;
}

/**
 * Informations sur le fichier exporté
 */
export interface ExportFileInfo {
  /** Nom du fichier généré */
  filename: string;
  
  /** Taille du fichier en bytes */
  size: number;
  
  /** Nombre de todos exportés */
  todos_count: number;
  
  /** Format utilisé */
  format: 'pretty' | 'compact';
  
  /** Timestamp de création */
  created_at: string;
}