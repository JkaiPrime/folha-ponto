<template>
  <q-layout view="lHh Lpr lFf">
    <q-header v-if="mostrarMenu" elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Abrir menu lateral"
          @click="drawer = !drawer"
        />
        <q-toolbar-title>PontoX - Folha Ponto</q-toolbar-title>
        <q-space />

        <q-btn
          flat
          dense
          icon="logout"
          label="Sair"
          @click="logout"
          class="q-ml-sm"
        />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-if="mostrarMenu"
      v-model="drawer"
      show-if-above
      bordered
    >
      <q-list padding>
        <q-item-label header class="text-grey-8 text-uppercase">
          Navegação
        </q-item-label>
        <q-item clickable v-ripple @click="irPara('/bater-ponto')">
          <q-item-section avatar><q-icon name="punch_clock" /></q-item-section>
          <q-item-section>Bater Ponto</q-item-section>
        </q-item>
        <!--
        <q-item clickable v-ripple @click="irPara('/justificativas')">
          <q-item-section avatar><q-icon name="fact_check" /></q-item-section>
          <q-item-section>Justificativas</q-item-section>
        </q-item>
        -->
        <q-item clickable v-ripple @click="irPara('/meus-pontos')">
          <q-item-section avatar><q-icon name="visibility" /></q-item-section>
          <q-item-section>Meus pontos</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/dashboard')">
          <q-item-section avatar><q-icon name="analytics" /></q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/visualizar')">
          <q-item-section avatar><q-icon name="visibility" /></q-item-section>
          <q-item-section>Visualizar pontos</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/editar')">
          <q-item-section avatar><q-icon name="edit" /></q-item-section>
          <q-item-section>Editar pontos</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/excluir')">
          <q-item-section avatar><q-icon name="delete" /></q-item-section>
          <q-item-section>Excluir pontos</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/cadastrar-colaborador')">
          <q-item-section avatar><q-icon name="person_add_alt_1" /></q-item-section>
          <q-item-section>Criar colaborador</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/criar-acesso')">
          <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
          <q-item-section>Gerenciamento do Acesso RH</q-item-section>
        </q-item>

        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/listar-colaboradores')">
          <q-item-section avatar><q-icon name="groups" /></q-item-section>
          <q-item-section>Gerenciar colaboradores</q-item-section>
        </q-item>
        
        <!--
        <q-item v-if="auth.role === 'gestao'" clickable v-ripple @click="irPara('/gerenciar-justificativa')">
          <q-item-section avatar><q-icon name="rule" /></q-item-section>
          <q-item-section>Gerenciar Justificativas</q-item-section>
        </q-item>
        -->
        <q-item clickable v-ripple @click="irPara('/reset-password')">
          <q-item-section avatar><q-icon name="password" /></q-item-section>
          <q-item-section>Alterar Senha</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const drawer = ref(false);
const router = useRouter();
const route = useRoute();

const mostrarMenu = computed<boolean>(() => route.path !== '/');

function irPara(path: string) {
  drawer.value = false;
  void router.push(path);
}
import { useAuthStore } from 'src/stores/auth';

const auth = useAuthStore();

function logout() {
  auth.logout();
  void router.push('/');
}
</script>
