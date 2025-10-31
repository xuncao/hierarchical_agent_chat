import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/chat/index.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Chat',
      component: Chat
    },
    {
      path: '/conversation/:id',
      name: 'Conversation',
      component: Chat,
      props: true
    }
  ],
})

export default router
