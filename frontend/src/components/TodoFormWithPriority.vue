<template>
  <div class="todo-form" :class="{ 'is-loading': isSubmitting }">
    <!-- Header avec titre et bouton de fermeture -->
    <div class="form-header">
      <h3 class="form-title">
        <span class="title-icon">➕</span>
        Ajouter une nouvelle tâche
      </h3>
      <button 
        type="button"
        @click="handleCancel"
        class="btn-close"
        title="Fermer le formulaire"
      >
        ✕
      </button>
    </div>
    
    <!-- Formulaire principal -->
    <div class="form-body">
      <!-- Champ nom (obligatoire) -->
      <div class="form-group">
        <label for="todoName" class="form-label">
          Nom de la tâche
          <span class="required-indicator">*</span>
        </label>
        <div class="input-wrapper">
          <input
            id="todoName"
            ref="todoNameInput"
            v-model="todoName"
            type="text"
            placeholder="Que voulez-vous accomplir ?"
            class="form-input"
            :class="{ 'has-error': nameError, 'is-valid': isNameValid }"
            @keydown.enter="handleSubmit"
            @keydown.escape="handleCancel"
            @input="validateName"
            @blur="validateName"
            maxlength="200"
            required
          />
          <div class="input-counter">{{ todoName.length }}/200</div>
        </div>
        
        <!-- Message d'erreur pour le nom -->
        <div v-if="nameError" class="error-message">
          {{ nameError }}
        </div>
        
        <!-- Message de validation pour le nom -->
        <div v-else-if="isNameValid && todoName.length > 0" class="success-message">
          ✓ Nom de tâche valide
        </div>
      </div>

      <!-- Bouton pour les options avancées -->
      <button
        type="button"
        @click="toggleAdvancedOptions"
        class="advanced-toggle"
        :class="{ 'is-expanded': showAdvanced }"
      >
        <span class="toggle-icon">{{ showAdvanced ? '🔽' : '▶️' }}</span>
        <span class="toggle-text">Options avancées</span>
        <span v-if="hasCustomPriority" class="option-badge">
          Priorité {{ customPriority }}
        </span>
      </button>

      <!-- Options avancées (avec animation) -->
      <Transition name="slide-down">
        <div v-if="showAdvanced" class="advanced-options">
          <!-- Section priorité -->
          <div class="option-section">
            <div class="section-header">
              <h4 class="section-title">🎯 Priorité personnalisée</h4>
              <p class="section-description">
                Choisissez où placer cette tâche dans votre liste
              </p>
            </div>

            <div class="priority-controls">
              <!-- Input priorité -->
              <div class="form-group">
                <label for="todoPriority" class="form-label">
                  Position souhaitée
                  <span class="optional-text">(optionnel)</span>
                </label>
                <input
                  id="todoPriority"
                  v-model.number="customPriority"
                  type="number"
                  min="1"
                  max="9999"
                  placeholder="Ex: 1 (première position)"
                  class="form-input priority-input"
                  :class="{ 'has-value': hasCustomPriority }"
                  @input="validatePriority"
                />
              </div>

              <!-- Boutons rapides de priorité -->
              <div class="priority-quick-buttons">
                <span class="quick-label">Raccourcis :</span>
                <button
                  type="button"
                  @click="setQuickPriority(1)"
                  class="btn-quick"
                  :class="{ 'is-active': customPriority === 1 }"
                >
                  🔥 Urgent (1)
                </button>
                <button
                  type="button"
                  @click="setQuickPriority(null)"
                  class="btn-quick"
                  :class="{ 'is-active': !hasCustomPriority }"
                >
                  📝 Normal (auto)
                </button>
              </div>
            </div>

            <!-- Aperçu de la priorité -->
            <div v-if="hasCustomPriority" class="priority-preview">
              <div class="preview-card">
                <div class="preview-header">
                  <span class="preview-icon">🎯</span>
                  <strong>Aperçu du placement</strong>
                </div>
                <p class="preview-text">
                  Cette tâche sera placée à la <strong>position {{ customPriority }}</strong> 
                  dans votre liste.
                </p>
                <p class="preview-note">
                  💡 Les autres tâches seront automatiquement reorganisées.
                </p>
              </div>
            </div>

            <!-- Message par défaut -->
            <div v-else class="default-behavior">
              <div class="default-card">
                <span class="default-icon">📋</span>
                <div class="default-text">
                  <strong>Comportement par défaut</strong>
                  <p>La tâche sera ajoutée en fin de liste des tâches actives.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Boutons d'action -->
      <div class="form-actions">
        <button
          type="button"
          @click="handleSubmit"
          :disabled="!canSubmit || isSubmitting"
          class="btn-submit"
          :class="{ 'is-loading': isSubmitting }"
        >
          <span v-if="isSubmitting" class="loading-spinner"></span>
          <span v-else class="submit-icon">✅</span>
          <span class="submit-text">
            {{ isSubmitting ? 'Création...' : 'Ajouter la tâche' }}
          </span>
        </button>
        
        <button
          type="button"
          @click="handleCancel"
          :disabled="isSubmitting"
          class="btn-cancel"
        >
          <span class="cancel-icon">↩️</span>
          Annuler
        </button>
      </div>
    </div>

    <!-- Aide contextuelle -->
    <div class="help-section">
      <details class="help-details">
        <summary class="help-summary">
          <span class="help-icon">❓</span>
          Comment utiliser la priorité ?
        </summary>
        <div class="help-content">
          <div class="help-grid">
            <div class="help-item">
              <strong>💡 Sans priorité</strong>
              <p>La tâche est ajoutée automatiquement en fin de liste des tâches actives.</p>
            </div>
            <div class="help-item">
              <strong>🎯 Avec priorité</strong>
              <p>La tâche est insérée exactement à la position demandée (1 = première position).</p>
            </div>
            <div class="help-item">
              <strong>🔄 Réorganisation</strong>
              <p>Les autres tâches sont automatiquement renumérotées pour maintenir l'ordre.</p>
            </div>
            <div class="help-item">
              <strong>⌨️ Raccourcis</strong>
              <p><kbd>Entrée</kbd> pour valider, <kbd>Échap</kbd> pour annuler.</p>
            </div>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue';

// ===== TYPES =====
interface Emits {
  addTodo: [name: string, priority?: number];
  cancel: [];
}

interface Props {
  autoFocus?: boolean;
  maxPriority?: number;
}

// ===== PROPS & EMITS =====
const props = withDefaults(defineProps<Props>(), {
  autoFocus: true,
  maxPriority: 9999
});

const emit = defineEmits<Emits>();

// ===== ÉTAT LOCAL =====
const todoName = ref('');
const customPriority = ref<number | null>(null);
const showAdvanced = ref(false);
const isSubmitting = ref(false);
const nameError = ref('');

// Refs pour les éléments DOM
const todoNameInput = ref<HTMLInputElement>();

// ===== COMPUTED =====
const hasCustomPriority = computed(() => 
  customPriority.value !== null && customPriority.value > 0
);

const isNameValid = computed(() => 
  todoName.value.trim().length >= 2 && !nameError.value
);

const canSubmit = computed(() => 
  isNameValid.value && !isSubmitting.value
);

// ===== VALIDATION =====
const validateName = () => {
  const name = todoName.value.trim();
  
  if (name.length === 0) {
    nameError.value = '';
    return;
  }
  
  if (name.length < 2) {
    nameError.value = 'Le nom doit contenir au moins 2 caractères';
    return;
  }
  
  if (name.length > 200) {
    nameError.value = 'Le nom ne peut pas dépasser 200 caractères';
    return;
  }
  
  // Vérifier les caractères interdits
  const forbiddenChars = ['<', '>', '"', "'", '&'];
  const hasForbiddenChars = forbiddenChars.some(char => name.includes(char));
  
  if (hasForbiddenChars) {
    nameError.value = 'Le nom contient des caractères non autorisés';
    return;
  }
  
  nameError.value = '';
};

const validatePriority = () => {
  if (customPriority.value !== null) {
    if (customPriority.value < 1) {
      customPriority.value = 1;
    } else if (customPriority.value > props.maxPriority) {
      customPriority.value = props.maxPriority;
    }
  }
};

// ===== MÉTHODES =====
const toggleAdvancedOptions = () => {
  showAdvanced.value = !showAdvanced.value;
  
  // Si on ferme les options avancées, on garde les valeurs
  // (l'utilisateur peut les rouvrir)
};

const setQuickPriority = (priority: number | null) => {
  customPriority.value = priority;
};

const handleSubmit = async () => {
  if (!canSubmit.value) return;
  
  validateName();
  if (nameError.value) return;
  
  isSubmitting.value = true;
  
  try {
    const name = todoName.value.trim();
    const priority = hasCustomPriority.value ? customPriority.value! : undefined;
    
    emit('addTodo', name, priority);
    
    // Reset du formulaire après succès
    resetForm();
    
  } catch (error) {
    console.error('Erreur lors de l\'ajout de la tâche:', error);
  } finally {
    isSubmitting.value = false;
  }
};

const handleCancel = () => {
  if (isSubmitting.value) return;
  
  resetForm();
  emit('cancel');
};

const resetForm = () => {
  todoName.value = '';
  customPriority.value = null;
  showAdvanced.value = false;
  nameError.value = '';
  isSubmitting.value = false;
};

// ===== MÉTHODES EXPOSÉES =====
const focusInput = async () => {
  await nextTick();
  todoNameInput.value?.focus();
};

// ===== GESTION DES RACCOURCIS CLAVIER =====
const handleGlobalKeydown = (event: KeyboardEvent) => {
  // Échap pour fermer le formulaire
  if (event.key === 'Escape' && !isSubmitting.value) {
    handleCancel();
  }
  
  // Ctrl/Cmd + Entrée pour soumettre rapidement
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    handleSubmit();
  }
};

// ===== WATCHERS =====
watch(todoName, () => {
  if (nameError.value) {
    validateName();
  }
});

// ===== LIFECYCLE =====
onMounted(() => {
  if (props.autoFocus) {
    focusInput();
  }
  
  // Ajouter les raccourcis clavier globaux
  document.addEventListener('keydown', handleGlobalKeydown);
});

onUnmounted(() => {
  // Nettoyer les event listeners
  document.removeEventListener('keydown', handleGlobalKeydown);
});

// ===== EXPOSE =====
defineExpose({
  focusInput,
  resetForm,
  todoName,
  hasCustomPriority
});
</script>

<style scoped>
/* ===== VARIABLES CSS ===== */
.todo-form {
  --primary-color: #3b82f6;
  --primary-hover: #2563eb;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --border-color: #d1d5db;
  --border-focus: #3b82f6;
  --bg-secondary: #f9fafb;
  --bg-card: #ffffff;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --border-radius: 8px;
  --transition: all 0.2s ease;
}

/* ===== STRUCTURE PRINCIPALE ===== */
.todo-form {
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  transition: var(--transition);
}

.todo-form.is-loading {
  pointer-events: none;
  opacity: 0.8;
}

/* ===== HEADER ===== */
.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.form-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 1.1em;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.btn-close:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

/* ===== BODY ===== */
.form-body {
  padding: 24px;
}

/* ===== GROUPES DE CHAMPS ===== */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.required-indicator {
  color: var(--danger-color);
  margin-left: 2px;
}

.optional-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 400;
  margin-left: 4px;
}

/* ===== INPUTS ===== */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  transition: var(--transition);
  background: var(--bg-card);
  color: var(--text-primary);
}

.form-input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.has-error {
  border-color: var(--danger-color);
}

.form-input.is-valid {
  border-color: var(--success-color);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.input-counter {
  position: absolute;
  right: 12px;
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--bg-card);
  padding: 2px 4px;
  border-radius: 4px;
}

.priority-input {
  max-width: 200px;
}

.priority-input.has-value {
  border-color: var(--warning-color);
  background: rgba(245, 158, 11, 0.05);
}

/* ===== MESSAGES ===== */
.error-message {
  font-size: 0.75rem;
  color: var(--danger-color);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-message::before {
  content: '⚠️';
}

.success-message {
  font-size: 0.75rem;
  color: var(--success-color);
  margin-top: 4px;
}

/* ===== TOGGLE OPTIONS AVANCÉES ===== */
.advanced-toggle {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 12px 16px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--text-primary);
  width: 100%;
  margin-bottom: 16px;
}

.advanced-toggle:hover {
  background: #f3f4f6;
  border-color: var(--border-focus);
}

.advanced-toggle.is-expanded {
  background: rgba(59, 130, 246, 0.05);
  border-color: var(--border-focus);
}

.toggle-icon {
  transition: transform 0.2s ease;
}

.toggle-text {
  flex: 1;
  text-align: left;
}

.option-badge {
  background: var(--warning-color);
  color: white;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

/* ===== OPTIONS AVANCÉES ===== */
.advanced-options {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e5e7eb;
}

.option-section {
  margin-bottom: 16px;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.section-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

/* ===== CONTRÔLES DE PRIORITÉ ===== */
.priority-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.priority-quick-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.btn-quick {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 6px 12px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-primary);
}

.btn-quick:hover {
  border-color: var(--border-focus);
  background: rgba(59, 130, 246, 0.05);
}

.btn-quick.is-active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* ===== APERÇUS ===== */
.priority-preview {
  margin-top: 16px;
}

.preview-card {
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--border-radius);
  padding: 16px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.875rem;
}

.preview-text {
  color: var(--text-primary);
  font-size: 0.875rem;
  margin: 0 0 8px 0;
}

.preview-note {
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin: 0;
}

.default-behavior {
  margin-top: 16px;
}

.default-card {
  background: rgba(107, 114, 128, 0.05);
  border: 1px solid rgba(107, 114, 128, 0.2);
  border-radius: var(--border-radius);
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.default-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.default-text strong {
  color: var(--text-primary);
  font-size: 0.875rem;
  display: block;
  margin-bottom: 4px;
}

.default-text p {
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin: 0;
}

/* ===== ACTIONS ===== */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-submit {
  flex: 1;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 20px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.875rem;
}

.btn-submit:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-submit:disabled {
  background: var(--text-muted);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-submit.is-loading {
  background: var(--text-muted);
}

.btn-cancel {
  background: white;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 12px 20px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
}

.btn-cancel:hover:not(:disabled) {
  background: var(--bg-secondary);
  border-color: var(--text-secondary);
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== LOADING SPINNER ===== */
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ===== AIDE ===== */
.help-section {
  background: #fef3c7;
  border-top: 1px solid #fde68a;
  padding: 16px 24px;
}

.help-details {
  font-size: 0.875rem;
}

.help-summary {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #92400e;
  font-weight: 500;
  list-style: none;
}

.help-summary::-webkit-details-marker {
  display: none;
}

.help-content {
  margin-top: 12px;
}

.help-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.help-item {
  background: rgba(255, 255, 255, 0.5);
  padding: 12px;
  border-radius: 6px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.help-item strong {
  color: #92400e;
  display: block;
  margin-bottom: 4px;
  font-size: 0.75rem;
}

.help-item p {
  color: #a16207;
  font-size: 0.75rem;
  margin: 0;
  line-height: 1.4;
}

kbd {
  background: #374151;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: monospace;
}

/* ===== ANIMATIONS ===== */
.slide-down-enter-active {
  transition: all 0.3s ease-out;
}

.slide-down-leave-active {
  transition: all 0.3s ease-in;
}

.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
  max-height: 0;
}

.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  transform: translateY(0);
  opacity: 1;
  max-height: 500px;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 640px) {
  .todo-form {
    border-radius: 0;
    margin: 0;
  }
  
  .form-header,
  .form-body,
  .help-section {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .help-grid {
    grid-template-columns: 1fr;
  }
  
  .priority-quick-buttons {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* ===== ACCESSIBILITÉ ===== */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}

.form-input:focus-visible,
.btn-submit:focus-visible,
.btn-cancel:focus-visible,
.btn-close:focus-visible,
.advanced-toggle:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}
</style>