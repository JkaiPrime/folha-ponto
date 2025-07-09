<template>
  <q-page class="q-pa-md q-gutter-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Justificativa de Ponto</div>
      </q-card-section>

      <q-card-section>
        <q-input v-model="codigo" label="Código do colaborador" maxlength="6" mask="######" filled />
        <q-input v-model="texto" label="Justificativa" type="textarea" filled />
        <q-file v-model="arquivo" label="Anexar arquivo (PDF ou imagem)" filled />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn label="Enviar" color="primary" @click="enviarJustificativa" />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { Notify } from 'quasar'
import axios from 'axios'

const codigo = ref('')
const texto = ref('')
const arquivo = ref(null)

const enviarJustificativa = async () => {
  const formData = new FormData()
  formData.append('colaborador_id', codigo.value)
  formData.append('justificativa', texto.value)
  formData.append('arquivo', arquivo.value)

  try {
    await axios.post('http://localhost:8000/justificativas', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    Notify.create({ type: 'positive', message: 'Justificativa enviada com sucesso!' })
    texto.value = ''
    arquivo.value = null
  } catch (err) {
    Notify.create({ type: 'negative', message: 'Erro ao enviar justificativa' })
  }
}
</script>
