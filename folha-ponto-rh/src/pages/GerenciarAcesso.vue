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
        <q-select
          v-model="papel"
          :options="['funcionario', 'gestao']"
          label="Papel do usuário"
          filled
          dense
          class="q-mb-md"
        />
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
          row-key="email"
          flat
          bordered
          dense
        >
          <template v-slot:body-cell-status="props">
            <q-td align="center">
              <q-badge :color="props.row.locked ? 'negative' : 'positive'" align="middle">
                {{ props.row.locked ? 'Bloqueado' : 'Ativo' }}
              </q-badge>
            </q-td>
          </template>

          <template v-slot:body-cell-excluir="props">
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

          <template v-slot:body-cell-desbloquear="props">
            <q-td align="center">
              <q-btn
                v-if="props.row.locked"
                flat
                dense
                round
                icon="lock_open"
                color="warning"
                @click="desbloquearUsuario(props.row.id)"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-promover="props">
          <q-td align="center">
            <q-btn
              flat
              dense
              round
              color="primary"
              icon="swap_horiz"
              @click="alternarPapel(props.row)"
              :title="`Alterar papel: ${props.row.role === 'gestao' ? 'funcionario' : 'gestao'}`"
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
const papel = ref('funcionario');

interface Usuario {
  id: number;
  nome: string;
  email: string;
  locked: boolean;
  role: string;
}

const columns: QTableColumn<Usuario>[] = [
  { name: 'nome', label: 'Nome', field: 'nome', align: 'center' },
  { name: 'email', label: 'Email', field: 'email', align: 'center' },
  { name: 'role', label: 'Papel', field: 'role', align: 'center' },
  { name: 'status', label: 'Status', field: 'locked', align: 'center' },
  { name: 'excluir', label: 'Excluir', field: () => '', align: 'center' },
  { name: 'desbloquear', label: 'Desbloquear', field: () => '', align: 'center' }
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
      password: senha.value,
      role: papel.value
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
    let mensagem = 'Erro ao cadastrar';

    if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      mensagem = axiosErr.response?.data?.detail || mensagem;
    }

    Notify.create({ type: 'negative', message: mensagem });
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

async function desbloquearUsuario(id: number) {
  try {
    await api.post(`/auth/usuarios/${id}/desbloquear`, {}, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    Notify.create({ type: 'positive', message: 'Usuário desbloqueado com sucesso' });
    await carregarUsuarios();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao desbloquear usuário' });
  }
}


async function alternarPapel(usuario: Usuario) {
  const novoRole = usuario.role === 'gestao' ? 'funcionario' : 'gestao';

  try {
    const formData = new FormData();
    formData.append('role', novoRole);

    await api.patch(`/auth/usuarios/${usuario.id}/papel`, formData, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    Notify.create({ type: 'positive', message: 'Papel atualizado com sucesso' });
    await carregarUsuarios();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar papel do usuário' });
  }
}

onMounted(carregarUsuarios);
</script>
