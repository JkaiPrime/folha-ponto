<template>
  <q-page class="flex flex-center q-pa-lg bg-grey-2">
    <q-card class="q-pa-xl q-mt-md full-width" style="max-width: 600px">
      <div class="column q-gutter-xl">

        <!-- Logo -->
        <div class="flex flex-center">
          <q-img src="src/assets/logo.svg" alt="Logo" style="max-width: 180px;" />
        </div>

        <!-- Relógio -->
        <div class="text-h4 text-primary text-center">{{ currentTime }}</div>

        <!-- Input + Botão -->
        <div class="row q-col-gutter-md items-center">
          <div class="col">
            <q-input
              v-model="colaboradorId"
              label="ID do Colaborador"
              maxlength="6"
              outlined
              dense
              class="q-px-sm"
              :disable="carregando"
            />
          </div>
          <div class="col-auto">
            <q-btn
              label="Bater Ponto"
              color="primary"
              @click="baterPonto"
              :loading="carregando"
            />
          </div>
        </div>

        <!-- Resultado -->
        <div v-if="mensagem" class="text-center">
          <q-banner dense class="bg-green-2 text-black">
            {{ mensagem }}
          </q-banner>
        </div>

        <div v-if="erro" class="text-center">
          <q-banner dense class="bg-red-2 text-black">
            {{ erro }}
          </q-banner>
        </div>
      </div>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const colaboradorId = ref('')
const currentTime = ref('')
const mensagem = ref('')
const erro = ref('')
const carregando = ref(false)

function atualizarRelogio() {
  const agora = new Date()
  currentTime.value = agora.toLocaleTimeString()
}

onMounted(() => {
  atualizarRelogio()
  setInterval(atualizarRelogio, 1000)
})

async function baterPonto() {
  mensagem.value = ''
  erro.value = ''
  carregando.value = true

  try {
    const response = await fetch('http://localhost:8000/pontos/bater-ponto', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ colaborador_id: colaboradorId.value })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Erro ao bater ponto.')
    }

    mensagem.value = `✅ Ponto registrado: ${data.mensagem || 'sucesso'}`
  } catch (err) {
    if (err instanceof Error) {
    erro.value = `❌ ${err.message}`
    } else {
      erro.value = '❌ Erro desconhecido ao bater ponto.'
    }
  } finally {
    carregando.value = false
  }
}
</script>
