import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Import des styles globaux
import './styles/global.css'

// Configuration du routeur
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('./views/Home.vue')
    },
    {
      path: '/todolist/:id',
      name: 'TodoListDetail',
      component: () => import('./views/TodoListDetail.vue'),
      props: true
    },
    {
      path: '/statistics',
      name: 'Statistics',
      component: () => import('./views/Statistics.vue')
    }
  ]
})

// Création et montage de l'application
const app = createApp(App)
app.use(router)
app.mount('#app')