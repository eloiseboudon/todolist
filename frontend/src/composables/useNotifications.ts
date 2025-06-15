import { ref, reactive } from 'vue';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
}

const notifications = ref<Notification[]>([]);

let notificationId = 0;

export function useNotifications() {
  
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = `notification-${++notificationId}`;
    const duration = notification.duration ?? 4000;
    
    const newNotification: Notification = {
      id,
      ...notification,
      duration,
    };

    notifications.value.push(newNotification);

    // Auto-remove après la durée spécifiée (sauf si persistent)
    if (!notification.persistent) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  };

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index > -1) {
      notifications.value.splice(index, 1);
    }
  };

  const clearAll = () => {
    notifications.value = [];
  };

  // Helpers pour différents types
  const success = (title: string, message?: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'success',
      title,
      message,
      ...options,
    });
  };

  const error = (title: string, message?: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'error',
      title,
      message,
      duration: 6000, // Plus long pour les erreurs
      ...options,
    });
  };

  const warning = (title: string, message?: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'warning',
      title,
      message,
      ...options,
    });
  };

  const info = (title: string, message?: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'info',
      title,
      message,
      ...options,
    });
  };

  // Notifications spécifiques pour les todos
  const todoSaved = () => {
    return success('Ordre sauvegardé', 'La réorganisation a été enregistrée');
  };

  const todoAdded = (name: string) => {
    return success('Todo ajouté', `"${name}" a été ajouté à la liste`);
  };

  const todoDeleted = (name: string) => {
    return success('Todo supprimé', `"${name}" a été supprimé`);
  };

  const todoCompleted = (name: string) => {
    return success('Todo terminé', `"${name}" a été marqué comme terminé`);
  };

  const todoUncompleted = (name: string) => {
    return info('Todo réactivé', `"${name}" a été remis en cours`);
  };

  const todolistDeleted = (name: string) => {
    return success('Todolist supprimée', `"${name}" a été supprimé`);
  };


  const apiError = (message: string = 'Une erreur est survenue') => {
    return error('Erreur API', message);
  };

  const saving = () => {
    return info('Sauvegarde...', 'Enregistrement en cours', { duration: 1000 });
  };

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    
    // Helpers par type
    success,
    error,
    warning,
    info,
    
    // Notifications spécifiques
    todoSaved,
    todoAdded,
    todoDeleted,
    todoCompleted,
    todoUncompleted,
    todolistDeleted,
    apiError,
    saving,
  };
}