<template>
  <q-layout view="hHh lpR fFf">
    <!-- HEADER -->
    <q-header v-if="mostrarMenu" elevated class="bg-primary text-white">
      <q-toolbar>
        <!-- Botão menu -->
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Abrir menu lateral"
          @click="drawer = !drawer"
        />
        <q-toolbar-title class="row items-center">
          <q-icon name="access_time" class="q-mr-sm" />
          <span>PontoX - Folha Ponto</span>
        </q-toolbar-title>
        <q-space />

        <!-- Botão de sair com tooltip -->
        <q-btn
          flat
          dense
          icon="logout"
          label="Logout"
          @click="logout"
          class="q-ml-sm text-weight-bold"
        >
          <q-tooltip>Sair</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <!-- SIDEBAR -->
    <q-drawer
      v-if="mostrarMenu"
      v-model="drawer"
      behavior="desktop"
      side="left"
      :width="280"
      bordered
      elevated
      class="bg-white"
    >
      <q-scroll-area class="fit">
        <!-- Card do usuário -->
        <div class="q-pa-md">
          <div class="drawer-card">
            <div class="row items-center no-wrap full-width">
              <template v-if="loadingMe">
                <q-skeleton type="QAvatar" size="48px" />
                <div class="q-ml-md col">
                  <q-skeleton type="text" width="120px" />
                  <q-skeleton type="text" width="80px" />
                </div>
              </template>

              <template v-else>
                <!-- Avatar com iniciais -->
                <q-avatar size="48px" class="avatar-gradient text-bold">
                  {{ initials }}
                </q-avatar>

                <div class="q-ml-md col ellipsis-area">
                  <!-- Nome -->
                  <div class="text-subtitle1 text-weight-medium ellipsis">
                    {{ displayName }}
                  </div>

                  <!-- Cargo -->
                  <div class="text-caption text-weight-bold text-dark q-mt-xs">
                    {{ cargoLabel }}
                  </div>

                  <!-- Papel -->
                  <div class="row items-center q-gutter-xs q-mt-xs">
                    <q-icon :name="roleIcon" :color="roleColor" size="18px" />
                    <q-badge
                      :color="roleColor"
                      text-color="white"
                      class="text-caption text-weight-bold"
                    >
                      {{ roleLabel }}
                    </q-badge>
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
            <div class="active-indicator"></div>
            <q-item-section avatar>
              <q-icon name="punch_clock" size="22px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-body2">Bater Ponto</q-item-label>
              <q-item-label caption>Registre entradas/saídas</q-item-label>
            </q-item-section>
          </q-item>

          <q-item clickable v-ripple :active="isActive('/meus-pontos')" @click="go('/meus-pontos')" class="nav-item">
            <div class="active-indicator"></div>
            <q-item-section avatar>
              <q-icon name="visibility" size="22px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-body2">Meus pontos</q-item-label>
              <q-item-label caption>Histórico e detalhes do seu dia</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator spaced />

          <!-- Gestão -->
          <template v-if="isGestao">
            <q-item clickable v-ripple :active="isActive('/dashboard')" @click="go('/dashboard')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="analytics" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Dashboard</q-item-label>
                <q-item-label caption>Métricas e indicadores</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/visualizar')" @click="go('/visualizar')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="table_view" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Visualizar pontos</q-item-label>
                <q-item-label caption>Consulta por colaborador/período</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/editar')" @click="go('/editar')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="edit" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Editar pontos</q-item-label>
                <q-item-label caption>Ajustes e correções autorizadas</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/excluir')" @click="go('/excluir')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="delete" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Excluir pontos</q-item-label>
                <q-item-label caption>Remoção de registros inválidos</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/criar-acesso')" @click="go('/criar-acesso')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="admin_panel_settings" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Acesso RH</q-item-label>
                <q-item-label caption>Gerenciamento de perfis e permissões</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/listar-colaboradores')" @click="go('/listar-colaboradores')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="groups" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Gerenciar colaboradores</q-item-label>
                <q-item-label caption>Lista, busca e ações rápidas</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-ripple :active="isActive('/insert-ponto')" @click="go('/insert-ponto')" class="nav-item">
              <div class="active-indicator"></div>
              <q-item-section avatar>
                <q-icon name="add_circle" size="22px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-body2">Inserir ponto manual</q-item-label>
                <q-item-label caption>Registro manual para um usuário</q-item-label>
              </q-item-section>
            </q-item>
          </template>

          <q-separator spaced />

          <!-- Conta -->
          <q-item clickable v-ripple :active="isActive('/alterar-senha')" @click="go('/alterar-senha')" class="nav-item">
            <div class="active-indicator"></div>
            <q-item-section avatar>
              <q-icon name="password" size="22px" />
            </q-item-section>
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
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api } from 'boot/axios';
import { useAuthStore, type Role, type MeColaborador } from 'src/stores/auth';
import { LoadingBar } from 'quasar';

const PUBLIC_PATHS = ['/', '/reset-password', '/reset-password-link'] as const;
const drawer = ref(false);
const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

router.beforeEach(() => LoadingBar.start());
router.afterEach(() => LoadingBar.stop());

const isPublicRoute = computed(() => {
  const hasMeta = route.matched.some(r => r.meta?.public === true);
  const isListed = (PUBLIC_PATHS as readonly string[]).includes(route.path);
  return hasMeta || isListed;
});
const mostrarMenu = computed(() => !isPublicRoute.value);

const loadingMe = ref(false);
const meLocal = ref<Partial<MeColaborador>>({});

const displayName = computed(() => auth.me?.nome || meLocal.value.nome || 'Usuário');

const roleRaw = computed<Role | null>(() => {
  const val = auth.me?.role ?? auth.role ?? meLocal.value.role;
  return typeof val === 'string' ? val: null;
});

const cargoRaw = computed(() => auth.me?.cargo ?? meLocal.value.cargo ?? null);

const isGestao = computed(() => ['gestao', 'admin', 'administrador'].includes(roleRaw.value || ''));

const roleLabel = computed(() => {
  const r = roleRaw.value;
  if (['gestao', 'admin', 'administrador'].includes(r || '')) return 'Gestão';
  if (r === 'funcionario') return 'Funcionário';
  if (r === 'estagiario') return 'Estagiário';
  return 'Usuário';
});

const roleColor = computed(() => {
  const r = roleRaw.value;
  if (['gestao', 'admin', 'administrador'].includes(r || '')) return 'primary';
  if (r === 'funcionario') return 'secondary';
  if (r === 'estagiario') return 'orange-6';
  return 'grey';
});

const roleIcon = computed(() => {
  const r = roleRaw.value;
  if (['gestao', 'admin', 'administrador'].includes(r || '')) return 'workspace_premium';
  if (r === 'funcionario') return 'badge';
  if (r === 'estagiario') return 'school';
  return 'help_outline';
});

const cargoLabel = computed(() => cargoRaw.value?.trim() || 'Cargo não definido');

/** Iniciais do nome + sobrenome */
const initials = computed(() => {
  const parts = displayName.value?.trim().split(' ') ?? [];
  const first = parts[0]?.[0] ?? 'U';
  const last = parts.length > 1 ? parts.at(-1)?.[0] ?? '' : '';
  return (first + last).toUpperCase();
});


const shouldFetchMe = computed(() => {
  const hasNomeEmail = Boolean(auth.me?.nome && auth.me?.email);
  const cargoDefined = typeof auth.me?.cargo !== 'undefined';
  return !hasNomeEmail || !cargoDefined;
});

async function ensureMe() {
  if (isPublicRoute.value || !shouldFetchMe.value) return;
  loadingMe.value = true;
  try {
    const res = await api.get<Partial<MeColaborador>>('/me/colaborador', { withCredentials: true });
    meLocal.value = res.data ?? {};
    auth.setMe(res.data ?? {});
  } catch {
    meLocal.value = {};
  } finally {
    loadingMe.value = false;
  }
}

onMounted(async () => {
  if (isPublicRoute.value) return;
  if (!auth.userLoaded) {
    try {
      await auth.fetchUser();
    } catch(err) {console.log("Error:", err)}
  }
  await ensureMe();
});

function logout() {
  void api.post('/auth/logout', {}, { withCredentials: true }).finally(() => {
    void auth.logout();
    void router.push('/');
  });
}

function go(path: string) {
  drawer.value = false;
  void router.replace(path);
}

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/');
}
</script>

<style scoped>
.drawer-card {
  display: flex;
  align-items: center;
  background: var(--q-color-white);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.drawer-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.avatar-gradient {
  background: linear-gradient(135deg, var(--q-color-primary), var(--q-color-secondary));
  color: #000;            /* letras escuras */
  font-weight: 800;       /* negrito */
  text-transform: uppercase;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ellipsis-area { min-width: 0; }
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-item {
  position: relative;
  border-radius: 12px;
  margin: 4px 8px;
  padding: 6px 8px;
  transition: background 0.15s ease, transform 0.05s ease, box-shadow 0.15s ease;
}
.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.06);
}
.nav-item:active { transform: translateY(1px); }
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
.q-header .q-toolbar {
  backdrop-filter: saturate(1.2) blur(2px);
}
</style>
