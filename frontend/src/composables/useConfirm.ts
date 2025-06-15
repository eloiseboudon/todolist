import { ref } from 'vue';

interface ConfirmOptions {
  type?: 'danger' | 'warning' | 'info';
  title: string;
  message: string;
  details?: string;
  confirmText?: string;
  cancelText?: string;
  loadingText?: string;
}

interface ConfirmState {
  show: boolean;
  loading: boolean;
  options: ConfirmOptions;
  resolve?: (value: boolean) => void;
}

const confirmState = ref<ConfirmState>({
  show: false,
  loading: false,
  options: {
    title: '',
    message: ''
  }
});

export function useConfirm() {
  
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      confirmState.value = {
        show: true,
        loading: false,
        options,
        resolve
      };
    });
  };

  const handleConfirm = async () => {
    if (confirmState.value.resolve) {
      confirmState.value.loading = true;
      
      // Petit délai pour l'animation de loading
      await new Promise(resolve => setTimeout(resolve, 300));
      
      confirmState.value.resolve(true);
      close();
    }
  };

  const handleCancel = () => {
    if (confirmState.value.resolve) {
      confirmState.value.resolve(false);
      close();
    }
  };

  const close = () => {
    confirmState.value.show = false;
    confirmState.value.loading = false;
    confirmState.value.resolve = undefined;
  };

  // Fonctions de confirmation prédéfinies
  const confirmDelete = (itemName: string, details?: string): Promise<boolean> => {
    return confirm({
      type: 'danger',
      title: 'Confirmer la suppression',
      message: `Êtes-vous sûr de vouloir supprimer "${itemName}" ?`,
      details: details || 'Cette action est irréversible.',
      confirmText: 'Supprimer',
      cancelText: 'Annuler',
      loadingText: 'Suppression...'
    });
  };

  const confirmAction = (title: string, message: string, details?: string): Promise<boolean> => {
    return confirm({
      type: 'warning',
      title,
      message,
      details,
      confirmText: 'Confirmer',
      cancelText: 'Annuler',
      loadingText: 'En cours...'
    });
  };

  const confirmInfo = (title: string, message: string, details?: string): Promise<boolean> => {
    return confirm({
      type: 'info',
      title,
      message,
      details,
      confirmText: 'OK',
      cancelText: 'Annuler',
      loadingText: 'Traitement...'
    });
  };

  return {
    // État
    confirmState,
    
    // Actions
    confirm,
    handleConfirm,
    handleCancel,
    close,
    
    // Fonctions prédéfinies
    confirmDelete,
    confirmAction,
    confirmInfo
  };
}