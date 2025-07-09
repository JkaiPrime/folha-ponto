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

let routerInstance: ReturnType<typeof createRouter>;

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

    // Redirecionamento da página de login
    if (to.path === '/') {
      if (auth.token) {
        next('/dashboard');
        return;
      } else {
        next();
        return;
      }
    }

    // Bloqueio de rotas que requerem autenticação
    if (to.meta.requiresAuth && !auth.token) {
      next('/');
      return;
    }

    // Bloqueio por papel (gestao ou funcionario)
    if (to.meta.role && auth.role !== to.meta.role) {
      next('/acesso-negado'); // Crie essa página para 403 ou use /bater-ponto
      return;
    }

    next();
  });

  return routerInstance;
});

export { routerInstance as Router };
