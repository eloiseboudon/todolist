// types/index.ts - Point d'entrée centralisé pour tous les types

// Types d'export
export type { 
  ExportOptions, 
  ExportMetadata, 
  ExportedTodo, 
  ExportData, 
  ExportPreset, 
  ExportPresetConfig,
  ExportFileInfo 
} from './export';

// Types de l'API (si vous voulez les re-exporter)
export type { 
  Todo, 
  TodoList, 
  UpdateTodoRequest 
} from '../services/api';

// Types supplémentaires pour l'application
export interface AppConfig {
  version: string;
  apiUrl: string;
  features: {
    exportEnabled: boolean;
    dragDropEnabled: boolean;
    notificationsEnabled: boolean;
  };
}

export interface NotificationOptions {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
}