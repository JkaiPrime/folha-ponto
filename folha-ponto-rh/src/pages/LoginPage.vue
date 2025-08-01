<template>
  <q-page class="flex flex-center login-page">
    <q-card class="q-pa-lg login-card">
      <q-card-section class="text-center">
        <q-img
          src="src\assets\logo.svg"
          style="width: 80px; margin-bottom: 20px;"
          spinner-color="white"
        />
        <div class="text-h5 text-bold text-primary">Ponto X</div>
      </q-card-section>

      <q-card-section>
        <q-input
          filled
          dense
          v-model="email"
          label="Email"
          type="email"
          class="q-mb-md"
        />
        <q-input
          filled
          dense
          v-model="password"
          :type="isPwd ? 'password' : 'text'"
          label="Senha"
          class="q-mb-md"
        >
          <template v-slot:append>
            <q-icon
              :name="isPwd ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click="isPwd = !isPwd"
            />
          </template>
        </q-input>
      </q-card-section>

      <q-card-actions align="center">
        <q-btn
          label="Entrar"
          color="primary"
          size="lg"
          class="full-width"
          :loading="carregando"
          :disable="carregando"
          @click="handleLogin"
        />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'src/stores/auth';
import { Notify } from 'quasar';
import { api } from 'boot/axios';
import axios from 'axios';

const isPwd = ref(true);
const email = ref('');
const password = ref('');
const auth = useAuthStore();
const router = useRouter();
const carregando = ref(false);

async function handleLogin() {
  console.log('[DEBUG] Iniciando handleLogin...');
  carregando.value = true;

  try {
    const data = new URLSearchParams()
    data.append('username', email.value)
    data.append('password', password.value)

    await api.post('/auth/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      withCredentials: true
    })

    await auth.fetchUser()
    // Redireciona conforme papel do usuário
    if (auth.role === 'gestao') {
      void router.push('/dashboard')
    } else {
      void router.push('/bater-ponto')
    }

  } catch (err: unknown) {
    let mensagem = 'Erro ao tentar login.'
    if (axios.isAxiosError(err)) {
      const status = err.response?.status
      const detail = err.response?.data?.detail

      if (status === 402) {
        mensagem = detail || 'Credenciais inválidas.'
      } else if (status === 423) {
        mensagem = 'Conta bloqueada por múltiplas tentativas incorretas.'
      }
    }

    Notify.create({ type: 'negative', message: mensagem, position: 'top' })
  } finally {
    carregando.value = false;
  }
}

</script>


<style scoped>
.login-page {
  background: linear-gradient(to right, #1976d2, #42a5f5);
  min-height: 100vh;
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 360px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  background: white;
}
</style>
