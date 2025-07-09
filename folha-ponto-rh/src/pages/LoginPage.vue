<template>
  <q-page class="flex flex-center login-page">
    <q-card class="q-pa-lg login-card">
      <q-card-section class="text-center">
        <q-img
          src="src\assets\logo.svg"
          style="width: 80px; margin-bottom: 20px;"
          spinner-color="white"
        />
        <div class="text-h5 text-bold text-primary">Login RH</div>
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
          label="Senha"
          type="password"
          class="q-mb-md"
        />
      </q-card-section>

      <q-card-actions align="center">
        <q-btn
          label="Entrar"
          color="primary"
          size="lg"
          class="full-width"
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

const email = ref('');
const password = ref('');
const auth = useAuthStore();
const router = useRouter();

async function handleLogin() {
  try {
    const data = new URLSearchParams()
    data.append('username', email.value)
    data.append('password', password.value)

    const res = await api.post('/auth/login', data, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    await auth.login(res.data.access_token)

    Notify.create({
      type: 'positive',
      message: 'Login realizado com sucesso',
      position: 'top',
      timeout: 1500
    });

    setTimeout(() => {
      if (auth.role === 'gestao') {
        void router.push('/dashboard')
      } else {
        void router.push('/bater-ponto')
      }
    }, 1000);
  } catch (err: unknown) {
    let status = 0;
    let detail = '';

    if (
      typeof err === 'object' &&
      err !== null &&
      'response' in err &&
      typeof err.response === 'object' &&
      err.response !== null
    ) {
      const res = err.response as { status?: number; data?: { detail?: string } };
      status = res.status ?? 0;
      detail = res.data?.detail ?? '';
    }

    if (status === 423) {
      Notify.create({
        type: 'warning',
        message: 'Usuário bloqueado. Tente novamente mais tarde.',
        position: 'top',
        timeout: 4000
      });
    } else {
      Notify.create({
        type: 'negative',
        message: detail || 'Credenciais inválidas. Tente novamente.',
        position: 'top',
        timeout: 3000
      });
    }

    email.value = '';
    password.value = '';
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
