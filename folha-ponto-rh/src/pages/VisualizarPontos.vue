<template>
  <q-page class="q-pa-md">
    <q-card :style="{ border: `1px solid ${roleAccent}` }" class="overflow-hidden">

      <!-- faixa decorativa com gradiente dinâmico -->
      <div
        class="role-gradient-bar"
        :style="{
          background: `linear-gradient(90deg, ${roleAccent} 0%, ${roleAccentSoft} 100%)`
        }"
      />

      <q-card-section class="row items-center justify-between">
        <div class="text-h6" :style="{ color: roleAccentText }">
          Visualizar pontos por colaborador
        </div>

        <div v-if="registros.length" class="row items-center q-gutter-sm">
          <q-chip outline color="primary" text-color="primary" icon="query_builder">
            Total do mês: <strong class="q-ml-xs">{{ totalMesHHMMSS }}</strong>
          </q-chip>

          <q-chip
            outline
            :color="roleChipProps.color"
            :text-color="roleChipProps.text"
            icon="badge"
          >
            <strong class="q-ml-xs text-capitalize">{{ selectedRole }}</strong>
            <q-tooltip anchor="bottom middle" self="top middle">
              Papel: {{ selectedRole }}
            </q-tooltip>
          </q-chip>

          <q-btn
            label="Exportar para Excel"
            color="secondary"
            @click="exportarExcel"
            :disable="registros.length === 0"
            :loading="exportLoading"
            icon="download"
          />
        </div>
      </q-card-section>

      <q-separator />

      <!-- Filtros -->
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

          <div class="col-12">
            <q-btn
              color="primary"
              label="Buscar"
              :disable="!colaboradorSelecionado || !mesSelecionado"
              :loading="loadingPontos"
              @click="buscarPontos"
              icon="search"
            />
          </div>
        </div>
      </q-card-section>

      <!-- MINI CARD -->
      <q-separator v-if="registros.length" />
      <q-card-section v-if="registros.length">
        <q-card
          flat
          bordered
          class="q-pa-md"
          :style="{ borderColor: roleAccent }"
        >
          <div class="row q-col-gutter-md items-center">
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Dias úteis considerados</div>
              <div class="text-h6">{{ diasUteisConsiderados }}</div>
            </div>
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Total esperado ({{ esperadoDiaLabel }})</div>
              <div class="text-h6">{{ esperadoMesHHMM }}</div>
            </div>
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Total trabalhado</div>
              <div class="text-h6">{{ totalMesHHMM }}</div>
            </div>
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Saldo</div>
              <q-chip
                :color="saldoColor"
                text-color="white"
                class="text-weight-medium text-subtitle1"
              >
                {{ saldoPrefix }}{{ saldoMesHHMM }}
              </q-chip>
            </div>
          </div>
          <div class="text-caption text-grey-6 q-mt-sm">
            * Contabiliza somente <strong>seg–sex</strong>. Se for o mês atual, considera até <strong>{{ limiteContagemLabel }}</strong>.
          </div>
        </q-card>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-table
          :rows="registros"
          :columns="columns"
          row-key="id"
          dense
          flat
          bordered
          :loading="loadingPontos"
          :rows-per-page-options="[10, 20, 50, 0]"
          v-model:pagination="pagination"
          :table-header-style="{ backgroundColor: roleAccent, color: '#fff' }"
        >
          <template #loading>
            <q-inner-loading showing>
              <q-spinner-dots size="32px" />
            </q-inner-loading>
          </template>

          <template #body-cell-data="props">
            <q-td :props="props" class="text-center">{{ props.row._data_fmt }}</q-td>
          </template>
          <template #body-cell-dia="props">
            <q-td :props="props" class="text-center">{{ props.row._dia_fmt }}</q-td>
          </template>
          <template #body-cell-entrada="props">
            <q-td :props="props" class="text-center">{{ props.row._entrada_fmt }}</q-td>
          </template>
          <template #body-cell-saida_almoco="props">
            <q-td :props="props" class="text-center">{{ props.row._salm_fmt }}</q-td>
          </template>
          <template #body-cell-volta_almoco="props">
            <q-td :props="props" class="text-center">{{ props.row._valm_fmt }}</q-td>
          </template>
          <template #body-cell-saida="props">
            <q-td :props="props" class="text-center">{{ props.row._saida_fmt }}</q-td>
          </template>
          <template #body-cell-total_dia="props">
            <q-td :props="props" class="text-center">
              <q-badge color="primary" outline>{{ props.row._total_fmt }}</q-badge>
            </q-td>
          </template>
          <template #body-cell-alterado_por="props">
            <q-td :props="props" class="text-center">
              <q-chip
                v-if="props.row._edited"
                dense
                color="amber"
                text-color="black"
                outline
              >
                {{ props.row._alterado_por_nome }}
                <q-tooltip anchor="bottom middle" self="top middle">
                  Editado por {{ props.row._alterado_por_nome }}
                </q-tooltip>
              </q-chip>
              <span v-else>—</span>
            </q-td>
          </template>

          <template #bottom>
            <div class="full-width row justify-end q-pa-sm q-gutter-sm">
              <q-chip v-if="registros.length" color="grey-3" text-color="dark">
                Registros: {{ registros.length }}
              </q-chip>
              <q-chip v-if="registros.length" color="amber-3" text-color="black" icon="history_edu">
                Edições: {{ totalEditados }}
              </q-chip>
            </div>
          </template>
        </q-table>

        <div v-if="!loadingPontos && registros.length === 0" class="q-mt-lg">
          <q-banner class="bg-grey-2 text-grey-9">
            <template #avatar>
              <q-icon name="info" />
            </template>
            Nenhum registro encontrado. Selecione um colaborador e um mês e clique em <strong>Buscar</strong>.
          </q-banner>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { Notify } from 'quasar';
import { api } from 'boot/axios';
import * as XLSX from 'xlsx';
import type { QTableColumn } from 'quasar';

const pagination = ref({
  page: 1,
  rowsPerPage: 0, // 0 = todas as linhas
  sortBy: '',
  descending: false
});

/* ========================= Tipagens ========================= */
type IsoStr = string | null | undefined;
type Role = 'funcionario' | 'gestao' | 'estagiario';

interface RegistroApi {
  id: number;
  data?: IsoStr;          // YYYY-MM-DD (date only) ou ISO datetime
  entrada?: IsoStr;
  saida_almoco?: IsoStr;
  volta_almoco?: IsoStr;
  saida?: IsoStr;

  // enriquecidos pelo backend (joinedload)
  alterado_por?: { nome?: string } | null;
}

interface RegistroFront extends RegistroApi {
  _data_fmt: string;      // dd/MM/yyyy
  _dia_fmt: string;       // QUI., SEX., ...
  _entrada_fmt: string;   // HH:mm
  _salm_fmt: string;      // HH:mm
  _valm_fmt: string;      // HH:mm
  _saida_fmt: string;     // HH:mm
  _total_fmt: string;     // HH:MM:SS
  _total_min: number;     // minutos inteiros

  // campos para UI
  _edited: boolean;
  _alterado_por_nome: string;
}

interface Colaborador {
  id: number;
  nome: string;
}

interface ColaboradorApi {
  id?: number | string;
  code?: number | string;
  nome?: string;
  role?: string;
}

/* ========================= State ========================= */
const colaboradores = ref<Colaborador[]>([]);
const colaboradorSelecionado = ref<number | null>(null);
const mesSelecionado = ref<string | null>(null);
const registros = ref<RegistroFront[]>([]);

const loadingColaboradores = ref(false);
const loadingPontos = ref(false);
const exportLoading = ref(false);

/* ===== Jornada dinâmica ===== */
const JORNADA_FUNC_MIN = 8 * 60 + 48; // 528
const JORNADA_EST_MIN  = 6 * 60;      // 360
const selectedRole = ref<Role>('funcionario'); // default

/* ========================= Type Guards ========================= */
function isRegistroApi(x: unknown): x is RegistroApi {
  if (!x || typeof x !== 'object') return false;
  const r = x as Record<string, unknown>;
  return typeof r['id'] === 'number';
}
function isRegistroApiArray(x: unknown): x is RegistroApi[] {
  return Array.isArray(x) && x.every(isRegistroApi);
}
function isColaboradorApi(x: unknown): x is ColaboradorApi {
  if (!x || typeof x !== 'object') return false;
  const r = x as Record<string, unknown>;
  return 'id' in r || 'code' in r || 'nome' in r || 'role' in r;
}
function isColaboradorApiArray(x: unknown): x is ColaboradorApi[] {
  return Array.isArray(x) && x.every(isColaboradorApi);
}

/* ========================= Helpers ========================= */
function toBrDate(dateLike?: string | Date | null): Date | null {
  if (!dateLike) return null;
  const d = typeof dateLike === 'string' ? new Date(dateLike) : dateLike;
  return isNaN(d.getTime()) ? null : d;
}
function fmtDiaSemana(d: Date | null): string {
  if (!d) return '';
  return d.toLocaleDateString('pt-BR', { weekday: 'short' }).toUpperCase();
}
function fmtHora(d: Date | null): string {
  if (!d) return '';
  return d.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'America/Sao_Paulo'
  });
}
function minutesToHHMM(min: number): string {
  const absMin = Math.max(0, Math.trunc(min));
  const h = Math.floor(absMin / 60);
  const m = absMin % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}
function minutesToHHMMSS(min: number): string {
  return `${minutesToHHMM(min)}:00`;
}

/* ===== Date-only safe (evita UTC shift) ===== */
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function parseDateOnlyLocal(s?: string | null): Date | null {
  if (!s) return null;
  if (ISO_DATE_RE.test(s)) {
    const [yStr, mStr, dStr] = s.split('-');
    const y = parseInt(yStr as string, 10);
    const m = parseInt(mStr as string, 10);
    const d = parseInt(dStr as string, 10);
    return new Date(y, m - 1, d); // meia-noite local
  }
  return toBrDate(s);
}
function brDateFromIsoDateOnly(s?: string | null): string {
  if (!s) return '-';
  if (ISO_DATE_RE.test(s)) {
    const [y, m, d] = s.split('-');
    return `${d}/${m}/${y}`;
  }
  const d = toBrDate(s);
  return d ? d.toLocaleDateString('pt-BR') : '-';
}
function dateSortKey(s?: string | null): number {
  if (!s) return 0;
  if (ISO_DATE_RE.test(s)) {
    const [y, m, d] = s.split('-').map(Number) as [number, number, number];
    return y * 10000 + m * 100 + d;
  }
  const d = toBrDate(s);
  return d ? d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate() : 0;
}

/** Total diário em minutos: (saida-entrada) - pausa almoço */
function calcMinDia(reg: { entrada?: IsoStr; saida?: IsoStr; saida_almoco?: IsoStr; volta_almoco?: IsoStr; }): number {
  const entrada = toBrDate(reg.entrada || null);
  const saida   = toBrDate(reg.saida   || null);
  if (!entrada || !saida) return 0;

  let ms = saida.getTime() - entrada.getTime();

  const sAlm = toBrDate(reg.saida_almoco || null);
  const vAlm = toBrDate(reg.volta_almoco || null);
  if (sAlm && vAlm) ms -= (vAlm.getTime() - sAlm.getTime());

  return Math.max(0, Math.round(ms / 60000)); // minutos inteiros
}

function normalizeRegistroFromApi(r: RegistroApi): RegistroFront {
  const dLocal = parseDateOnlyLocal(r.data || null);
  const totalDiaMin = calcMinDia(r);
  const alteradorNome = r?.alterado_por?.nome ? String(r.alterado_por.nome) : '';

  return {
    ...r,
    _data_fmt:   brDateFromIsoDateOnly(r.data),
    _dia_fmt:    fmtDiaSemana(dLocal) || '-',
    _entrada_fmt: fmtHora(toBrDate(r.entrada || null)) || '-',
    _salm_fmt:    fmtHora(toBrDate(r.saida_almoco || null)) || '-',
    _valm_fmt:    fmtHora(toBrDate(r.volta_almoco || null)) || '-',
    _saida_fmt:   fmtHora(toBrDate(r.saida || null)) || '-',
    _total_fmt:   minutesToHHMMSS(totalDiaMin),
    _total_min:   totalDiaMin,
    _edited:      Boolean(alteradorNome),
    _alterado_por_nome: alteradorNome || '—'
  };
}

/* ========================= Colunas ========================= */
const columns: QTableColumn<RegistroFront>[] = [
  { name: 'data',         label: 'Data',           field: (row: RegistroFront) => row._data_fmt,  align: 'center' },
  { name: 'dia',          label: 'Dia',            field: (row: RegistroFront) => row._dia_fmt,   align: 'center' },
  { name: 'entrada',      label: 'Entrada',        field: (row: RegistroFront) => row._entrada_fmt, align: 'center' },
  { name: 'saida_almoco', label: 'Almoço saída',   field: (row: RegistroFront) => row._salm_fmt,  align: 'center' },
  { name: 'volta_almoco', label: 'Almoço retorno', field: (row: RegistroFront) => row._valm_fmt,  align: 'center' },
  { name: 'saida',        label: 'Saída',          field: (row: RegistroFront) => row._saida_fmt, align: 'center' },
  { name: 'total_dia',    label: 'Total Dia',      field: (row: RegistroFront) => row._total_fmt, align: 'center' },
  { name: 'alterado_por', label: 'Alterado por',   field: (row: RegistroFront) => row._alterado_por_nome, align: 'center' }
];

/* ========================= Data Loading ========================= */
async function carregarColaboradores(): Promise<void> {
  loadingColaboradores.value = true;
  try {
    const res = await api.get('/colaboradores');
    const raw = res.data as unknown;

    if (isColaboradorApiArray(raw)) {
      colaboradores.value = raw.map((c) => ({
        id: Number(c.id ?? c.code ?? 0),
        nome: String(c.nome ?? '')
      })).filter((c) => Number.isFinite(c.id) && c.nome.length > 0);
    } else {
      colaboradores.value = [];
    }
  } catch {
    colaboradores.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaboradores' });
  } finally {
    loadingColaboradores.value = false;
  }
}

async function carregarRoleDoColaborador(id: number): Promise<void> {
  try {
    const res = await api.get(`/colaboradores/${id}`);
    const r = res.data as ColaboradorApi;
    const role = (r && typeof r.role === 'string') ? r.role : 'funcionario';
    selectedRole.value = (['funcionario', 'gestao', 'estagiario'].includes(role) ? role : 'funcionario') as Role;
  } catch {
    selectedRole.value = 'funcionario'; // fallback
  }
}

function inferirRolePelosRegistros(rows: RegistroFront[]): Role | null {
  if (!rows.length) return null;
  const temAlmoco = rows.some(r => (r._salm_fmt && r._salm_fmt !== '-') || (r._valm_fmt && r._valm_fmt !== '-'));
  if (!temAlmoco) return 'estagiario';
  return null;
}

async function buscarPontos(): Promise<void> {
  if (!colaboradorSelecionado.value || !mesSelecionado.value) return;

  const [anoStr, mesStr] = mesSelecionado.value.split('-'); // "YYYY-MM"
  const ano = Number(anoStr);
  const mes = Number(mesStr); // 1..12
  if (!ano || !mes) return;

  // 1) atualiza o role do colaborador selecionado
  await carregarRoleDoColaborador(Number(colaboradorSelecionado.value));

  // 2) range YYYY-MM-DD (sem toISOString)
  const inicio = `${ano}-${String(mes).padStart(2, '0')}-01`;
  const lastDayNum = new Date(ano, mes, 0).getDate();
  const fim = `${ano}-${String(mes).padStart(2, '0')}-${String(lastDayNum).padStart(2, '0')}`;

  loadingPontos.value = true;
  try {
    const res = await api.get('/pontos/por-data', {
      params: { colaborador_id: Number(colaboradorSelecionado.value), inicio, fim }
    });

    const raw = res.data as unknown;

    if (isRegistroApiArray(raw)) {
      registros.value = raw
        .map((r: RegistroApi) => normalizeRegistroFromApi(r))
        .sort((a: RegistroFront, b: RegistroFront) => dateSortKey(a.data) - dateSortKey(b.data));

      // fallback: se não veio role, tenta inferir (sem almoço)
      const inf = inferirRolePelosRegistros(registros.value);
      if (inf && selectedRole.value !== inf) selectedRole.value = inf;
    } else {
      registros.value = [];
    }
  } catch {
    registros.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao buscar pontos do colaborador' });
  } finally {
    loadingPontos.value = false;
  }
}

/* Atualiza automaticamente ao mudar filtros (debounce) */
let buscarTimeout: number | undefined;
watch([colaboradorSelecionado, mesSelecionado], () => {
  if (buscarTimeout !== undefined) window.clearTimeout(buscarTimeout);
  buscarTimeout = window.setTimeout(() => { void buscarPontos(); }, 250);
});

/* ========================= Totais & Banco de Horas ========================= */
function countBusinessDaysOfMonth(yyyy: number, mm1to12: number, limitToToday = true): number {
  const first = new Date(yyyy, mm1to12 - 1, 1);
  const last  = new Date(yyyy, mm1to12, 0);
  const today = new Date();

  const end = (limitToToday && today.getFullYear() === yyyy && (today.getMonth() + 1) === mm1to12)
    ? new Date(yyyy, mm1to12 - 1, today.getDate())
    : last;

  let count = 0;
  for (let d = new Date(first); d <= end; d.setDate(d.getDate() + 1)) {
    const dow = d.getDay(); // 0=dom, 6=sáb
    if (dow !== 0 && dow !== 6) count++;
  }
  return count;
}

const totalMesMin     = computed<number>(() => registros.value.reduce((acc, r) => acc + r._total_min, 0));
const totalMesHHMM    = computed<string>(() => minutesToHHMM(totalMesMin.value));
const totalMesHHMMSS  = computed<string>(() => minutesToHHMMSS(totalMesMin.value));

const diasUteisConsiderados = computed<number>(() => {
  if (!mesSelecionado.value) return 0;
  const [yStr, mStr] = mesSelecionado.value.split('-');
  const y = Number(yStr);
  const m = Number(mStr);
  if (!y || !m) return 0;
  return countBusinessDaysOfMonth(y, m, true);
});

/* —— JORNADA dinâmica por role —— */
const jornadaAlvoMin = computed<number>(() =>
  selectedRole.value === 'estagiario' ? JORNADA_EST_MIN : JORNADA_FUNC_MIN
);

const esperadoDiaLabel = computed<string>(() =>
  selectedRole.value === 'estagiario' ? '6h/dia' : '8h48/dia'
);

const esperadoMesMin    = computed<number>(() => diasUteisConsiderados.value * jornadaAlvoMin.value);
const esperadoMesHHMM   = computed<string>(() => minutesToHHMM(esperadoMesMin.value));
const esperadoMesHHMMSS = computed<string>(() => minutesToHHMMSS(esperadoMesMin.value));

const saldoMesMin  = computed<number>(() => totalMesMin.value - esperadoMesMin.value);
const saldoMesHHMM = computed<string>(() => minutesToHHMM(Math.abs(saldoMesMin.value)));
const saldoPrefix  = computed<string>(() => (saldoMesMin.value >= 0 ? '+' : '-'));
const saldoColor   = computed<'positive' | 'negative' | 'grey'>(() =>
  saldoMesMin.value > 0 ? 'positive' : (saldoMesMin.value < 0 ? 'negative' : 'grey')
);

const totalEditados = computed<number>(() => registros.value.filter(r => r._edited).length);

const limiteContagemLabel = computed<string>(() => {
  if (!mesSelecionado.value) return '';
  const [yStr, mStr] = mesSelecionado.value.split('-');
  const y = Number(yStr);
  const m = Number(mStr);
  const today = new Date();
  const isCurrentMonth = today.getFullYear() === y && (today.getMonth() + 1) === m;
  return isCurrentMonth ? today.toLocaleDateString('pt-BR') : new Date(y, m, 0).toLocaleDateString('pt-BR');
});

/* ===== Tema dinâmico por papel ===== */
const roleChipProps = computed(() => {
  const map: Record<Role, { color: string; text: string }> = {
    funcionario: { color: 'secondary',     text: 'secondary' },
    gestao:      { color: 'deep-purple-6', text: 'white'     },
    estagiario:  { color: 'orange-6',      text: 'orange-6'  }
  };
  return map[selectedRole.value] ?? map.funcionario;
});

// cores para bordas, header e gradiente (hex)
const roleAccent = computed<string>(() => {
  switch (selectedRole.value) {
    case 'gestao':     return '#673ab7';  // deep-purple-6
    case 'estagiario': return '#fb8c00';  // orange-6
    default:           return '#26a69a';  // secondary (teal-ish)
  }
});

// versão "soft" pro gradiente (mesma cor com mais claro)
const roleAccentSoft = computed<string>(() => {
  switch (selectedRole.value) {
    case 'gestao':     return '#b39ddb';  // purple claro
    case 'estagiario': return '#ffcc80';  // orange claro
    default:           return '#80cbc4';  // teal claro
  }
});

const roleAccentText = computed<string>(() => {
  return selectedRole.value === 'gestao' ? '#4527a0'
       : selectedRole.value === 'estagiario' ? '#e65100'
       : '#1f7d73';
});

/* ========================= Export ========================= */
function exportarExcel(): void {
  exportLoading.value = true;
  try {
    const linhas: string[][] = registros.value.map((row: RegistroFront) => ([
      row._data_fmt,
      row._dia_fmt,
      row._entrada_fmt !== '-' ? row._entrada_fmt : '',
      row._salm_fmt    !== '-' ? row._salm_fmt    : '',
      row._valm_fmt    !== '-' ? row._valm_fmt    : '',
      row._saida_fmt   !== '-' ? row._saida_fmt   : '',
      row._total_fmt
    ]));

    const wsData: string[][] = [
      ['DATA', 'DIA', 'Entrada', 'Almoço saída', 'Almoço retorno', 'Saída', 'Total DIA'],
      ...linhas,
      ['', '', '', '', '', 'TOTAL MÊS', totalMesHHMMSS.value],
      ['', '', '', '', '', `ESPERADO (${esperadoDiaLabel.value})`, esperadoMesHHMMSS.value],
      ['', '', '', '', '', 'SALDO', `${saldoPrefix.value}${saldoMesHHMM.value}:00`]
    ];

    const ws = XLSX.utils.aoa_to_sheet(wsData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Folha - Ponto');

    const colaborador = colaboradores.value.find((c: Colaborador) => c.id === colaboradorSelecionado.value);
    const nomeArquivo = colaborador ? colaborador.nome.replace(/\s+/g, '_') : String(colaboradorSelecionado.value ?? 'colaborador');

    XLSX.writeFile(wb, `FOLHA-PONTO_${nomeArquivo}.xlsx`);
  } finally {
    exportLoading.value = false;
  }
}

/* ========================= Lifecycle ========================= */
onMounted(async () => {
  await carregarColaboradores();
  // pré-seleciona mês atual
  const hoje = new Date();
  const yyyy = hoje.getFullYear();
  const mm = String(hoje.getMonth() + 1).padStart(2, '0');
  mesSelecionado.value = `${yyyy}-${mm}`;
});

// atualiza o role assim que escolher um colaborador
watch(colaboradorSelecionado, async (id) => {
  if (id) await carregarRoleDoColaborador(Number(id));
});
</script>

<style scoped>
/* faixa decorativa superior */
.role-gradient-bar {
  height: 6px;
  width: 100%;
}
</style>
