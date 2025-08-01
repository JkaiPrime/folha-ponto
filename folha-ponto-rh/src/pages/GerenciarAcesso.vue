<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 600px;">
      <q-card-section>
        <div class="text-h6">Cadastrar novo usuário</div>
      </q-card-section>
      <q-card-section>
        <q-input v-model="nome" label="Nome" filled dense class="q-mb-sm" />
        <q-input v-model="email" label="Email" type="email" filled dense class="q-mb-sm" />
        <q-input
          filled
          dense
          v-model="senha"
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
          <template v-slot:body-cell-role="props">
            <q-td align="center">
              <q-icon
                :name="props.row.role === 'gestao' ? 'admin_panel_settings' : 'person'"
                :color="props.row.role === 'gestao' ? 'indigo' : 'primary'"
              >
                <q-tooltip>
                  {{ props.row.role === 'gestao' ? 'Gestão' : 'Funcionário' }}
                </q-tooltip>
              </q-icon>
            </q-td>
          </template>

          <template v-slot:body-cell-promover="props">
            <q-td align="center">
              <q-btn
                flat
                dense
                round
                color="primary"
                icon="arrow_upward"
                v-if="props.row.role === 'funcionario'"
                @click="alternarPapel(props.row)"
              >
                <q-tooltip>Promover a Gestão</q-tooltip>
              </q-btn>
              <q-btn
                flat
                dense
                round
                color="grey"
                icon="arrow_downward"
                v-else
                @click="alternarPapel(props.row)"
              >
                <q-tooltip>Rebaixar para Funcionário</q-tooltip>
              </q-btn>
            </q-td>
          </template>

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
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import { api } from 'boot/axios';
import type { QTableColumn } from 'quasar';
import type { AxiosError } from 'axios';


const isPwd = ref(true)
const nome = ref('');
const email = ref('');
const senha = ref('');
const usuarios = ref([]);

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
  { name: 'promover', label: 'Alterar Papel', field: () => '', align: 'center' },
  { name: 'status', label: 'Status', field: 'locked', align: 'center' },
  { name: 'excluir', label: 'Excluir', field: () => '', align: 'center' },
  { name: 'desbloquear', label: 'Desbloquear', field: () => '', align: 'center' }
];

async function carregarUsuarios() {
  try {
    const res = await api.get('/auth/usuarios');
    usuarios.value = res.data;
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar usuários' });
  }
}

async function cadastrarUsuario() {
  if (!nome.value || !email.value || !senha.value) {
    Notify.create({ type: 'warning', message: 'Preencha todos os campos' });
    return;
  }

  console.log('[DEBUG] Tentando cadastrar usuário...', {
    nome: nome.value,
    email: email.value,
    role: papel.value
  });

  try {
    const res = await api.post(
      '/auth/signup',
      {
        nome: nome.value,
        email: email.value,
        password: senha.value,
        role: papel.value
      },
      {
        withCredentials: true // ✅ garante envio do cookie JWT
      }
    );

    console.log('[DEBUG] Resposta do cadastro:', res.data);

    Notify.create({ type: 'positive', message: 'Usuário cadastrado com sucesso' });

    nome.value = '';
    email.value = '';
    senha.value = '';
    papel.value = 'funcionario';
    await carregarUsuarios();
  } catch (err: unknown) {
    const error = err as AxiosError<{ detail?: string }>;
    console.log('[DEBUG] Erro ao cadastrar usuário:', err);

    let mensagem = 'Erro ao cadastrar usuário';
    if (error.response) {
      console.log('[DEBUG] Status da resposta:', error.response.status);
      console.log('[DEBUG] Detalhes:', error.response.data);

      mensagem = error.response.data?.detail || mensagem;

      if (error.response.status === 401) {
        mensagem = 'Não autorizado. Verifique se está logado como gestor.';
      } else if (error.response.status === 403) {
        mensagem = 'Permissão negada para cadastrar usuários.';
      } else if (error.response.status === 422) {
        mensagem = 'Dados inválidos enviados. Verifique os campos.';
      }
    }

    Notify.create({ type: 'negative', message: mensagem });
  }
}


async function excluirUsuario(id: number) {
  if (!confirm('Deseja realmente excluir este usuário?')) return;

  try {
    await api.delete(`/auth/usuarios/${id}`);
    Notify.create({ type: 'positive', message: 'Usuário excluído' });
    await carregarUsuarios();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir usuário' });
  }
}

async function desbloquearUsuario(id: number) {
  try {
    await api.post(`/auth/usuarios/${id}/desbloquear`);
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

    await api.patch(`/auth/usuarios/${usuario.id}/papel`, formData);

    Notify.create({ type: 'positive', message: 'Papel atualizado com sucesso' });
    await carregarUsuarios();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar papel do usuário' });
  }
}

onMounted(carregarUsuarios);
</script>
