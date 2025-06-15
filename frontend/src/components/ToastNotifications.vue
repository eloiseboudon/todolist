<template>
  <Teleport to="body">
    <div :class="styles.toastContainer">
      <TransitionGroup name="toast" tag="div">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="[
            styles.toast,
            styles[notification.type]
          ]"
          @click="removeNotification(notification.id)"
        >
          <!-- Icône -->
          <div :class="styles.toastIcon">
            <span v-if="notification.type === 'success'">✅</span>
            <span v-else-if="notification.type === 'error'">❌</span>
            <span v-else-if="notification.type === 'warning'">⚠️</span>
            <span v-else-if="notification.type === 'info'">ℹ️</span>
          </div>

          <!-- Contenu -->
          <div :class="styles.toastContent">
            <div :class="styles.toastTitle">
              {{ notification.title }}
            </div>
            <div 
              v-if="notification.message" 
              :class="styles.toastMessage"
            >
              {{ notification.message }}
            </div>
          </div>

          <!-- Bouton fermer -->
          <button 
            :class="styles.toastClose"
            @click.stop="removeNotification(notification.id)"
            aria-label="Fermer la notification"
          >
            ×
          </button>

          <!-- Barre de progression -->
          <div 
            v-if="!notification.persistent"
            :class="styles.progressBar"
            :style="{ animationDuration: `${notification.duration}ms` }"
          ></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useNotifications } from '@/composables/useNotifications';
import styles from '@/styles/components/ToastNotifications.module.css';

const { notifications, removeNotification } = useNotifications();
</script>