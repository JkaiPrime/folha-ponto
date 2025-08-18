<template>
  <q-page class="q-pa-md flex flex-center">
    <q-card class="q-pa-md" style="width: 100%; max-width: 520px">
      <q-card-section>
        <div class="text-h6">Redefinir senha</div>
        <div class="text-subtitle2 text-grey-7">Defina uma nova senha para sua conta</div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-gutter-md">
        <q-banner v-if="!token" class="bg-orange-2 text-orange-10">
          O link não contém o token de redefinição. Cole abaixo o token recebido
          ou solicite um novo à gestão.
        </q-banner>

        <q-input
          v-model="token"
          label="Token de redefinição"
          filled dense stack-label
          :rules="[v => !!v || 'Informe o token (ou use o link enviado)']"
          autogrow
        >
          <template #append>
            <q-icon name="content_paste" />
          </template>
        </q-input>

        <q-input
          v-model="novaSenha"
          :type="mostrarSenha ? 'text' : 'password'"
          label="Nova senha"
          filled dense stack-label
          :rules="senhaRules"
        >
          <template #append>
            <q-icon
              :name="mostrarSenha ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click="mostrarSenha = !mostrarSenha"
            />
          </template>
        </q-input>

        <q-input
          v-model="confirmarSenha"
          :type="mostrarSenha ? 'text' : 'password'"
          label="Confirmar nova senha"
          filled dense stack-label
          :rules="[v => v === novaSenha || 'As senhas não coincidem']"
        />

        <q-linear-progress :value="forcaSenha" :color="forcaSenhaColor" size="8px" rounded />
        <div class="text-caption text-grey-7">
          Força da senha: <b>{{ forcaSenhaLabel }}</b>
        </div>

        <q-banner v-if="validando" class="bg-blue-1 text-blue-10">
          Validando link de redefinição…
        </q-banner>
        <q-banner v-else-if="!tokenValido" class="bg-orange-2 text-orange-10">
          Link inválido ou expirado. Cole um token válido ou solicite novo link.
        </q-banner>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Voltar ao login" @click="irLogin" />
        <q-btn
          label="Redefinir senha"
          color="primary"
          :loading="loading"
          :disable="!podeEnviar || !tokenValido"
          @click="resetar"
        />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Notify } from 'quasar'
import { api } from 'boot/axios'
import type { AxiosError } from 'axios'

const route = useRoute()
const router = useRouter()

const token = ref<string>('')
const novaSenha = ref<string>('')
const confirmarSenha = ref<string>('')

const mostrarSenha = ref(false)
const loading = ref(false)

const validando = ref(false)
const tokenValido = ref(true) // assume válido; validamos ao montar

onMounted(async () => {
  const q = route.query.token
  token.value = Array.isArray(q) ? (q?.[0] || '') : (q ?? '')

  if (!token.value) {
    tokenValido.value = false
    return
  }

  validando.value = true
  try {
    await api.post(
      '/auth/reset-password/validate',
      { token: token.value },
      { __skipAuthRedirect: true } // 👈 não redireciona pro login se 401 aqui
    )
    tokenValido.value = true
  } catch {
    tokenValido.value = false
    Notify.create({ type: 'warning', message: 'Link inválido ou expirado.' })
  } finally {
    validando.value = false
  }
})

/** Validações de senha */
const senhaRules = [
  (v: string) => !!v || 'Informe a nova senha',
  (v: string) => v.length >= 8 || 'Mínimo de 8 caracteres',
  (v: string) => /[A-Z]/.test(v) || 'Pelo menos 1 letra maiúscula',
  (v: string) => /[a-z]/.test(v) || 'Pelo menos 1 letra minúscula',
  (v: string) => /\d/.test(v) || 'Pelo menos 1 número',
  (v: string) => /[^A-Za-z0-9]/.test(v) || 'Pelo menos 1 símbolo'
]

/** Força da senha (feedback visual) */
const forcaSenha = computed(() => {
  let score = 0
  if (novaSenha.value.length >= 8) score++
  if (/[A-Z]/.test(novaSenha.value)) score++
  if (/[a-z]/.test(novaSenha.value)) score++
  if (/\d/.test(novaSenha.value)) score++
  if (/[^A-Za-z0-9]/.test(novaSenha.value)) score++
  return score / 5
})
const forcaSenhaLabel = computed(() => (forcaSenha.value < 0.4 ? 'Fraca' : forcaSenha.value < 0.8 ? 'Média' : 'Forte'))
const forcaSenhaColor = computed(() => (forcaSenha.value < 0.4 ? 'negative' : forcaSenha.value < 0.8 ? 'warning' : 'positive'))

const podeEnviar = computed(() =>
  !!token.value &&
  !!novaSenha.value &&
  confirmarSenha.value === novaSenha.value &&
  forcaSenha.value >= 0.4
)

async function resetar () {
  if (!podeEnviar.value || !tokenValido.value) return
  loading.value = true
  try {
    await api.post(
      '/auth/reset-password',
      { token: token.value, nova_senha: novaSenha.value },
      { __skipAuthRedirect: true } // 👈 idem
    )
    Notify.create({ type: 'positive', message: 'Senha redefinida com sucesso!' })
    irLogin()
  } catch (err: unknown) {
    const e = err as AxiosError<{ detail?: string }>
    let msg = e.response?.data?.detail || 'Erro ao redefinir senha'
    if (e.response?.status === 401) msg = 'Token expirado. Solicite um novo link.'
    if (e.response?.status === 400) msg = 'Token inválido.'
    Notify.create({ type: 'negative', message: msg })
  } finally {
    loading.value = false
  }
}

function irLogin () {
  void router.push({ path: '/' })
}
</script>
