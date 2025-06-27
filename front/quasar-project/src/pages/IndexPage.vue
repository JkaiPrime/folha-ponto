<template>
  <q-page class="flex flex-center q-pa-lg bg-grey-2">
    <q-card class="q-pa-xl q-mt-md full-width" style="max-width: 800px">
      <div class="column q-gutter-xl">
        <!-- LOGO -->
        <div class="flex flex-center">
          <q-img src="src/assets/logo.svg" alt="Logo" style="max-width: 180px" />
        </div>

        <!-- RELÓGIO -->
        <div class="text-h4 text-primary text-center">{{ currentTime }}</div>

        <!-- INPUT + BOTÃO -->
        <div class="row q-col-gutter-md items-center">
          <div class="col">
            <q-input
              v-model="userInput"
              label="Digite os 6 dígitos"
              type="text"
              maxlength="6"
              outlined
              dense
              :disable="carregando"
              class="q-px-sm"
              style="font-size: 1.2rem"
              @input="validarInput"
              @keypress="permitirSomenteNumeros"
            />
          </div>
          <div class="col-auto">
            <q-btn
              label="Enviar"
              color="primary"
              size="lg"
              :loading="carregando"
              :disable="carregando"
              @click="enviarParaApi"
            />
          </div>
        </div>
      </div>
    </q-card>

    <!-- MODAL -->
    <q-dialog v-model="mostrarResposta">
      <q-card style="max-width: 90vw">
        <q-card-section class="text-h6">Resposta da API</q-card-section>
        <q-card-section>
          <pre>{{ respostaApi }}</pre>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';

const userInput = ref('');
const respostaApi = ref('');
const mostrarResposta = ref(false);
const currentTime = ref('');
const carregando = ref(false);
const inputValido = ref(false);

// Relógio
function atualizarRelogio() {
  const agora = new Date();
  currentTime.value = agora.toLocaleTimeString();
}

onMounted(() => {
  atualizarRelogio();
  setInterval(atualizarRelogio, 1000);
  validarInput();
});

// Validação: apenas 6 dígitos
function validarInput() {
  inputValido.value = /^\d{6}$/.test(userInput.value);
}

// Bloquear letras no teclado
function permitirSomenteNumeros(event: KeyboardEvent) {
  const key = event.key;
  if (!/^\d$/.test(key)) {
    event.preventDefault();
  }
}

// Toast de erro
function mostrarToast(mensagem: string) {
  Notify.create({
    type: 'negative',
    message: mensagem,
    timeout: 3000,
    position: 'top',
  });
}

// Envio
async function enviarParaApi() {
  if (!userInput.value.trim()) {
    mostrarToast('Digite um valor antes de enviar!');
    return;
  }

  carregando.value = true;
  try {
    const res = await fetch('http://localhost:8000/sua-rota', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ valor: userInput.value }),
    });

    if (!res.ok) {
      throw new Error(`Erro ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    respostaApi.value = JSON.stringify(data, null, 2);
    mostrarResposta.value = true;
  } catch (err: unknown) {
    if (err instanceof Error) {
      mostrarToast('Erro ao acessar a API: ' + err.message);
    } else {
      mostrarToast('Erro desconhecido ao acessar a API.');
    }
  } finally {
    carregando.value = false;
  }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
