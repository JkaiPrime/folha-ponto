<template>
  <q-layout view="lHh Lpr lFf">
    <q-header v-if="mostrarMenu" elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          @click="drawer = !drawer"
        />
        <q-toolbar-title>
          RH - Painel de Controle
        </q-toolbar-title>
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

        <q-item clickable v-ripple @click="irPara('/dashboard')">
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-item clickable v-ripple @click="irPara('/visualizar')">
          <q-item-section avatar>
            <q-icon name="visibility" />
          </q-item-section>
          <q-item-section>Visualizar pontos</q-item-section>
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

const mostrarMenu = computed(() => route.path !== '/');

function irPara(path: string) {
  drawer.value = false;
  void router.push(path);
}
</script>
