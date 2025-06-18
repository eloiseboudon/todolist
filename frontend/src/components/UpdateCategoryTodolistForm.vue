<template>
    <div :class="styles.updateCategoryForm">
        <div :class="styles.formOverlay" @click="closeForm"></div>

        <div :class="styles.formModal">
            <div :class="styles.formHeader">
                <h3>Modifier la catégorie</h3>
                <button @click="closeForm" :class="styles.btnClose">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="size-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <div :class="styles.formContent">
                <div :class="styles.currentTodolist">
                    <h4>{{ todolist.name }}</h4>
                    <p v-if="todolist.category" :class="styles.currentCategory">
                        Catégorie actuelle :
                        <span :style="{ color: todolist.category.color }">
                            {{ getCategoryIcon(todolist.category.icon) }} {{ todolist.category.name }}
                        </span>
                    </p>
                    <p v-else :class="styles.noCategory">Aucune catégorie assignée</p>
                </div>

                <!-- État de chargement -->
                <div v-if="loading" :class="styles.loading">
                    <div :class="styles.spinner">⏳</div>
                    <p>Chargement des catégories...</p>
                </div>

                <!-- Affichage des erreurs -->
                <div v-if="error" :class="styles.error">
                    <p>❌ {{ error }}</p>
                    <button @click="clearError" :class="styles.btnDismissError">Fermer</button>
                </div>

                <!-- Formulaire de sélection -->
                <form v-if="!loading" @submit.prevent="handleSubmit" :class="styles.form">
                    <div :class="styles.formGroup">
                        <label for="category-select" :class="styles.label">
                            Choisir une catégorie :
                        </label>

                        <select id="category-select" v-model="selectedCategoryId" :class="styles.categorySelect"
                            :disabled="saving">
                            <option v-for="category in categories" :key="category.id" :value="category.id">
                                {{ getCategoryIcon(category.icon) }} {{ category.name }}
                            </option>
                        </select>
                    </div>

                    <div :class="styles.formActions">
                        <button type="button" @click="closeForm" :class="styles.btnCancel" :disabled="saving">
                            Annuler
                        </button>
                        <button type="submit" :class="styles.btnSave" :disabled="saving || !hasChanged">
                            <span v-if="saving">⏳ Sauvegarde...</span>
                            <span v-else>💾 Enregistrer</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { categoriesApi, todoListsApi } from '@/services/api';
import { getCategoryIcon } from '@/composables/useCategory';
import { useNotifications } from '@/composables/useNotifications';
import styles from '@/styles/components/UpdateCategoryTodolistForm.module.css';
import type { TodoList, Category } from '@/services/api';

interface Props {
    todolist: TodoList;
}

interface Emits {
    close: [];
    updated: [todolist: TodoList];
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Notifications
const { success, error: notifyError } = useNotifications();

// État du composant
const categories = ref<Category[]>([]);
const selectedCategoryId = ref<number | ''>('');
const loading = ref(false);
const saving = ref(false);
const error = ref<string | null>(null);

// Computed
const selectedCategory = computed(() => {
    if (!selectedCategoryId.value) return null;
    return categories.value.find(cat => cat.id === selectedCategoryId.value) || null;
});

const hasChanged = computed(() => {
    const currentCategoryId = props.todolist.category?.id || '';
    return selectedCategoryId.value !== currentCategoryId;
});

// Méthodes
const loadCategories = async () => {
    loading.value = true;
    error.value = null;

    try {
        categories.value = await categoriesApi.getActive();

        // Initialiser la sélection avec la catégorie actuelle
        selectedCategoryId.value = props.todolist.category?.id || '';
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Erreur lors du chargement des catégories';
        console.error('Erreur chargement catégories:', err);
    } finally {
        loading.value = false;
    }
};

const handleSubmit = async () => {
    if (!hasChanged.value) {
        closeForm();
        return;
    }

    saving.value = true;
    error.value = null;

    try {
        const updateData = {
            name: props.todolist.name,
            category_id: selectedCategoryId.value || null
        };

        const updatedTodolist = await todoListsApi.update(props.todolist.id, updateData);
        emit('updated', updatedTodolist);
        success(
            'Catégorie mise à jour',
            selectedCategoryId.value
                ? `La catégorie "${selectedCategory.value?.name}" a été assignée à la TodoList`
                : 'La catégorie a été supprimée de la TodoList'
        );

        emit('updated', updatedTodolist);
        closeForm();
    } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la mise à jour';
        error.value = errorMessage;
        notifyError('Erreur de sauvegarde', errorMessage);
        console.error('Erreur mise à jour catégorie:', err);
    } finally {
        saving.value = false;
    }
};

const closeForm = () => {
    emit('close');
};

const clearError = () => {
    error.value = null;
};

// Lifecycle
onMounted(() => {
    loadCategories();
});
</script>