<template>
  <q-page class="q-pa-md q-gutter-md">
    <q-card class="q-pa-md" style="max-width: 600px; margin: auto;">
      <q-card-section>
        <div class="text-h6">Justificativa de Ponto</div>
      </q-card-section>

      <q-card-section>
        <q-field filled class="q-mb-md">
          <template #control>
            <div class="text-body1 text-primary">
              {{ nomeColaborador }} ({{ codigoColaborador }})
            </div>
          </template>
        </q-field>

        <q-input
          filled
          v-model="datasFormatadas"
          label="Datas da Justificativa"
          readonly
          class="q-mb-md"
        >
          <template #append>
            <q-icon name="event" class="cursor-pointer" @click="abrirCalendario = true" />
          </template>

          <q-popup-proxy
            cover
            transition-show="scale"
            transition-hide="scale"
            v-model="abrirCalendario"
          >
            <q-date
              v-model="datasSelecionadas"
              multiple
              mask="YYYY-MM-DD"
              color="primary"
              @update:model-value="atualizarDatasFormatadas"
            />
          </q-popup-proxy>
        </q-input>

        <q-input
          v-model="texto"
          label="Justificativa"
          type="textarea"
          filled
          class="q-mb-md"
        />

        <q-uploader
          label="Anexar arquivo"
          :auto-upload="false"
          accept=".pdf,image/*"
          class="q-mb-md"
          @added="onArquivoSelecionado"
        />

        <q-btn label="Enviar Justificativa" color="primary" @click="confirmarEnvio = true" />
      </q-card-section>
    </q-card>
  </q-page>
  <q-dialog v-model="confirmarEnvio">
  <q-card>
    <q-card-section class="text-h6">
      Confirmar envio da justificativa
    </q-card-section>

    <q-card-section>
      Essa ação não poderá ser corrigida pelo sistema. Se estiver errado, será necessário entrar em contato com o RH.
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat label="Cancelar" color="primary" v-close-popup />
      <q-btn flat label="Confirmar Envio" color="negative" @click="enviarJustificativaConfirmado" />
    </q-card-actions>
  </q-card>
</q-dialog>
</template>


<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Notify } from 'quasar'
import { api } from 'boot/axios'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const nomeColaborador = ref('')
const codigoColaborador = ref('')
const texto = ref('')

const arquivo = ref<File | null>(null)
const confirmarEnvio = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/me/colaborador')
    nomeColaborador.value = res.data.nome
    codigoColaborador.value = res.data.code
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaborador' })
  }
})
async function enviarJustificativaConfirmado() {
  confirmarEnvio.value = false
  await enviar()
}
const abrirCalendario = ref(false)
const datasSelecionadas = ref<string[]>([])
const datasFormatadas = ref('')

function atualizarDatasFormatadas() {
  datasFormatadas.value = datasSelecionadas.value.join(', ')
}

function onArquivoSelecionado(arquivos: readonly File[]) {
  arquivo.value = arquivos[0] || null
}

async function enviar() {
  if (!texto.value || !arquivo.value || datasSelecionadas.value.length === 0) {
    Notify.create({ type: 'warning', message: 'Preencha todos os campos' })
    return
  }

  const formData = new FormData()
  formData.append('colaborador_id', codigoColaborador.value)
  formData.append('justificativa', texto.value)
  formData.append('datas', datasSelecionadas.value.join(','))
  formData.append('arquivo', arquivo.value)

  try {
    await api.post('/justificativas', formData, {
      headers: {
        Authorization: `Bearer ${auth.token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    Notify.create({ type: 'positive', message: 'Justificativa enviada com sucesso!' })
    texto.value = ''
    arquivo.value = null
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao enviar justificativa' })
  }
}
</script>
