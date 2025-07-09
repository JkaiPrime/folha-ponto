<template>
  <q-page class="column flex flex-center q-pa-xl">
    <q-icon name="block" color="negative" size="80px" />
    <div class="text-h5 text-negative q-mt-md">
      Acesso Negado
    </div>
    <div class="text-subtitle2 q-mt-sm text-grey-7">
      Você não tem permissão para acessar esta página.
    </div>
    <q-btn
      class="q-mt-xl"
      color="primary"
      label="Voltar para o início"
      @click="voltar"
      icon="arrow_back"
      unelevated
    />
  </q-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()

function voltar() {
  void router.push('/bater-ponto')
}
</script>
