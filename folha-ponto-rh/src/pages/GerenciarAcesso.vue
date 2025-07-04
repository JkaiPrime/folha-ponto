<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 600px;">
      <q-card-section>
        <div class="text-h6">Cadastrar novo usuário</div>
      </q-card-section>
      <q-card-section>
        <q-input v-model="nome" label="Nome" filled dense class="q-mb-sm" />
        <q-input v-model="email" label="Email" type="email" filled dense class="q-mb-sm" />
        <q-input v-model="senha" label="Senha" type="password" filled dense class="q-mb-md" />
        <q-btn label="Cadastrar" color="primary" @click="cadastrarUsuario" />
      </q-card-section>
    </q-card>

    <q-separator spaced />

    <q-card>
      <q-card-section>
        <div class="text-h6">Usuários cadastrados</div>
      </q-card-section>
      <q-card-section>
        <q-table
          :rows="usuarios"
          :columns="columns"
          row-key="id"
          flat
          bordered
          dense
        >
          <template v-slot:body-cell-actions="props">
            <q-td align="center">
              <q-btn
                flat
                dense
                round
                icon="delete"
                color="negative"
                @click="excluirUsuario(props.row.id)"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import { api } from 'boot/axios';
import { useAuthStore } from 'src/stores/auth';
import type { QTableColumn } from 'quasar';

const nome = ref('');
const email = ref('');
const senha = ref('');
const usuarios = ref([]);
const auth = useAuthStore();


interface Usuario {
  id: number;
  nome: string;
  email: string;
}

const columns: QTableColumn<Usuario>[] = [
  { name: 'id', label: 'ID', field: 'id', align: 'center' },
  { name: 'nome', label: 'Nome', field: 'nome', align: 'center' },
  { name: 'email', label: 'Email', field: 'email', align: 'center' },
  { name: 'actions', label: 'Ações', field: () => '', align: 'center' }
];

async function carregarUsuarios() {
  try {
    const res = await api.get('/auth/usuarios', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    usuarios.value = res.data;
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Erro ao carregar usuários'
    });
  }
}

async function cadastrarUsuario() {
  if (!nome.value || !email.value || !senha.value) {
    Notify.create({
      type: 'warning',
      message: 'Preencha todos os campos'
    });
    return;
  }

  try {
    await api.post('/auth/signup', {
      nome: nome.value,
      email: email.value,
      password: senha.value
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    Notify.create({
      type: 'positive',
      message: 'Usuário cadastrado com sucesso'
    });

    nome.value = '';
    email.value = '';
    senha.value = '';
    await carregarUsuarios();
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
    const axiosError = err as { response?: { data?: { detail?: string } } };
    Notify.create({
      type: 'negative',
      message: axiosError.response?.data?.detail || 'Erro ao cadastrar'
    });
    } else {
      Notify.create({
        type: 'negative',
        message: 'Erro desconhecido ao cadastrar'
      });
    }
  }
}

async function excluirUsuario(id: number) {
  if (!confirm('Deseja realmente excluir este usuário?')) return;

  try {
    await api.delete(`/auth/usuarios/${id}`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    Notify.create({ type: 'positive', message: 'Usuário excluído' });
    await carregarUsuarios();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir usuário' });
  }
}

onMounted(carregarUsuarios);
</script>
