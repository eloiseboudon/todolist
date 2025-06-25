<template>
  <div :class="styles.simpleTodoForm">
    <div :class="styles.formRow">
      <!-- Champ nom principal -->
      <input ref="nameInput" v-model="todoName" type="text" placeholder="Nom de la tâche..."
        :class="styles.todoNameInput" @keydown.enter="handleSubmit" @keydown.escape="handleCancel" maxlength="200"
        required />

      <!-- Champ priorité compact -->
      <input v-model.number="customPriority" type="number" min="1" max="999" placeholder="Priorité"
        :class="styles.priorityInput" title="Priorité optionnelle (ex: 1 = urgent)" @keydown.enter="handleSubmit"
        @keydown.escape="handleCancel" />
{{ todolist.name }}
      <input v-if="True" v-model="quantity" type="text" placeholder="Quantité"
        :class="styles.quantityInput" @keydown.enter="handleSubmit" @keydown.escape="handleCancel" />

      <!-- Boutons d'action groupés -->
      <div :class="styles.actionButtons">
        <button @click="handleSubmit" :disabled="!todoName.trim()" :class="styles.btnAdd"
          title="Ajouter la tâche (Entrée)" type="button">
          ✓
        </button>

        <button @click="handleCancel" :class="styles.btnCancel" title="Annuler (Échap)" type="button">
          ✕
        </button>
      </div>

      <!-- Icône d'information avec tooltip -->
      <div :class="styles.infoTooltip">
        <button type="button" :class="styles.infoButton" @mouseenter="showTooltip = true"
          @mouseleave="showTooltip = false" @click="toggleTooltip" title="Aide et astuces">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
          </svg>

        </button>

        <!-- Tooltip avec l'astuce -->
        <div v-if="showTooltip" :class="styles.tooltipContent" @mouseenter="showTooltip = true"
          @mouseleave="showTooltip = false">
          <div :class="styles.tooltipArrow"></div>
          <div :class="styles.tooltipText">
            <strong>💡 Astuce :</strong><br>
            Laissez la priorité vide pour ajouter en fin de liste,<br>
            ou indiquez un chiffre (1 = urgent).
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';
import styles from '@/styles/components/SimpleTodoForm.module.css';
import type { TodoList, Category } from '@/services/api';

interface Props {
    todolist: TodoList;
}

interface Emits {
  addTodo: [name: string, priority?: number, quantity?: string];
  cancel: [];
}

const emit = defineEmits<Emits>();
const props = defineProps<Props>();

// État local
const todoName = ref('');
const customPriority = ref<number | null>(null);
const quantity = ref('');
const nameInput = ref<HTMLInputElement>();
const showTooltip = ref(false);

// Méthodes principales
const handleSubmit = () => {
  if (!todoName.value.trim()) return;

  const priority = customPriority.value && customPriority.value > 0 ? customPriority.value : undefined;
  const qty = quantity.value.trim() || undefined;

  emit('addTodo', todoName.value.trim(), priority, qty);
  resetForm();
};

const handleCancel = () => {
  resetForm();
  emit('cancel');
};

const resetForm = () => {
  todoName.value = '';
  customPriority.value = null;
  quantity.value = '';
  showTooltip.value = false;
};

const toggleTooltip = () => {
  showTooltip.value = !showTooltip.value;
};

const focusInput = async () => {
  await nextTick();
  nameInput.value?.focus();
};

// Lifecycle
onMounted(() => {
  focusInput();
});

// Méthodes exposées pour le parent
defineExpose({
  focusInput,
  resetForm
});
</script>
