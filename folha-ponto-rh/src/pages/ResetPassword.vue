<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 400px;">
      <q-card-section>
        <div class="text-h6">Alterar Senha</div>
      </q-card-section>

      <q-input
        filled
        v-model="newPassword"
        :type="isPwd ? 'password' : 'text'"
        label="Nova Senha"
        class="q-mb-md"
      >
        <template v-slot:append>
          <q-icon :name="isPwd ? 'visibility_off' : 'visibility'" @click="isPwd = !isPwd" />
        </template>
      </q-input>

      <q-input
        filled
        v-model="confirmPassword"
        :type="isPwdConfirm ? 'password' : 'text'"
        label="Confirmar Senha"
        class="q-mb-md"
      >
        <template v-slot:append>
          <q-icon :name="isPwdConfirm ? 'visibility_off' : 'visibility'" @click="isPwdConfirm = !isPwdConfirm" />
        </template>
      </q-input>

      <q-btn label="Alterar Senha" color="primary" @click="alterarSenha" :loading="loading" />
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

const newPassword = ref('')
const confirmPassword = ref('')
const isPwd = ref(true)
const isPwdConfirm = ref(true)
const loading = ref(false)
const auth = useAuthStore()

const alterarSenha = async () => {
  if (newPassword.value !== confirmPassword.value) {
    Notify.create({ type: 'negative', message: 'As senhas não coincidem' })
    return
  }
  loading.value = true
  try {
    await api.put('/auth/alterar-senha', null, {
      params: { new_password: newPassword.value },
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    Notify.create({ type: 'positive', message: 'Senha alterada com sucesso' })
    newPassword.value = ''
    confirmPassword.value = ''
  }catch {
    Notify.create({ type: 'negative', message: 'Erro ao alterar senha' })
  } finally {
    loading.value = false
  }
}
</script>
