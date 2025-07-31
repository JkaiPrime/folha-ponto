<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md" style="max-width: 400px; margin: auto;">
      <q-card-section>
        <div class="text-h6">Redefinir Senha</div>
      </q-card-section>

      <q-input filled v-model="email" label="E-mail" type="email" class="q-mb-md" />

      <q-input
        v-model="newPassword"
        :type="isPwd ? 'password' : 'text'"
        label="Nova Senha"
        filled
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

      <q-input
        v-model="confirmPassword"
        :type="isPwdConfirm ? 'password' : 'text'"
        label="Confirmar Senha"
        filled
        class="q-mb-md"
      >
        <template v-slot:append>
          <q-icon
            :name="isPwdConfirm ? 'visibility_off' : 'visibility'"
            class="cursor-pointer"
            @click="isPwdConfirm = !isPwdConfirm"
          />
        </template>
      </q-input>

      <q-btn
        label="Redefinir"
        color="primary"
        @click="resetPassword"
        :loading="loading"
        class="full-width"
      />
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import type { AxiosError } from 'axios'

const email = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const isPwd = ref(true)
const isPwdConfirm = ref(true)

const resetPassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    Notify.create({ type: 'negative', message: 'Senhas não coincidem' })
    return
  }
  loading.value = true
  try {
    await api.put('/auth/reset-password', null, {
      params: { email: email.value, new_password: newPassword.value }
    })
    Notify.create({ type: 'positive', message: 'Senha redefinida com sucesso!' })
    email.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (error: unknown) {
    const err = error as AxiosError<{ detail?: string }>
    Notify.create({ type: 'negative', message: err.response?.data?.detail || 'Erro ao redefinir senha' })
  } finally {
    loading.value = false
  }
}
</script>
