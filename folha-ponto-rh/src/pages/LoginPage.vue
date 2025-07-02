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

const email = ref('');
const password = ref('');
const auth = useAuthStore();
const router = useRouter();

async function handleLogin() {
  try {
    Notify.create({
      type: 'info',
      message: 'Iniciando o login...',
      position: 'top',
      timeout: 1000,
      group: false
    });

    await auth.login(email.value, password.value);

    Notify.create({
      type: 'positive',
      message: 'Login realizado com sucesso',
      position: 'top',
      timeout: 1500
    });

    setTimeout(() => {
        void router.push('/dashboard');
    }, 1000);
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Credenciais inválidas. Tente novamente.',
      position: 'top',
      timeout: 3000
    });
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
