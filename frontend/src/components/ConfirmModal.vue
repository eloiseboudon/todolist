<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" :class="styles.modalOverlay" @click.self="onCancel">
        <div :class="styles.modalContainer">
          
          <!-- Header -->
          <div :class="styles.modalHeader">
            <div :class="styles.iconContainer">
              <span :class="[styles.icon, styles[type]]">{{ getIcon() }}</span>
            </div>
            <h3 :class="styles.title">{{ title }}</h3>
          </div>

          <!-- Body -->
          <div :class="styles.modalBody">
            <p :class="styles.message">{{ message }}</p>
            <div v-if="details" :class="styles.details">
              {{ details }}
            </div>
          </div>

          <!-- Footer -->
          <div :class="styles.modalFooter">
            <button 
              @click="onCancel" 
              :class="[styles.btn, styles.btnCancel]"
              type="button"
            >
              {{ cancelText }}
            </button>
            <button 
              @click="onConfirm" 
              :class="[styles.btn, styles.btnConfirm, styles[type]]"
              type="button"
              :disabled="loading"
            >
              <span v-if="loading" :class="styles.spinner">⏳</span>
              {{ loading ? loadingText : confirmText }}
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  show: boolean;
  type?: 'danger' | 'warning' | 'info';
  title: string;
  message: string;
  details?: string;
  confirmText?: string;
  cancelText?: string;
  loadingText?: string;
  loading?: boolean;
}

interface Emits {
  confirm: [];
  cancel: [];
}

const props = withDefaults(defineProps<Props>(), {
  type: 'danger',
  confirmText: 'Confirmer',
  cancelText: 'Annuler',
  loadingText: 'Suppression...',
  loading: false
});

const emit = defineEmits<Emits>();

const getIcon = () => {
  switch (props.type) {
    case 'danger': return '🗑️';
    case 'warning': return '⚠️';
    case 'info': return 'ℹ️';
    default: return '❓';
  }
};

const onConfirm = () => {
  emit('confirm');
};

const onCancel = () => {
  emit('cancel');
};

// Gestion de la touche Escape
import { onMounted, onUnmounted } from 'vue';

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.show) {
    onCancel();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleEscape);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape);
});

import styles from '@/styles/components/ConfirmModal.module.css';
</script>