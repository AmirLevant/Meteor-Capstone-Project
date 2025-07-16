import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlowTest from '../views/PlowTest.vue'
import ManagerView from '../views/ManagerView.vue'
import DriverView from '../views/DriverView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/test',
      name: 'test',
      component: PlowTest,
    },
    {
      path: '/manager',
      name: 'manager',
      component: ManagerView
    },
    {
      path: '/driver',
      name: 'driver',
      component: DriverView
    }
  ],
})

export default router