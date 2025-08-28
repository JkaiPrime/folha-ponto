<template>
  <q-layout view="hHh lpR fFf">
    <!-- HEADER -->
    <q-header v-if="mostrarMenu" elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Abrir menu lateral" @click="drawer = !drawer" />
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
            <div class="row items-center no-wrap">
              <template v-if="loadingMe">
                <q-skeleton type="QAvatar" size="40px" />
                <div class="q-ml-md" style="min-width: 0">
                  <q-skeleton type="text" width="140px" />
                  <q-skeleton type="text" width="180px" />
                  <q-skeleton type="text" width="80px" />
                </div>
              </template>

              <template v-else>
                <q-avatar size="40px" class="text-primary bg-primary-1">
                  {{ firstLetter }}
                </q-avatar>

                <div class="q-ml-md column" style="min-width: 0">
                  <div class="row items-center no-wrap">
                    <div class="text-body1 text-weight-medium ellipsis">
                      {{ displayName }}
                    </div>
                    <!--
                    <q-badge v-if="displayCode" class="q-ml-sm" outline align="middle">
                      {{ displayCode }}
                    </q-badge>
                    -->
                  </div>
                  <!--
                  <div class="text-caption text-grey-7 ellipsis">
                    {{ displayEmail }}
                  </div>
                  -->
                  <div class="row items-center q-gutter-xs q-mt-xs">
                    <q-badge :color="roleColor" text-color="white" outline class="text-caption">
                      {{ roleLabel }}
                    </q-badge>
                    <!--
                    <q-badge v-if="displayId !== null" color="grey-4" text-color="dark" outline class="text-caption">
                      ID: {{ displayId }}
                    </q-badge>
                    -->
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- MENU -->
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
          <template v-if="isGestao">
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
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from 'boot/axios'
import { useAuthStore, type Role, type MeColaborador } from 'src/stores/auth'

/** Rotas públicas (sem header/drawer) */
const PUBLIC_PATHS = ['/', '/reset-password', '/reset-password-link'] as const

const drawer = ref(false)
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const isPublicRoute = computed<boolean>(() =>
  route.matched.some(r => r.meta?.public === true) ||
  (PUBLIC_PATHS as readonly string[]).includes(route.path)
)
const mostrarMenu = computed<boolean>(() => !isPublicRoute.value)

/** Estado local (fallback) */
const loadingMe = ref(false)
const meLocal = ref<Partial<MeColaborador>>({})

/** Preferimos STORE; local é só backup */
const displayName = computed<string>(() =>
  (auth.me?.nome && auth.me.nome.length > 0 ? auth.me.nome : (meLocal.value.nome ?? 'Usuário'))
)
/*
const displayEmail = computed<string>(() =>
  (auth.me?.email && auth.me.email.length > 0 ? auth.me.email : (meLocal.value.email ?? ''))
)
  */
/*
const displayCode = computed<string | null>(() =>
  (auth.me?.code ?? meLocal.value.code ?? null) as string
)
  */
 /*
const displayId = computed<number | null>(() => {
  const idStore = auth.me?.id
  const idLocal = meLocal.value.id
  return (typeof idStore === 'number' ? idStore : (typeof idLocal === 'number' ? idLocal : null))
})
*/
const roleRaw = computed<Role | null>(() => (auth.me?.role ?? auth.role ?? meLocal.value.role ?? null) as Role)
const isGestao = computed<boolean>(() => {
  const r = roleRaw.value
  return r === 'gestao' || r === 'admin' || r === 'administrador'
})
const roleLabel = computed<string>(() => {
  const r = roleRaw.value
  if (r === 'gestao' || r === 'admin' || r === 'administrador') return 'Gestão'
  if (r === 'funcionario') return 'Funcionário'
  return 'Usuário'
})
const roleColor = computed<'primary' | 'secondary' | 'grey'>(() => {
  const r = roleRaw.value
  if (r === 'gestao' || r === 'admin' || r === 'administrador') return 'primary'
  if (r === 'funcionario') return 'secondary'
  return 'grey'
})
const firstLetter = computed(() => (displayName.value?.[0] || 'U').toUpperCase())

/** Garante que temos /me/colaborador no store; se não, busca e preenche ambos */
async function ensureMe(): Promise<void> {
  if (auth.userLoaded && auth.me?.nome && auth.me?.email) {
    return
  }
  loadingMe.value = true
  try {
    const res = await api.get<Partial<MeColaborador>>('/me/colaborador', { withCredentials: true })
    meLocal.value = res.data ?? {}
    // Ao setar no store, NUNCA passa role: undefined (store já cuida disso)
    auth.setMe(res.data ?? {})
  } catch {
    meLocal.value = {}
  } finally {
    loadingMe.value = false
  }
}

onMounted(async () => {
  if (isPublicRoute.value) return

  if (!auth.userLoaded) {
    await auth.fetchUser().catch(() => void 0)
  }
  await ensureMe()
})

function logout () {
  void api.post('/auth/logout', {}, { withCredentials: true })
    .finally(() => {
      void auth.logout()
      void router.push('/')
    })
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
.nav-item:hover { background: rgba(0,0,0,0.04); }
.nav-item:active { transform: translateY(1px); }

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
</style>
