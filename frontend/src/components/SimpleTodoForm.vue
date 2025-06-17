<template>
  <div :class="styles.simpleTodoForm">
    <div :class="styles.formRow">
      <!-- Champ nom principal -->
      <input
        ref="nameInput"
        v-model="todoName"
        type="text"
        placeholder="Nom de la tâche..."
        :class="styles.todoNameInput"
        @keydown.enter="handleSubmit"
        @keydown.escape="handleCancel"
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
        @keydown.enter="handleSubmit"
        @keydown.escape="handleCancel"
      />
      
      <!-- Boutons d'action groupés -->
      <div style="display: flex; gap: var(--spacing-xs);">
        <button 
          @click="handleSubmit" 
          :disabled="!todoName.trim()"
          :class="styles.btnAdd"
          title="Ajouter la tâche (Entrée)"
          type="button"
        >
          ✓
        </button>
        
        <button 
          @click="handleCancel" 
          :class="styles.btnCancel"
          title="Annuler (Échap)"
          type="button"
        >
          ✕
        </button>
      </div>
    </div>
    
    <!-- Aide contextuelle discrète -->
    <div :class="styles.formHint">
      💡 <strong>Astuce :</strong> Laissez la priorité vide pour ajouter en fin de liste, ou indiquez un chiffre (1 = urgent).
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';
import styles from '@/styles/components/SimpleTodoForm.module.css';

interface Emits {
  addTodo: [name: string, priority?: number];
  cancel: [];
}

const emit = defineEmits<Emits>();

// État local
const todoName = ref('');
const customPriority = ref<number | null>(null);
const nameInput = ref<HTMLInputElement>();

// Méthodes principales
const handleSubmit = () => {
  if (!todoName.value.trim()) return;
  
  const priority = customPriority.value && customPriority.value > 0 ? customPriority.value : undefined;
  
  console.log('📝 [SimpleTodoForm] Ajout todo:', { 
    name: todoName.value.trim(), 
    priority,
    hasCustomPriority: !!priority 
  });
  
  emit('addTodo', todoName.value.trim(), priority);
  resetForm();
};

const handleCancel = () => {
  console.log('📝 [SimpleTodoForm] Annulation');
  resetForm();
  emit('cancel');
};

const resetForm = () => {
  todoName.value = '';
  customPriority.value = null;
};

const focusInput = async () => {
  await nextTick();
  nameInput.value?.focus();
};

// Lifecycle
onMounted(() => {
  focusInput();
  console.log('📝 [SimpleTodoForm] Composant monté et focusé');
});

// Méthodes exposées pour le parent
defineExpose({
  focusInput,
  resetForm
});
</script>