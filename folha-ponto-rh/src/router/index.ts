// src/router/index.ts
import { defineRouter } from '#q-app/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
  type RouteLocationNormalized
} from 'vue-router'
import routes from './routes'
import { useAuthStore } from 'src/stores/auth'

let routerInstance: ReturnType<typeof createRouter>

/** Rotas públicas (não exigem sessão) */
const PUBLIC_PATHS = new Set<string>(['/', '/reset-password', '/reset-password-link'])

function isPublicRoute (to: RouteLocationNormalized): boolean {
  // Se qualquer nível da rota tiver meta.public, é pública
  if (to.matched.some(r => r.meta?.public === true)) return true
  // Se o caminho completo estiver listado como público, também é
  if (PUBLIC_PATHS.has(to.path)) return true
  return false
}

export default defineRouter(function () {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history'
        ? createWebHistory
        : createWebHashHistory)

  routerInstance = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  routerInstance.beforeEach(async (to, _from, next) => {
    const auth = useAuthStore()
    // console.log('[DEBUG] Navegando para:', to.fullPath)

    // 🔓 Rotas públicas passam direto (sem fetchUser/validações)
    if (isPublicRoute(to)) {
      return next()
    }

    // 🔐 Carrega usuário se necessário
    if (!auth.userLoaded && typeof auth.fetchUser === 'function') {
      try {
        await auth.fetchUser()
      } catch (e) {
        console.warn('[DEBUG] fetchUser falhou:', e)
      }
    }

    // 🔒 Bloqueia rotas que exigem autenticação
    if (to.meta?.requiresAuth) {
      const hasSession = Boolean(auth.role || auth.colaboradorId)
      if (!hasSession) {
        // console.warn('[DEBUG] Sem sessão -> login')
        return next({ path: '/' })
      }
    }

    // 🧩 Restringe por papel quando meta.role estiver definido
    if (to.meta?.role) {
      if (auth.role !== to.meta.role) {
        console.warn('[DEBUG] Role inválida. Esperada:', to.meta.role, 'Atual:', auth.role)
        return next({ path: '/acesso-negado' })
      }
    }

    return next()
  })

  return routerInstance
})

export { routerInstance as Router }
