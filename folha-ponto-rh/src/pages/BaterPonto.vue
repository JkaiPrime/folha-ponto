<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 500px;">
      <q-card-section class="text-center">
        <img src="src/assets/logo.svg" alt="Logo" style="max-width: 150px;" />
        <div class="text-h5 q-mt-sm">{{ horaAtual }}</div>
      </q-card-section>

      <q-card-section>
        <q-field filled class="q-mb-md">
          <template #control>
            <div class="text-body1 text-primary">
              {{ nomeColaborador }} ({{ codigoColaborador }})
            </div>
          </template>
        </q-field>

        <q-btn label="BATER PONTO" color="primary" class="full-width" @click="baterPonto" />

        <q-banner
          v-if="mensagemErro"
          class="bg-red-1 text-red q-mt-md"
          rounded
        >
          <q-icon name="error" color="red" class="q-mr-sm" />
          {{ mensagemErro }}
        </q-banner>

        <q-banner
          v-if="mensagemSucesso"
          class="bg-green-1 text-green q-mt-md"
          rounded
        >
          <q-icon name="check_circle" color="green" class="q-mr-sm" />
          {{ mensagemSucesso }}
        </q-banner>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import dayjs from 'dayjs'

const horaAtual = ref(dayjs().format('HH:mm:ss'))
const mensagemErro = ref('')
const mensagemSucesso = ref('')

const nomeColaborador = ref('')
const codigoColaborador = ref('')
const auth = useAuthStore()

onMounted(async () => {
  atualizarHora()
  try {
    const res = await api.get('/me/colaborador', {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    nomeColaborador.value = res.data.nome
    codigoColaborador.value = res.data.code
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaborador' })
  }
})

function atualizarHora() {
  setInterval(() => {
    horaAtual.value = dayjs().format('HH:mm:ss')
  }, 1000)
}

async function baterPonto() {
  mensagemErro.value = ''
  mensagemSucesso.value = ''

  if (!codigoColaborador.value) {
    mensagemErro.value = 'Código do colaborador não encontrado.'
    return
  }

  try {
    const res = await api.post('/pontos/bater-ponto', {
      colaborador_id: codigoColaborador.value
    }, {
      headers: {
        Authorization: `Bearer ${auth.token}`
      }
    })

    if (res?.data?.tipo) {
      mensagemSucesso.value = `Ponto registrado com sucesso: ${res.data.tipo.toUpperCase()}`
    } else {
      mensagemSucesso.value = 'Ponto registrado com sucesso.'
    }

  } catch (err: unknown) {
    console.error(err)
    mensagemErro.value = 'Erro ao registrar ponto. Verifique sua conexão ou tente novamente.'
  }
}

</script>
