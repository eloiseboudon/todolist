<template>
  <div id="app">
    <!-- Header de navigation -->
    <header :class="styles.header">
      <nav :class="styles.nav">
        <div class="app-logo">
          <router-link to="/" :class="styles.logo">
            <div class="mini-logo">T</div>
            <span class="app-title">TaskFlow</span>
          </router-link>
        </div>
        <div :class="styles.navLinks">
          <router-link to="/" :class="styles.navLink">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
            Accueil
          </router-link>
          <router-link to="/statistics" :class="styles.navLink">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
            </svg>
            Statistiques
          </router-link>
        </div>
      </nav>
    </header>

    <!-- Contenu principal -->
    <main :class="styles.main">
      <router-view />
    </main>

    <!-- Footer -->
    <footer :class="styles.footer">
      <p>Made with ❤️ using Vue.js + FastAPI</p>
    </footer>

    <!-- Notifications Toast -->
    <ToastNotifications />

    <!-- Modal de confirmation globale -->
    <ConfirmModal :show="confirmState.show" :type="confirmState.options.type" :title="confirmState.options.title"
      :message="confirmState.options.message" :details="confirmState.options.details"
      :confirm-text="confirmState.options.confirmText" :cancel-text="confirmState.options.cancelText"
      :loading-text="confirmState.options.loadingText" :loading="confirmState.loading" @confirm="handleConfirm"
      @cancel="handleCancel" />

    <button :class="styles.themeToggle" @click="toggleTheme">
      <span v-if="theme === 'light'">🌙</span>
      <span v-else>☀️</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import styles from '@/styles/App.module.css';
import ToastNotifications from '@/components/ToastNotifications.vue';
import ConfirmModal from '@/components/ConfirmModal.vue';
import { useConfirm } from '@/composables/useConfirm';
import { useTheme } from '@/composables/useTheme';

const { confirmState, handleConfirm, handleCancel } = useConfirm();
const { theme, toggleTheme } = useTheme();
</script>