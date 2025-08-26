<template>
  <q-page class="q-pa-md">
    <q-card>
      <!-- Header -->
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Editar pontos por colaborador</div>

        <div v-if="registros.length" class="row items-center q-gutter-sm">
          <q-chip outline color="primary" text-color="primary" icon="query_builder">
            Registros: <strong class="q-ml-xs">{{ registros.length }}</strong>
          </q-chip>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Filtros (mesmo layout do visualizar) -->
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-select
              v-model="colaboradorSelecionado"
              :options="colaboradores"
              option-value="id"
              option-label="nome"
              emit-value
              map-options
              label="Selecionar colaborador"
              filled
              dense
              :loading="loadingColaboradores"
              clearable
            />
          </div>

          <div class="col-12 col-sm-6">
            <q-input
              v-model="mesSelecionado"
              label="Selecionar mês"
              filled
              dense
              mask="####-##"
              placeholder="YYYY-MM"
            >
              <template #append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy transition-show="scale" transition-hide="scale">
                    <q-date
                      v-model="mesSelecionado"
                      mask="YYYY-MM"
                      minimal
                      default-view="Months"
                      emit-immediately
                    />
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </div>
        </div>
      </q-card-section>

      <q-separator v-if="registros.length" />

      <!-- Tabela -->
      <q-card-section>
        <q-table
          :rows="registros"
          :columns="columns"
          row-key="rowKey"
          dense
          flat
          bordered
          :loading="loadingPontos"
          v-model:pagination="pagination"
          :rows-per-page-options="[10, 20, 50, 0]"
        >
          <template #loading>
            <q-inner-loading showing>
              <q-spinner-dots size="32px" />
            </q-inner-loading>
          </template>

          <!-- Colunas formatadas como no 'visualizar' -->
          <template #body-cell-data="p">
            <q-td :props="p" class="text-center">{{ p.row._data_fmt }}</q-td>
          </template>
          <template #body-cell-dia="p">
            <q-td :props="p" class="text-center">{{ p.row._dia_fmt }}</q-td>
          </template>

          <!-- Campos editáveis (respeitando linha de justificativa sem id) -->
          <template #body-cell-entrada="p">
            <q-td :props="p">
              <template v-if="p.row.id">
                <q-input
                  v-model="p.row.entrada"
                  type="datetime-local"
                  dense
                  outlined
                />
              </template>
              <template v-else>
                <div class="text-italic text-primary">
                  Justificativa: {{ p.row.justificativa || 'Sem motivo informado' }}
                </div>
              </template>
            </q-td>
          </template>

          <template #body-cell-saida_almoco="p">
            <q-td :props="p">
              <template v-if="p.row.id">
                <q-input v-model="p.row.saida_almoco" type="datetime-local" dense outlined />
              </template>
              <template v-else>
                <div class="text-grey-6">—</div>
              </template>
            </q-td>
          </template>

          <template #body-cell-volta_almoco="p">
            <q-td :props="p">
              <template v-if="p.row.id">
                <q-input v-model="p.row.volta_almoco" type="datetime-local" dense outlined />
              </template>
              <template v-else>
                <div class="text-grey-6">—</div>
              </template>
            </q-td>
          </template>

          <template #body-cell-saida="p">
            <q-td :props="p">
              <template v-if="p.row.id">
                <q-input v-model="p.row.saida" type="datetime-local" dense outlined />
              </template>
              <template v-else>
                <div class="text-grey-6">—</div>
              </template>
            </q-td>
          </template>

          <template #body-cell-actions="p">
            <q-td :props="p" align="center">
              <q-btn
                label="Salvar"
                color="positive"
                size="sm"
                :disable="!p.row.id"
                :loading="savingId === p.row.id"
                @click="salvarAlteracao(p.row)"
                icon="save"
              />
            </q-td>
          </template>

          <template #bottom>
            <div class="full-width row justify-end q-pa-sm">
              <q-chip v-if="registros.length" color="grey-3" text-color="dark">
                Registros: {{ registros.length }}
              </q-chip>
            </div>
          </template>
        </q-table>

        <div v-if="!loadingPontos && registros.length === 0" class="q-mt-lg">
          <q-banner class="bg-grey-2 text-grey-9">
            <template #avatar>
              <q-icon name="info" />
            </template>
            Nenhum registro encontrado. Selecione um colaborador e um mês.
          </q-banner>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Notify } from 'quasar'
import { api } from 'boot/axios'
import type { QTableColumn } from 'quasar'

/* ========================= Tipagens ========================= */
type IsoStr = string | null | undefined

interface RegistroApi {
  id: number | null
  data?: IsoStr            // YYYY-MM-DD (date-only) ou ISO
  entrada?: IsoStr
  saida_almoco?: IsoStr
  volta_almoco?: IsoStr
  saida?: IsoStr
  justificativa?: string | null
}

interface RegistroFront extends RegistroApi {
  rowKey: string           // chave estável para q-table
  _data_fmt: string        // dd/MM/yyyy
  _dia_fmt: string         // QUI., SEX., ...
}

interface Colaborador {
  id: number
  nome: string
}
interface ColaboradorApi {
  id?: number | string
  code?: number | string
  nome?: string
}

/* ========================= State ========================= */
const colaboradores = ref<Colaborador[]>([])
const colaboradorSelecionado = ref<number | null>(null)
const mesSelecionado = ref<string | null>(null)
const registros = ref<RegistroFront[]>([])

const loadingColaboradores = ref(false)
const loadingPontos = ref(false)
const savingId = ref<number | null>(null)

const pagination = ref({
  page: 1,
  rowsPerPage: 0,
  sortBy: '',
  descending: false
})

/* ========================= Guards ========================= */
function isColaboradorApiArray(x: unknown): x is ColaboradorApi[] {
  return Array.isArray(x) && x.every((r) => r && typeof r === 'object')
}
function isRegistroApiArray(x: unknown): x is RegistroApi[] {
  return Array.isArray(x) && x.every((r) => r && typeof r === 'object' && 'id' in (r as object))
}

/* ========================= Datas (BR safe) ========================= */
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/
function toBrDate(dateLike?: string | Date | null): Date | null {
  if (!dateLike) return null
  const d = typeof dateLike === 'string' ? new Date(dateLike) : dateLike
  return isNaN(d.getTime()) ? null : d
}
function parseDateOnlyLocal(s?: string | null): Date | null {
  if (!s) return null
  if (ISO_DATE_RE.test(s)) {
    const [yStr, mStr, dStr] = s.split('-')
    const y = Number(yStr)
    const m = Number(mStr)
    const d = Number(dStr)
    return new Date(y, m - 1, d) // meia-noite local
  }
  return toBrDate(s)
}

function brDateFromIsoDateOnly(s?: string | null): string {
  if (!s) return '-'
  if (ISO_DATE_RE.test(s)) {
    const [y, m, d] = s.split('-')
    return `${d}/${m}/${y}`
  }
  const d = toBrDate(s)
  return d ? d.toLocaleDateString('pt-BR') : '-'
}
function fmtDiaSemana(d: Date | null): string {
  if (!d) return ''
  return d.toLocaleDateString('pt-BR', { weekday: 'short' }).toUpperCase()
}
function dateSortKey(s?: string | null): number {
  if (!s) return 0
  if (ISO_DATE_RE.test(s)) {
    const [y, m, d] = s.split('-').map(Number) as [number, number, number]
    return y * 10000 + m * 100 + d
  }
  const d = toBrDate(s)
  return d ? d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate() : 0
}

/** Converte ISO ou 'YYYY-MM-DDTHH:mm:ss' para 'YYYY-MM-DDTHH:mm' p/ <input type="datetime-local"> */
function toLocalDatetimeInput(val: IsoStr): string | null {
  if (!val) return null
  // pega os 16 primeiros chars 'YYYY-MM-DDTHH:mm' quando vier com segundos
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(val)) return val.slice(0, 16)
  // se vier como ISO completo do backend, Date->format local
  const d = toBrDate(val)
  if (!d) return null
  const yyyy = String(d.getFullYear())
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}`
}

/* ========================= Normalização ========================= */
function normalizeRegistroFromApi(r: RegistroApi): RegistroFront {
  const dLocal = parseDateOnlyLocal(r.data || null)
  return {
    ...r,
    entrada: toLocalDatetimeInput(r.entrada),
    saida_almoco: toLocalDatetimeInput(r.saida_almoco),
    volta_almoco: toLocalDatetimeInput(r.volta_almoco),
    saida: toLocalDatetimeInput(r.saida),
    _data_fmt: brDateFromIsoDateOnly(r.data),
    _dia_fmt: fmtDiaSemana(dLocal) || '-',
    rowKey: `${r.id ?? 'just'}_${r.data ?? Math.random()}`
  }
}

/* ========================= Colunas ========================= */
const columns: QTableColumn<RegistroFront>[] = [
  { name: 'data',         label: 'Data',           field: (row) => row._data_fmt,  align: 'center' },
  { name: 'dia',          label: 'Dia',            field: (row) => row._dia_fmt,   align: 'center' },
  { name: 'entrada',      label: 'Entrada',        field: 'entrada',               align: 'center' },
  { name: 'saida_almoco', label: 'Almoço saída',   field: 'saida_almoco',          align: 'center' },
  { name: 'volta_almoco', label: 'Almoço retorno', field: 'volta_almoco',          align: 'center' },
  { name: 'saida',        label: 'Saída',          field: 'saida',                 align: 'center' },
  { name: 'actions',      label: 'Ações',          field: () => '',                align: 'center' }
]

/* ========================= Data Loading ========================= */
async function carregarColaboradores(): Promise<void> {
  loadingColaboradores.value = true
  try {
    const res = await api.get('/colaboradores')
    const raw = res.data as unknown

    if (isColaboradorApiArray(raw)) {
      colaboradores.value = raw.map((c) => ({
        id: Number(c.id ?? c.code ?? 0),
        nome: String(c.nome ?? '')
      })).filter((c) => Number.isFinite(c.id) && c.nome.length > 0)
    } else {
      colaboradores.value = []
    }
  } catch {
    colaboradores.value = []
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaboradores' })
  } finally {
    loadingColaboradores.value = false
  }
}

async function buscarPontos(): Promise<void> {
  if (!colaboradorSelecionado.value || !mesSelecionado.value) return

  const [anoStr, mesStr] = mesSelecionado.value.split('-') // "YYYY-MM"
  const ano = Number(anoStr)
  const mes = Number(mesStr)
  if (!ano || !mes) return

  // range seguro (sem toISOString → evita UTC shift)
  const inicio = `${ano}-${String(mes).padStart(2, '0')}-01`
  const lastDayNum = new Date(ano, mes, 0).getDate()
  const fim = `${ano}-${String(mes).padStart(2, '0')}-${String(lastDayNum).padStart(2, '0')}`

  loadingPontos.value = true
  try {
    const res = await api.get('/pontos/por-data', {
      params: { colaborador_id: Number(colaboradorSelecionado.value), inicio, fim }
    })
    const raw = res.data as unknown

    if (isRegistroApiArray(raw)) {
      registros.value = raw
        .map((r) => normalizeRegistroFromApi(r))
        .sort((a, b) => dateSortKey(a.data) - dateSortKey(b.data))
    } else {
      registros.value = []
    }
  } catch {
    registros.value = []
    Notify.create({ type: 'negative', message: 'Erro ao carregar pontos do colaborador' })
  } finally {
    loadingPontos.value = false
  }
}

/* Debounce automático ao mudar filtros (igual ao visualizar) */
let buscarTimeout: number | undefined
watch([colaboradorSelecionado, mesSelecionado], () => {
  if (buscarTimeout !== undefined) window.clearTimeout(buscarTimeout)
  buscarTimeout = window.setTimeout(() => { void buscarPontos() }, 250)
})

/* ========================= Save ========================= */
async function salvarAlteracao(registro: RegistroFront): Promise<void> {
  if (!registro.id) return
  savingId.value = registro.id
  try {
    await api.put(`/pontos/${registro.id}`, {
      entrada: registro.entrada,
      saida_almoco: registro.saida_almoco,
      volta_almoco: registro.volta_almoco,
      saida: registro.saida
    })
    Notify.create({ type: 'positive', message: 'Registro atualizado com sucesso!' })
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar registro' })
  } finally {
    savingId.value = null
  }
}

/* ========================= Lifecycle ========================= */
onMounted(async () => {
  await carregarColaboradores()
  // pré-seleciona mês atual
  const hoje = new Date()
  const yyyy = hoje.getFullYear()
  const mm = String(hoje.getMonth() + 1).padStart(2, '0')
  mesSelecionado.value = `${yyyy}-${mm}`
})
</script>

<style scoped>
/* ajustes visuais pequenos */
</style>
