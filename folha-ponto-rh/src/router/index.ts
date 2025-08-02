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

  routerInstance.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  console.log('[DEBUG] Navegando para:', to.path);

  // 🔹 Garante que os dados do usuário sejam carregados
  if (!auth.userLoaded) {
    await auth.fetchUser();
  }

  // ✅ Sempre permite a rota de login, mesmo se não estiver autenticado
  if (to.path === '/') {
    return next();
  }

  // Bloqueio de rotas que exigem autenticação
  if (to.meta.requiresAuth && (!auth.token && !auth.colaboradorId)) {
    console.warn('[DEBUG] Usuário sem sessão, redirecionando para login');
    return next('/');
  }

  // Bloqueio por papel
  if (to.meta.role && auth.role !== to.meta.role) {
    console.warn('[DEBUG] Acesso negado para role:', auth.role);
    return next('/acesso-negado');
  }

  next();
});


  return routerInstance;
});

export { routerInstance as Router };
