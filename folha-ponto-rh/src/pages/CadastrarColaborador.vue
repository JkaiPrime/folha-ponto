<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Cadastrar novo colaborador</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-input v-model="nome" label="Nome do colaborador" filled dense class="q-mb-md" />
        <q-input v-model="code" label="Código do colaborador (ex: 00, 11, 22...)" filled dense class="q-mb-sm" />

        <div class="text-caption text-grey q-mb-md">
          Dicas:
          <ul>
            <li><strong>00</strong> - Administração</li>
            <li><strong>11</strong> - Suporte</li>
            <li><strong>22</strong> - Comercial</li>
          </ul>
        </div>

        <q-btn label="Cadastrar" color="primary" @click="cadastrar" :disable="!nome || !code" />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Notify } from 'quasar';
import { api } from 'boot/axios';
import { useAuthStore } from 'src/stores/auth';
import axios from 'axios';
const nome = ref('');
const code = ref('');
const auth = useAuthStore();

async function cadastrar() {
  try {
    await api.post('/colaboradores', {
      nome: nome.value,
      code: code.value
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    Notify.create({ type: 'positive', message: 'Colaborador cadastrado com sucesso' });
    nome.value = '';
    code.value = '';
  } catch (err) {
    let msg = 'Erro ao cadastrar';

    if (axios.isAxiosError(err) && err.response) {
      msg = err.response.data?.detail || msg;
    }

    Notify.create({ type: 'negative', message: msg });
  }
}
</script>
