<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 600px;">
      <q-card-section>
        <div class="text-h6">Cadastrar novo colaborador</div>
      </q-card-section>

      <q-card-section class="q-gutter-md">
        <q-input v-model="codigo" label="Código do colaborador" filled dense class="q-mb-sm" />
        <q-select
          v-model="emailUsuario"
          :options="emailsUsuarios"
          label="Vincular a usuário (opcional)"
          filled
          dense
          emit-value
          map-options
          class="q-mb-md"
        />
        <q-input v-model="nome" label="Nome do colaborador" filled dense class="q-mb-md" />
        <q-btn label="Cadastrar" color="primary" @click="cadastrarColaborador" />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Notify } from 'quasar'
import { api } from 'boot/axios'
import { useAuthStore } from 'src/stores/auth'

const codigo = ref('')
const nome = ref('')
const emailUsuario = ref('')
const emailsUsuarios = ref<string[]>([])


interface UsuarioResponse {
  id: number;
  nome: string;
  email: string;
  role: string;
  locked: boolean;
}


const auth = useAuthStore()

onMounted(() => {
  void carregarUsuarios()
})

async function carregarUsuarios() {
  try {
    const res = await api.get('/auth/usuarios', {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    emailsUsuarios.value = (res.data as UsuarioResponse[]).map((u) => u.email)
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar usuários' })
  }
}

async function cadastrarColaborador() {
  if (!codigo.value || !nome.value) {
    Notify.create({ type: 'warning', message: 'Preencha todos os campos obrigatórios' })
    return
  }

  try {
    await api.post('/colaboradores', {
      email_usuario: emailUsuario.value,
      code: codigo.value,
      nome: nome.value
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })

    Notify.create({ type: 'positive', message: 'Colaborador cadastrado com sucesso' })
    codigo.value = ''
    nome.value = ''
    emailUsuario.value = ''
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao cadastrar colaborador' })
  }
}
</script>
