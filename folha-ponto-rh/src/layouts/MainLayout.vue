<template>
  <q-layout view="hHh lpR fFf">
    <!-- HEADER -->
    <q-header v-if="mostrarMenu" elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          flat dense round icon="menu"
          aria-label="Abrir menu lateral"
          @click="drawer = !drawer"
        />

        <q-toolbar-title class="row items-center">
          <q-icon name="access_time" class="q-mr-sm" />
          <span>PontoX - Folha Ponto</span>
        </q-toolbar-title>

        <q-space />

        <q-btn flat dense icon="logout" label="Sair" @click="logout" class="q-ml-sm" />
      </q-toolbar>
    </q-header>

    <!-- SIDEBAR -->
    <q-drawer
      v-if="mostrarMenu"
      v-model="drawer"
      show-if-above
      side="left"
      :width="270"
      bordered
      elevated
      class="bg-white"
    >
      <q-scroll-area class="fit">
        <!-- Cartão com nome, email e cargo -->
        <div class="q-pa-md">
          <div class="drawer-card">
            <q-avatar size="40px" class="text-primary bg-primary-1">
              {{ firstLetter }}
            </q-avatar>
            <div class="q-ml-md column">
              <div class="text-body1 text-weight-medium ellipsis">{{ displayName }}</div>
              <div class="text-caption text-grey-7 ellipsis">{{ displayEmail }}</div>
              <div class="text-caption text-grey-6">{{ roleLabel }}</div>
            </div>
          </div>
        </div>

        <q-list padding class="q-pt-none">
          <!-- Funcionário -->
          <q-item clickable v-ripple :active="isActive('/bater-ponto')" @click="go('/bater-ponto')" class="nav-item">
            <div class="active-indicator" />
            <q-item-section avatar><q-icon name="punch_clock" size="22px" /></q-item-section>
            <q-item-section>
              <q-item-label class="text-body2">Bater Ponto</q-item-label>
              <q-item-label caption>Registre entradas/saídas</q-item-label>
            </q-item-section>
          </q-item>

          <q-item clickable v-ripple :active="isActive('/meus-pontos')" @click="go('/meus-pontos')" class="nav-item">
            <div class="active-indicator" />
            <q-item-section avatar><q-icon name="visibility" size="22px" /></q-item-section>
            <q-item-section>
              <q-item-label class="text-body2">Meus pontos</q-item-label>
              <q-item-label caption>Histórico e detalhes do seu dia</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator spaced />

          <!-- Gestão -->
          <template v-if="auth.role === 'gestao'">
            <q-item clickable v-ripple :active="isActive('/dashboard')" @click="go('/dashboard')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="analytics" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Dashboard</q-item-label>
                <q-item-label caption>Métricas e indicadores</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/visualizar')" @click="go('/visualizar')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="table_view" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Visualizar pontos</q-item-label>
                <q-item-label caption>Consulta por colaborador/período</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/editar')" @click="go('/editar')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="edit" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Editar pontos</q-item-label>
                <q-item-label caption>Ajustes e correções autorizadas</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/excluir')" @click="go('/excluir')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="delete" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Excluir pontos</q-item-label>
                <q-item-label caption>Remoção de registros inválidos</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/cadastrar-colaborador')" @click="go('/cadastrar-colaborador')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="person_add_alt_1" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Criar colaborador</q-item-label>
                <q-item-label caption>Cadastro básico e vínculo</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/criar-acesso')" @click="go('/criar-acesso')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="admin_panel_settings" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Acesso RH</q-item-label>
                <q-item-label caption>Gerenciamento de perfis e permissões</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/listar-colaboradores')" @click="go('/listar-colaboradores')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="groups" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Gerenciar colaboradores</q-item-label>
                <q-item-label caption>Lista, busca e ações rápidas</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/insert-ponto')" @click="go('/insert-ponto')" class="nav-item">
              <div class="active-indicator" />
              <q-item-section avatar><q-icon name="add_circle" size="22px" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Inserir ponto manual</q-item-label>
                <q-item-label caption>Registro manual para um usuário</q-item-label>
              </q-item-section>
            </q-item>
          </template>

          <q-separator spaced />

          <!-- Conta -->
          <q-item clickable v-ripple :active="isActive('/alterar-senha')" @click="go('/alterar-senha')" class="nav-item">
            <div class="active-indicator" />
            <q-item-section avatar><q-icon name="password" size="22px" /></q-item-section>
            <q-item-section>
              <q-item-label class="text-body2">Alterar Senha</q-item-label>
              <q-item-label caption>Atualize sua senha com segurança</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <!-- CONTEÚDO -->
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, getCurrentInstance } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import type { AxiosInstance } from 'axios'

/** Rotas públicas (sem header/drawer e sem fetch do /me) */
const PUBLIC_PATHS = ['/', '/reset-password', '/reset-password-link'] as const

const drawer = ref(false)
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

/** Exibe header/drawer somente fora das rotas públicas */
const isPublicRoute = computed<boolean>(() => {
  // meta.public em qualquer nível
  if (route.matched.some(r => r.meta?.public === true)) return true
  // paths explícitos
  return (PUBLIC_PATHS as readonly string[]).includes(route.path)
})
const mostrarMenu = computed<boolean>(() => !isPublicRoute.value)

/** Estado do “bem-vindo” */
const displayName = ref<string>('Usuário')
const displayEmail = ref<string>('')
const roleFromMe = ref<string | null>(null)

/** Logger simples (ativo só em dev) */
const DEBUG = import.meta.env.DEV
function log (...args: unknown[]) {
  if (DEBUG) console.log(...args)
}

/** Mapeia a role crua para rótulo amigável */
function mapRoleLabel (r: string): string {
  const v = (r || '').toLowerCase()
  if (['gestao', 'admin', 'administrador'].includes(v)) return 'Gestão'
  if (['funcionario', 'colaborador'].includes(v)) return 'Funcionário'
  return r || 'Usuário'
}

const rawRole = computed(() => roleFromMe.value || auth.role || '')
const roleLabel = computed(() => mapRoleLabel(rawRole.value))
const firstLetter = computed(() => (displayName.value?.[0] || 'U').toUpperCase())

/** Obtém Axios do boot ($api), se disponível */
function getAxiosFromBoot(): AxiosInstance | null {
  const inst = getCurrentInstance()
  const gp = inst?.appContext.config.globalProperties as Record<string, unknown> | undefined
  const candidate = gp?.$api
  return (candidate && typeof candidate === 'object') ? (candidate as AxiosInstance) : null
}

onMounted(async () => {
  // 🚫 Não toca em sessão nas rotas públicas
  if (isPublicRoute.value) {
    log('[MainLayout] rota pública, pulando fetch do usuário')
    return
  }

  // Carrega user do store se ainda não veio
  if (!auth.userLoaded && typeof auth.fetchUser === 'function') {
    try {
      await auth.fetchUser()
    } catch (err: unknown) {
      console.warn('[MainLayout] erro ao carregar usuário:', err)
    }
  }

  // Fallbacks
  displayName.value = 'Usuário'
  displayEmail.value = ''

  log('[MainLayout] route.path:', route.path)
  log('[MainLayout] auth info:', { role: auth.role, userLoaded: auth.userLoaded })

  // Busca /me/colaborador
  const api = getAxiosFromBoot()
  log('[MainLayout] usando $api do boot?', Boolean(api))

  try {
    console.groupCollapsed('[MainLayout] GET /me/colaborador')

    if (api) {
      const res = await api.get('/me/colaborador')
      log('status:', res.status)
      log('data:', res.data)
      const d: { nome?: string; email?: string; role?: string } = res.data ?? {}
      if (d.nome) displayName.value = d.nome
      if (d.email) displayEmail.value = d.email
      if (d.role) roleFromMe.value = d.role
    } else {
      const res = await fetch('/me/colaborador', { credentials: 'include' })
      log('status:', res.status)
      const data: { nome?: string; email?: string; role?: string } = await res.json()
      log('data:', data)
      if (data.nome) displayName.value = data.nome
      if (data.email) displayEmail.value = data.email
      if (data.role) roleFromMe.value = data.role
    }

    log('após set:', {
      displayName: displayName.value,
      displayEmail: displayEmail.value,
      rawRole: rawRole.value,
      roleLabel: roleLabel.value
    })
    console.groupEnd()
  } catch (err: unknown) {
    console.groupCollapsed('[MainLayout] ERRO /me/colaborador')
    log(err)
    console.groupEnd()
  }
})

function logout () {
  void auth.logout()
  void router.push('/')
}

function go (path: string) {
  drawer.value = false
  void router.replace(path)
}

function isActive (path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
/* Cartão topo do drawer */
.drawer-card {
  display: flex;
  align-items: center;
  background: var(--q-color-white);
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.04);
}

/* Item de navegação moderno */
.nav-item {
  position: relative;
  border-radius: 12px;
  margin: 4px 8px;
  padding: 6px 8px;
  transition: background 0.15s ease, transform 0.05s ease;
}
.nav-item:hover {
  background: rgba(0,0,0,0.04);
}
.nav-item:active {
  transform: translateY(1px);
}

/* Indicador ativo (faixa à esquerda) */
.nav-item .active-indicator {
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: 2px;
  background: transparent;
  transition: background 0.2s ease, width 0.2s ease;
}
.nav-item.q-item--active .active-indicator {
  background: var(--q-color-primary);
  width: 4px;
}

/* Ajuste estético do chip no header */
.bg-primary-10 { background: rgba(255,255,255,0.12); }
</style>
