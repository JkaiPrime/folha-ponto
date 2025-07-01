// src/router/index.ts

import { defineRouter } from '#q-app/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'src/stores/auth';

let routerInstance: ReturnType<typeof createRouter>; // ✅ exportável

export default defineRouter(function () {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory);

  routerInstance = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE)
  });

  routerInstance.beforeEach((to, from, next) => {
    const auth = useAuthStore();

    if (to.path === '/') {
      if (auth.token) {
        next('/dashboard');
        return;
      } else {
        next();
        return;
      }
    }

    if (
      to.path.startsWith('/dashboard') ||
      to.path.startsWith('/editar') ||
      to.path.startsWith('/visualizar') ||
      to.path.startsWith('/excluir')
    ) {
      if (!auth.token) {
        next('/');
        return;
      }
    }

    next();
  });

  return routerInstance;
});

export { routerInstance as Router }; // ✅ exporta o router corretamente
