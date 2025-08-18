<template>
  <q-page class="q-pa-md">
    <!-- CADASTRO -->
    <q-card class="q-pa-md q-mx-auto" style="max-width: 600px;">
      <q-card-section>
        <div class="text-h6">Cadastrar novo usuário</div>
      </q-card-section>
      <q-card-section>
        <q-input v-model="nome" label="Nome" filled dense class="q-mb-sm" />
        <q-input v-model="email" label="Email" type="email" filled dense class="q-mb-sm" />
        <q-input filled dense v-model="senha" :type="isPwd ? 'password' : 'text'" label="Senha" class="q-mb-md">
          <template #append>
            <q-icon :name="isPwd ? 'visibility_off' : 'visibility'" class="cursor-pointer" @click="isPwd = !isPwd" />
          </template>
        </q-input>
        <q-select v-model="papel" :options="roles" label="Papel do usuário" filled dense class="q-mb-md" />
        <q-btn label="Cadastrar" color="primary" @click="cadastrarUsuario" />
      </q-card-section>
    </q-card>

    <q-separator spaced />

    <!-- LISTA -->
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
          <template #body-cell-role="props">
            <q-td align="center">
              <q-icon :name="props.row.role === 'gestao' ? 'admin_panel_settings' : 'person'"
                      :color="props.row.role === 'gestao' ? 'indigo' : 'primary'">
                <q-tooltip>{{ props.row.role === 'gestao' ? 'Gestão' : 'Funcionário' }}</q-tooltip>
              </q-icon>
            </q-td>
          </template>

          <template #body-cell-promover="props">
            <q-td align="center">
              <q-btn
                flat dense round color="primary" icon="arrow_upward"
                v-if="props.row.role === 'funcionario'"
                @click="alternarPapel(props.row)"
              >
                <q-tooltip>Promover a Gestão</q-tooltip>
              </q-btn>
              <q-btn
                flat dense round color="grey" icon="arrow_downward"
                v-else
                @click="alternarPapel(props.row)"
              >
                <q-tooltip>Rebaixar para Funcionário</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template #body-cell-status="props">
            <q-td align="center">
              <q-badge :color="props.row.locked ? 'negative' : 'positive'">
                {{ props.row.locked ? 'Bloqueado' : 'Ativo' }}
              </q-badge>
            </q-td>
          </template>

          <template #body-cell-gerenciar="props">
            <q-td align="center">
              <q-btn flat dense round icon="settings" color="primary" @click="abrirGerenciar(props.row)">
                <q-tooltip>Gerenciar acesso</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template #body-cell-excluir="props">
            <q-td align="center">
              <q-btn flat dense round icon="delete" color="negative" @click="excluirUsuario(props.row.id)" />
            </q-td>
          </template>

          <template #body-cell-desbloquear="props">
            <q-td align="center">
              <q-btn v-if="props.row.locked" flat dense round icon="lock_open" color="warning"
                     @click="desbloquearUsuario(props.row.id)" />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- DIALOG: Gerenciar Acesso -->
    <q-dialog v-model="dlgGerenciar" persistent>
      <q-card style="min-width: 560px; max-width: 90vw;">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Gerenciar acesso</div>
          <q-badge :color="editLocked ? 'negative' : 'positive'" outline>
            {{ editLocked ? 'Bloqueado' : 'Ativo' }}
          </q-badge>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md">
          <q-input v-model="editNome" label="Nome" filled dense />
          <q-input v-model="editEmail" label="Email" type="email" filled dense />
          <q-select v-model="editRole" :options="roles" label="Papel" filled dense />

          <div class="row q-col-gutter-sm items-end">
            <div class="col">
              <q-input v-model="novaSenha" :type="showPwd ? 'text' : 'password'"
                       label="Definir senha temporária" filled dense>
                <template #append>
                  <q-icon :name="showPwd ? 'visibility_off' : 'visibility'"
                          class="cursor-pointer" @click="showPwd = !showPwd" />
                </template>
              </q-input>
            </div>
            <div class="col-auto">
              <q-btn color="primary" label="Definir" :disable="!novaSenha" :loading="loadingDialog"
                     @click="definirSenhaTemporaria" />
            </div>
          </div>

          <!--<div class="row q-col-gutter-sm items-end">
            <div class="col">
              <q-input v-model="resetLink" label="Link de redefinição (gerado)" filled dense readonly />
            </div>
            <div class="col-auto">
              <q-btn flat icon="content_copy" color="primary" :disable="!resetLink" @click="copiarResetLink" />
            </div>
            <div class="col-auto">
              <q-btn color="secondary" label="Gerar link" :loading="loadingDialog" @click="gerarResetLink" />
            </div>
          </div>
          -->
          <q-banner v-if="editLocked" class="bg-orange-2 text-orange-10">
            Usuário está bloqueado. Use o botão <b>Desbloquear</b> na tabela para liberar o acesso.
          </q-banner>
        </q-card-section>

        <q-card-actions align="between">
          <q-btn flat label="Fechar" v-close-popup />
          <q-space />
          <q-btn label="Salvar alterações" color="primary" :loading="loadingDialog" @click="salvarEdicoes" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Notify } from 'quasar'
import { api } from 'boot/axios'
import type { QTableColumn } from 'quasar'
import type { AxiosError } from 'axios'

const roles = ['funcionario', 'gestao'] as const

const isPwd = ref(true)
const showPwd = ref(false)

const nome = ref('')
const email = ref('')
const senha = ref('')
const papel = ref<typeof roles[number]>('funcionario')

interface Usuario {
  id: number
  nome: string
  email: string
  locked: boolean
  role: 'funcionario' | 'gestao'
}
const usuarios = ref<Usuario[]>([])

const columns: QTableColumn<Usuario>[] = [
  { name: 'nome',        label: 'Nome',           field: 'nome',   align: 'center' },
  { name: 'email',       label: 'Email',          field: 'email',  align: 'center' },
  { name: 'role',        label: 'Papel',          field: 'role',   align: 'center' },
  { name: 'promover',    label: 'Alterar Papel',  field: () => '', align: 'center' },
  { name: 'status',      label: 'Status',         field: 'locked', align: 'center' },
  { name: 'gerenciar',   label: 'Gerenciar',      field: () => '', align: 'center' }, // ⚙️
  { name: 'excluir',     label: 'Excluir',        field: () => '', align: 'center' },
  { name: 'desbloquear', label: 'Desbloquear',    field: () => '', align: 'center' }
]

async function carregarUsuarios () {
  try {
    const res = await api.get<Usuario[]>('/auth/usuarios')
    usuarios.value = res.data
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar usuários' })
  }
}

async function cadastrarUsuario () {
  if (!nome.value || !email.value || !senha.value) {
    Notify.create({ type: 'warning', message: 'Preencha todos os campos' })
    return
  }
  try {
    await api.post('/auth/signup', {
      nome: nome.value, email: email.value, password: senha.value, role: papel.value
    }, { withCredentials: true })
    Notify.create({ type: 'positive', message: 'Usuário cadastrado com sucesso' })
    nome.value = ''; email.value = ''; senha.value = ''; papel.value = 'funcionario'
    await carregarUsuarios()
  } catch (err: unknown) {
    const error = err as AxiosError<{ detail?: string }>
    let mensagem = error.response?.data?.detail || 'Erro ao cadastrar usuário'
    if (error.response?.status === 401) mensagem = 'Não autorizado.'
    if (error.response?.status === 403) mensagem = 'Permissão negada.'
    if (error.response?.status === 422) mensagem = 'Dados inválidos.'
    Notify.create({ type: 'negative', message: mensagem })
  }
}

async function excluirUsuario (id: number) {
  if (!confirm('Deseja realmente excluir este usuário?')) return
  try {
    await api.delete(`/auth/usuarios/${id}`)
    Notify.create({ type: 'positive', message: 'Usuário excluído' })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir usuário' })
  }
}

async function desbloquearUsuario (id: number) {
  try {
    await api.post(`/auth/usuarios/${id}/desbloquear`)
    Notify.create({ type: 'positive', message: 'Usuário desbloqueado' })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao desbloquear usuário' })
  }
}

async function alternarPapel (usuario: Usuario) {
  const novoRole = usuario.role === 'gestao' ? 'funcionario' : 'gestao'
  try {
    const fd = new FormData()
    fd.append('role', novoRole)
    await api.patch(`/auth/usuarios/${usuario.id}/papel`, fd)
    Notify.create({ type: 'positive', message: 'Papel atualizado' })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar papel' })
  }
}

/** ============ Dialog de Gerenciamento ============ */
const dlgGerenciar = ref(false)
const editUser = ref<Usuario | null>(null)
const editNome = ref('')
const editEmail = ref('')
const editRole = ref<Usuario['role']>('funcionario')
const editLocked = ref(false)

const novaSenha = ref('')
const resetLink = ref<string | null>(null)
const loadingDialog = ref(false)

function abrirGerenciar (u: Usuario) {
  editUser.value = { ...u }
  editNome.value = u.nome
  editEmail.value = u.email
  editRole.value = u.role
  editLocked.value = u.locked
  novaSenha.value = ''
  resetLink.value = null
  dlgGerenciar.value = true
}

async function salvarEdicoes () {
  if (!editUser.value) return
  loadingDialog.value = true
  try {
    // 1) Atualiza nome/email
    await api.patch(`/auth/usuarios/${editUser.value.id}`, {
      nome: editNome.value,
      email: editEmail.value
    })
    // 2) Se mudou o papel, usa o endpoint existente
    if (editRole.value !== editUser.value.role) {
      const fd = new FormData()
      fd.append('role', editRole.value)
      await api.patch(`/auth/usuarios/${editUser.value.id}/papel`, fd)
    }
    Notify.create({ type: 'positive', message: 'Alterações salvas' })
    dlgGerenciar.value = false
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao salvar alterações' })
  } finally {
    loadingDialog.value = false
  }
}

/*async function gerarResetLink () {
  if (!editUser.value) return
  loadingDialog.value = true
  try {
    const res = await api.post<{ reset_url: string }>(`/auth/usuarios/${editUser.value.id}/reset-link`)
    resetLink.value = res.data.reset_url
    Notify.create({ type: 'positive', message: 'Link gerado' })
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao gerar link' })
  } finally {
    loadingDialog.value = false
  }
}

async function copiarResetLink () {
  if (!resetLink.value) return
  try {
    await copyToClipboard(resetLink.value)
    Notify.create({ type: 'positive', message: 'Link copiado' })
  } catch {
    Notify.create({ type: 'warning', message: 'Não foi possível copiar' })
  }
}
  */

async function definirSenhaTemporaria () {
  if (!editUser.value || !novaSenha.value) return
  loadingDialog.value = true
  try {
    await api.post(`/auth/usuarios/${editUser.value.id}/password-temporaria`, {
      nova_senha: novaSenha.value
    })
    Notify.create({ type: 'positive', message: 'Senha temporária definida' })
    novaSenha.value = ''
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao definir senha' })
  } finally {
    loadingDialog.value = false
  }
}

onMounted(carregarUsuarios)
</script>
