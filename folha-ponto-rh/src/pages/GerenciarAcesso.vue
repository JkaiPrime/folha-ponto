<!-- File: src/pages/GerenciarAcesso.vue -->
<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Gerenciar usuários</div>

        <div class="row items-center q-gutter-sm">
          <q-input
            v-model="filtro"
            dense
            filled
            debounce="200"
            placeholder="Filtrar por nome, email, cargo, código..."
            clearable
            style="min-width: 280px"
          >
            <template #prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-btn
            color="primary"
            icon="person_add"
            label="Cadastrar usuário"
            @click="abrirDialogCadastro"
          />
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-pa-none">
        <div class="q-pa-sm" style="overflow-x:auto;">
          <q-table
            :rows="usuarios"
            :columns="columns"
            row-key="id"
            flat
            bordered
            dense
            wrap-cells
            :loading="loadingUsuarios || loadingJoin"
            :pagination="pagination"
            :rows-per-page-options="[0, 10, 20, 50]"
            :filter="filtro"
            :filter-method="tableFilter"
            table-style="min-width: 1100px"
            no-data-label="Nenhum usuário encontrado"
          >
            <template #loading>
              <q-inner-loading showing>
                <q-spinner size="32px" />
              </q-inner-loading>
            </template>

            <template #body-cell-role="props">
              <q-td align="center">
                <q-chip
                  square dense
                  :color="props.row.role === 'gestao' ? 'indigo-5' : (props.row.role === 'estagiario' ? 'orange-5' : 'primary')"
                  text-color="white"
                >
                  <q-icon
                    class="q-mr-xs"
                    :name="props.row.role === 'gestao' ? 'admin_panel_settings' : (props.row.role === 'estagiario' ? 'school' : 'person')"
                  />
                  {{ roleLabel(props.row.role) }}
                </q-chip>
              </q-td>
            </template>

            <template #body-cell-cargo="props">
              <q-td align="center">
                {{ props.row.cargo || 'Não definido' }}
              </q-td>
            </template>

            <template #body-cell-code="props">
              <q-td align="center">
                <q-badge v-if="props.row.code" outline color="primary">
                  {{ props.row.code }}
                </q-badge>
                <span v-else>—</span>
              </q-td>
            </template>

            <template #body-cell-status="props">
              <q-td align="center">
                <q-badge :color="props.row.locked ? 'negative' : 'positive'">
                  {{ props.row.locked ? 'Bloqueado' : 'Ativo' }}
                </q-badge>
              </q-td>
            </template>

            <template #body-cell-promover="props">
              <q-td align="center">
                <q-btn
                  v-if="props.row.role === 'funcionario'"
                  flat dense round color="primary" icon="arrow_upward"
                  @click="alternarPapel(props.row)"
                >
                  <q-tooltip>Promover a Gestão</q-tooltip>
                </q-btn>
                <q-btn
                  v-else-if="props.row.role === 'gestao'"
                  flat dense round color="grey" icon="arrow_downward"
                  @click="alternarPapel(props.row)"
                >
                  <q-tooltip>Rebaixar para Funcionário</q-tooltip>
                </q-btn>
                <q-btn
                  v-else
                  flat dense round color="orange" icon="work"
                  @click="alternarPapelCiclo(props.row)"
                >
                  <q-tooltip>Alternar papel (estagiário)</q-tooltip>
                </q-btn>
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
                <q-btn
                  v-if="props.row.locked"
                  flat dense round icon="lock_open" color="warning"
                  @click="desbloquearUsuario(props.row.id)"
                />
              </q-td>
            </template>
          </q-table>
        </div>
      </q-card-section>
    </q-card>

    <!-- DIALOG: Cadastro -->
    <q-dialog v-model="dlgCadastro" persistent>
      <q-card style="min-width: 560px; max-width: 90vw;">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Cadastrar novo usuário</div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-4">
              <q-input
                v-model="formCadastro.code"
                label="Código do colaborador"
                mask="######"
                fill-mask
                hint="6 dígitos"
                filled dense
              />
            </div>
            <div class="col-12 col-sm-8">
              <q-input v-model="formCadastro.nome" label="Nome" filled dense />
            </div>
            <div class="col-12">
              <q-input v-model="formCadastro.email" type="email" label="Email" filled dense />
            </div>
            <div class="col-12 col-sm-6">
              <q-input
                v-model="formCadastro.senha"
                :type="showPwdCadastro ? 'text' : 'password'"
                label="Senha"
                filled dense
              >
                <template #append>
                  <q-icon
                    :name="showPwdCadastro ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPwdCadastro = !showPwdCadastro"
                  />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-sm-6">
              <q-input
                v-model="formCadastro.confirmarSenha"
                :type="showPwdCadastro ? 'text' : 'password'"
                label="Confirmar senha"
                filled dense
              />
            </div>
            <div class="col-12 col-sm-6">
              <q-select
                v-model="formCadastro.role"
                :options="roles"
                label="Papel"
                filled dense
                emit-value
                map-options
              />
            </div>
            <div class="col-12 col-sm-6">
              <q-input v-model="formCadastro.cargo" label="Cargo (opcional)" filled dense />
            </div>
          </div>

          <q-banner v-if="erroCadastro" class="bg-red-2 text-red-10">
            {{ erroCadastro }}
          </q-banner>
        </q-card-section>

        <q-card-actions align="between">
          <q-btn flat label="Fechar" v-close-popup />
          <q-space />
          <q-btn
            label="Cadastrar"
            color="primary"
            :loading="loadingCadastro"
            @click="cadastrarUsuario"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG: Gerenciar Acesso -->
    <q-dialog v-model="dlgGerenciar" persistent>
      <q-card style="min-width: 640px; max-width: 92vw;">
        <q-card-section class="row items-center justify-between">
          <div class="column">
            <div class="text-h6">Gerenciar acesso</div>
            <div class="text-caption text-grey-7">
              Edite dados do usuário e o vínculo de colaborador (código/cargo).
            </div>
          </div>
          <q-badge :color="editLocked ? 'negative' : 'positive'" outline>
            {{ editLocked ? 'Bloqueado' : 'Ativo' }}
          </q-badge>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md">
          <div class="row q-col-gutter-sm">
            <div class="col-12 col-md-6">
              <q-input v-model="editNome" label="Nome" filled dense />
            </div>
            <div class="col-12 col-md-6">
              <q-input v-model="editEmail" label="Email" type="email" filled dense />
            </div>
            <div class="col-12 col-md-6">
              <q-select v-model="editRole" :options="roles" label="Papel" filled dense emit-value map-options />
            </div>
          </div>

          <q-separator spaced />

          <div class="row items-center justify-between">
            <div class="text-subtitle2">Dados do colaborador</div>
            <q-spinner v-if="loadingColab" size="20px" />
          </div>

          <div class="row q-col-gutter-sm">
            <div class="col-12 col-sm-4">
              <q-input
                v-model="editCode"
                label="Código (6 dígitos)"
                mask="######"
                fill-mask
                inputmode="numeric"
                hint="Vínculo colaborador"
                filled dense
              />
            </div>
            <div class="col-12 col-sm-8">
              <q-input v-model="editCargo" label="Cargo" filled dense />
            </div>
          </div>

          <q-banner
            v-if="!loadingColab && !editColabId"
            class="bg-orange-2 text-orange-10 q-mt-sm"
          >
            Nenhum colaborador vinculado. Informe <b>código/cargo</b> e eu criarei o vínculo ao salvar.
          </q-banner>

          <q-separator spaced />

          <div class="row q-col-gutter-sm items-end">
            <div class="col">
              <q-input
                v-model="novaSenha"
                :type="showPwd ? 'text' : 'password'"
                label="Definir senha temporária"
                filled dense
              >
                <template #append>
                  <q-icon
                    :name="showPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPwd = !showPwd"
                  />
                </template>
              </q-input>
            </div>
            <div class="col-auto">
              <q-btn
                color="primary"
                label="Definir"
                :disable="!novaSenha"
                :loading="loadingDialog"
                @click="definirSenhaTemporaria"
              />
            </div>
          </div>

          <q-banner v-if="editLocked" class="bg-orange-2 text-orange-10 q-mt-sm">
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
import { isAxiosError, type AxiosError } from 'axios'

type Role = 'funcionario' | 'gestao' | 'estagiario'

interface Usuario {
  id: number
  nome: string
  email: string
  locked: boolean
  role: Role
  cargo?: string | null
  code?: string | null
}

interface ColabByUser {
  id: number
  user_id: number
  code: string | null
  cargo: string | null
  nome: string
  email: string | null
  role: Role | null
}

/* ===== estado ===== */
const filtro = ref('')
const loadingUsuarios = ref(false)
const loadingJoin = ref(false)
const usuarios = ref<Usuario[]>([])

const pagination = ref({ page: 1, rowsPerPage: 0, sortBy: 'nome', descending: false })

const roles = [
  { label: 'Funcionário', value: 'funcionario' as Role },
  { label: 'Gestão', value: 'gestao' as Role },
  { label: 'Estagiário', value: 'estagiario' as Role }
]

const columns: QTableColumn<Usuario>[] = [
  { name: 'nome', label: 'Nome', field: 'nome', align: 'left', sortable: true },
  { name: 'email', label: 'Email', field: 'email', align: 'left', sortable: true },
  { name: 'role', label: 'Papel', field: 'role', align: 'center', sortable: true },
  { name: 'cargo', label: 'Cargo', field: 'cargo', align: 'center', sortable: true },
  { name: 'code', label: 'Código', field: 'code', align: 'center', sortable: true },
  { name: 'status', label: 'Status', field: 'locked', align: 'center', sortable: true },
  { name: 'promover', label: 'Alterar Papel', field: () => '', align: 'center' },
  { name: 'gerenciar', label: 'Gerenciar', field: () => '', align: 'center' },
  { name: 'excluir', label: 'Excluir', field: () => '', align: 'center' },
  { name: 'desbloquear', label: 'Desbloquear', field: () => '', align: 'center' }
]

function roleLabel (r: Role) {
  return r === 'gestao' ? 'Gestão' : (r === 'estagiario' ? 'Estagiário' : 'Funcionário')
}

function tableFilter(
  rows: readonly Usuario[],
  terms: string,
  cols: readonly QTableColumn<Usuario>[],
  getCellValue: (col: QTableColumn<Usuario>, row: Usuario) => unknown
): readonly Usuario[] {
  const t = (terms ?? '').toString().trim().toLowerCase()
  if (!t) return rows
  const toText = (v: unknown): string => {
    if (v == null) return ''
    const tp = typeof v
    // eslint-disable-next-line @typescript-eslint/no-base-to-string
    if (tp === 'string' || tp === 'number' || tp === 'boolean') return String(v)
    return ''
  }
  const matches = (row: Usuario) => {
    const colText = cols.map(c => toText(getCellValue(c, row)).toLowerCase()).join(' ')
    const roleTxt = roleLabel(row.role).toLowerCase()
    return colText.includes(t) || roleTxt.includes(t)
  }
  return rows.filter(matches) as readonly Usuario[]
}

/* ===== carregamento + hidratação ===== */
async function carregarUsuarios () {
  loadingUsuarios.value = true
  try {
    const res = await api.get<Usuario[]>('/auth/usuarios', { withCredentials: true })
    usuarios.value = res.data
    await hidratarComColaborador()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar usuários' })
  } finally {
    loadingUsuarios.value = false
  }
}

async function hidratarComColaborador () {
  const pendentes = usuarios.value.filter(u => u.code == null || u.cargo == null)
  if (pendentes.length === 0) return
  loadingJoin.value = true
  try {
    const updates = await Promise.allSettled(
      pendentes.map(async (u) => {
        const { data } = await api.get<ColabByUser>(`/colaboradores/by-user/${u.id}`, { withCredentials: true })
        return { id: u.id, code: data.code, cargo: data.cargo }
      })
    )
    const map = new Map<number, { code: string | null; cargo: string | null }>()
    for (const r of updates) {
      if (r.status === 'fulfilled') map.set(r.value.id, { code: r.value.code, cargo: r.value.cargo })
    }
    usuarios.value = usuarios.value.map(u => map.has(u.id) ? { ...u, ...map.get(u.id)! } : u)
  } finally {
    loadingJoin.value = false
  }
}

/* ===== ações tabela ===== */
async function excluirUsuario (id: number) {
  if (!confirm('Deseja realmente excluir este usuário?')) return
  try {
    await api.delete(`/auth/usuarios/${id}`, { withCredentials: true })
    Notify.create({ type: 'positive', message: 'Usuário excluído' })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir usuário' })
  }
}

async function desbloquearUsuario (id: number) {
  try {
    await api.post(`/auth/usuarios/${id}/desbloquear`, undefined, { withCredentials: true })
    Notify.create({ type: 'positive', message: 'Usuário desbloqueado' })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao desbloquear usuário' })
  }
}

async function alternarPapel (usuario: Usuario) {
  const novoRole: Role = usuario.role === 'gestao' ? 'funcionario' : 'gestao'
  try {
    const fd = new FormData()
    fd.append('role', novoRole)
    await api.patch(`/auth/usuarios/${usuario.id}/papel`, fd, { withCredentials: true })
    Notify.create({ type: 'positive', message: 'Papel atualizado' })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar papel' })
  }
}

async function alternarPapelCiclo (usuario: Usuario) {
  const ordem = ['estagiario', 'funcionario', 'gestao'] as const
  const idx = ordem.indexOf(usuario.role as typeof ordem[number])
  const nextIndex = (idx + 1) % ordem.length
  const proximo: Role = ordem[nextIndex] as Role
  try {
    const fd = new FormData()
    fd.append('role', proximo)
    await api.patch(`/auth/usuarios/${usuario.id}/papel`, fd, { withCredentials: true })
    Notify.create({ type: 'positive', message: `Papel alterado para ${proximo}` })
    await carregarUsuarios()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar papel' })
  }
}

/* ===== cadastro ===== */
const dlgCadastro = ref(false)
const loadingCadastro = ref(false)
const showPwdCadastro = ref(false)
const erroCadastro = ref<string | null>(null)

const formCadastro = ref<{ code: string; nome: string; email: string; senha: string; confirmarSenha: string; role: Role; cargo: string; }>({
  code: '', nome: '', email: '', senha: '', confirmarSenha: '', role: 'funcionario', cargo: ''
})

function abrirDialogCadastro () {
  erroCadastro.value = null
  formCadastro.value = { code: '', nome: '', email: '', senha: '', confirmarSenha: '', role: 'funcionario', cargo: '' }
  dlgCadastro.value = true
}

async function cadastrarUsuario () {
  erroCadastro.value = null
  if (!formCadastro.value.nome || !formCadastro.value.email || !formCadastro.value.senha) {
    erroCadastro.value = 'Preencha nome, email e senha.'; return
  }
  if (formCadastro.value.senha !== formCadastro.value.confirmarSenha) {
    erroCadastro.value = 'As senhas não conferem.'; return
  }
  if (formCadastro.value.code && formCadastro.value.code.length !== 6) {
    erroCadastro.value = 'Código do colaborador deve ter 6 dígitos.'; return
  }

  loadingCadastro.value = true
  try {
    await api.post('/auth/signup', {
      nome: formCadastro.value.nome,
      email: formCadastro.value.email,
      password: formCadastro.value.senha,
      role: formCadastro.value.role
    }, { withCredentials: true })

    if (formCadastro.value.code || formCadastro.value.cargo) {
      try {
        await api.post('/colaboradores', {
          code: formCadastro.value.code || undefined,
          nome: formCadastro.value.nome,
          email_usuario: formCadastro.value.email,
          cargo: formCadastro.value.cargo || undefined
        }, { withCredentials: true })
      } catch {
        Notify.create({ type: 'warning', message: 'Usuário criado. Falha ao criar colaborador (code/cargo).' })
      }
    }

    Notify.create({ type: 'positive', message: 'Usuário cadastrado com sucesso' })
    dlgCadastro.value = false
    await carregarUsuarios()
  } catch (err: unknown) {
    const error = err as AxiosError<{ detail?: string }>
    let mensagem = error.response?.data?.detail || 'Erro ao cadastrar usuário'
    if (error.response?.status === 401) mensagem = 'Não autorizado.'
    if (error.response?.status === 403) mensagem = 'Permissão negada.'
    if (error.response?.status === 422) mensagem = 'Dados inválidos.'
    erroCadastro.value = mensagem
  } finally {
    loadingCadastro.value = false
  }
}

/* ===== gerenciar ===== */
const dlgGerenciar = ref(false)
const editUser = ref<Usuario | null>(null)
const editNome = ref('')
const editEmail = ref('')
const editRole = ref<Role>('funcionario')
const editLocked = ref(false)

const editColabId = ref<number | null>(null)
const editCode = ref('')
const editCargo = ref('')
const loadingColab = ref(false)

const showPwd = ref(false)
const novaSenha = ref('')
const loadingDialog = ref(false)

async function fetchColaboradorByUser (userId: number) {
  loadingColab.value = true
  editColabId.value = null
  try {
    const { data } = await api.get<ColabByUser>(`/colaboradores/by-user/${userId}`, { withCredentials: true })
    editColabId.value = data.id
    editCode.value = data.code || ''
    editCargo.value = data.cargo || ''
  } catch (err: unknown) {
    if (isAxiosError(err) && err.response?.status !== 404) {
      Notify.create({ type: 'warning', message: 'Falha ao carregar colaborador' })
    }
    editColabId.value = null
  } finally {
    loadingColab.value = false
  }
}

function abrirGerenciar (u: Usuario) {
  editUser.value = { ...u }
  editNome.value = u.nome
  editEmail.value = u.email
  editRole.value = u.role
  editLocked.value = u.locked
  editCode.value = u.code || ''
  editCargo.value = u.cargo || ''
  novaSenha.value = ''
  dlgGerenciar.value = true
  void fetchColaboradorByUser(u.id)
}

async function salvarEdicoes () {
  if (!editUser.value) return
  if (editCode.value && editCode.value.length !== 6) {
    Notify.create({ type: 'warning', message: 'Código do colaborador deve ter 6 dígitos.' })
    return
  }

  loadingDialog.value = true
  try {
    // 1) Atualiza nome/email do usuário
    await api.patch(`/auth/usuarios/${editUser.value.id}`, {
      nome: editNome.value,
      email: editEmail.value
    }, { withCredentials: true })

    // 2) Papel (se mudou)
    if (editRole.value !== editUser.value.role) {
      const fd = new FormData()
      fd.append('role', editRole.value)
      await api.patch(`/auth/usuarios/${editUser.value.id}/papel`, fd, { withCredentials: true })
    }

    // 3) Vínculo Colaborador: envia só os campos do vínculo, com trim
    const payload = {
      code: editCode.value ? editCode.value.trim() : null,
      cargo: editCargo.value ? editCargo.value.trim() : null
    }
    const resp = await api.patch(`/colaboradores/by-user/${editUser.value.id}`, payload, { withCredentials: true })
    console.debug('[GERENCIAR] PATCH /colaboradores/by-user resp:', resp.data)

    // 4) Atualiza a linha local imediatamente (tipado, com guarda)
    const currIdx = usuarios.value.findIndex(u => u.id === editUser.value!.id)
    if (currIdx !== -1) {
      const curr = usuarios.value[currIdx]
      if (curr) {
        const updated: Usuario = {
          id: curr.id,
          nome: curr.nome,
          email: curr.email,
          locked: curr.locked,
          role: curr.role,
          code: payload.code,
          cargo: payload.cargo
        }
        usuarios.value.splice(currIdx, 1, updated)
      }
    }

    Notify.create({ type: 'positive', message: 'Alterações salvas' })
    dlgGerenciar.value = false

    // 5) Recarrega + rehidrata (garante refletir também se /auth/usuarios não retornar cargo/code)
    await carregarUsuarios()
    await hidratarComColaborador()
  } catch (e) {
    const emsg = isAxiosError(e) ? (e.response?.data?.detail || e.message) : 'Erro ao salvar alterações'
    console.error('[GERENCIAR] Falha PATCH by-user:', emsg)
    Notify.create({ type: 'negative', message: 'Erro ao salvar alterações' })
  } finally {
    loadingDialog.value = false
  }
}

async function definirSenhaTemporaria () {
  if (!editUser.value || !novaSenha.value) return
  loadingDialog.value = true
  try {
    await api.post(`/auth/usuarios/${editUser.value.id}/password-temporaria`, {
      nova_senha: novaSenha.value
    }, { withCredentials: true })
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

<style scoped>
::v-deep(.q-table thead tr th) {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--q-table-bg, #fff);
}
::v-deep(.q-table tbody tr:nth-child(even)) {
  background: rgba(0,0,0,0.02);
}
::v-deep(.q-table tbody tr:hover) {
  background: rgba(25,118,210,0.08);
}
</style>
