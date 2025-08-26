<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 1000px;">
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Meus registros de ponto</div>

        <div v-if="registros.length" class="row items-center q-gutter-sm">
          <q-chip outline color="primary" text-color="primary" icon="query_builder">
            Total do mês: <strong class="q-ml-xs">{{ totalMesHHMMSS }}</strong>
          </q-chip>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Filtro: apenas mês, busca automática -->
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-input
              v-model="mesSelecionado"
              label="Selecione o mês"
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

      <!-- Resumo do mês -->
      <q-separator v-if="registros.length" />
      <q-card-section v-if="registros.length">
        <q-card flat bordered class="q-pa-md">
          <div class="row q-col-gutter-md items-center">
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Dias úteis considerados</div>
              <div class="text-h6">{{ diasUteisConsiderados }}</div>
            </div><!--
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Total esperado (8h/dia)</div>
              <div class="text-h6">{{ esperadoMesHHMM }}</div>
            </div>-->
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Total trabalhado</div>
              <div class="text-h6">{{ totalMesHHMM }}</div>
            </div><!--
            <div class="col-6 col-sm-3">
              <div class="text-caption text-grey-7">Saldo</div>
              <q-chip :color="saldoColor" text-color="white" class="text-weight-medium text-subtitle1">
                {{ saldoPrefix }}{{ saldoMesHHMM }}
              </q-chip>
            </div>
            -->
          </div>
          <div class="text-caption text-grey-6 q-mt-sm">
            * Contabiliza somente <strong>seg–sex</strong>. Se for o mês atual, considera até
            <strong>{{ limiteContagemLabel }}</strong>.
          </div>
        </q-card>
      </q-card-section>

      <q-separator />

      <!-- Tabela -->
      <q-card-section>
        <q-table
          :rows="registros"
          :columns="columns"
          row-key="id"
          dense
          flat
          bordered
          :loading="loading"
          :rows-per-page-options="[10, 20, 50, 0]"
          v-model:pagination="pagination"
          no-data-label="Sem registros para o período selecionado"
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
          <template #body-cell-status="props">
            <q-td :props="props" class="text-center">
              <q-badge
                :color="props.row._completo ? 'positive' : 'negative'"
                :label="props.row._completo ? 'Completo' : 'Incompleto'"
                outline
              >
              </q-badge>
              <q-tooltip v-if="!props.row._completo">
                Faltando: {{ props.row._faltando.join(', ') }}
              </q-tooltip>
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

        <div v-if="!loading && registros.length === 0" class="q-mt-lg">
          <q-banner class="bg-grey-2 text-grey-9">
            <template #avatar><q-icon name="info" /></template>
            Nenhum registro encontrado. Selecione um mês.
          </q-banner>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { QTableColumn } from 'quasar';

/* ===== Tipos ===== */
type IsoStr = string | null | undefined;

interface UsuarioMin { id: number; nome: string; }
interface RegistroApi {
  id: number;
  data: string;             // YYYY-MM-DD ou ISO
  entrada: IsoStr;
  saida_almoco: IsoStr;
  volta_almoco: IsoStr;
  saida: IsoStr;
  alterado_por?: UsuarioMin | null;
}
interface RegistroFront extends RegistroApi {
  _data_fmt: string;        // dd/MM/yyyy
  _dia_fmt: string;         // QUI., SEX., ...
  _entrada_fmt: string;     // HH:mm
  _salm_fmt: string;        // HH:mm
  _valm_fmt: string;        // HH:mm
  _saida_fmt: string;       // HH:mm
  _total_fmt: string;       // HH:MM:SS
  _total_min: number;       // minutos do dia
  _completo: boolean;       // Entrada & Saída presentes (almoço opcional)
  _faltando: string[];      // lista amigável do que falta
}

/* ===== Estado ===== */
const mesSelecionado = ref<string | null>(null);
const registros = ref<RegistroFront[]>([]);
const loading = ref(false);

/* QTable: mostrar tudo por padrão */
const pagination = ref({ page: 1, rowsPerPage: 0, sortBy: '', descending: false });

/* ===== Colunas ===== */
const columns: QTableColumn<RegistroFront>[] = [
  { name: 'data',         label: 'Data',           field: r => r._data_fmt,  align: 'center' },
  { name: 'dia',          label: 'Dia',            field: r => r._dia_fmt,   align: 'center' },
  { name: 'entrada',      label: 'Entrada',        field: r => r._entrada_fmt, align: 'center' },
  { name: 'saida_almoco', label: 'Almoço saída',   field: r => r._salm_fmt,  align: 'center' },
  { name: 'volta_almoco', label: 'Almoço retorno', field: r => r._valm_fmt,  align: 'center' },
  { name: 'saida',        label: 'Saída',          field: r => r._saida_fmt, align: 'center' },
  { name: 'total_dia',    label: 'Total Dia',      field: r => r._total_fmt, align: 'center' },
  { name: 'status',       label: 'Status',         field: () => '',          align: 'center' }
];

/* ===== Helpers de data ===== */
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function toLocalDate(s?: string | null): Date | null {
  if (!s) return null;
  const d = new Date(s);
  return isNaN(d.getTime()) ? null : d;
}
function brDateFromIsoDateOnly(s?: string | null): string {
  if (!s) return '-';
  if (ISO_DATE_RE.test(s)) {
    const [y, m, d] = s.split('-') as [string, string, string];
    return `${d}/${m}/${y}`;
  }
  const d = toLocalDate(s);
  return d ? d.toLocaleDateString('pt-BR') : '-';
}
function fmtHora(iso?: IsoStr): string {
  if (!iso) return '-';
  const d = toLocalDate(iso);
  if (!d) return '-';
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' });
}

/** Total diário em minutos: (saida-entrada) - pausa almoço (se existir) */
function calcMinDia(reg: { entrada?: IsoStr; saida?: IsoStr; saida_almoco?: IsoStr; volta_almoco?: IsoStr; }): number {
  const entrada = toLocalDate(reg.entrada || null);
  const saida   = toLocalDate(reg.saida   || null);
  if (!entrada || !saida) return 0;

  let ms = saida.getTime() - entrada.getTime();
  const sAlm = toLocalDate(reg.saida_almoco || null);
  const vAlm = toLocalDate(reg.volta_almoco || null);
  if (sAlm && vAlm) ms -= (vAlm.getTime() - sAlm.getTime());

  return Math.max(0, Math.round(ms / 60000));
}

/* ===== Completo / Incompleto =====
   Regras:
   - "Completo" = tem Entrada e Saída (almoço opcional) → cobre estagiário (2 batidas)
   - "Incompleto" = faltando Entrada ou Saída.
   Tooltip lista o que estiver faltando.
*/
function completenessInfo(r: RegistroApi): { completo: boolean; faltando: string[] } {
  const faltando: string[] = [];
  if (!r.entrada) faltando.push('Entrada');
  if (!r.saida)   faltando.push('Saída');
  // almoço é opcional; se quiser marcar também: descomente abaixo
  // if (!r.saida_almoco) faltando.push('Saída almoço');
  // if (!r.volta_almoco) faltando.push('Volta almoço');
  return { completo: faltando.length === 0, faltando };
}

/* ===== Normalização ===== */
function normalize(r: RegistroApi): RegistroFront {
  const totalMin = calcMinDia(r);
  const { completo, faltando } = completenessInfo(r);
  return {
    ...r,
    _data_fmt:   brDateFromIsoDateOnly(r.data),
    _dia_fmt:    (toLocalDate(r.data)?.toLocaleDateString('pt-BR', { weekday: 'short' }).toUpperCase() ?? '-'),
    _entrada_fmt: fmtHora(r.entrada),
    _salm_fmt:    fmtHora(r.saida_almoco),
    _valm_fmt:    fmtHora(r.volta_almoco),
    _saida_fmt:   fmtHora(r.saida),
    _total_fmt:   minutesToHHMMSS(totalMin),
    _total_min:   totalMin,
    _completo:    completo,
    _faltando:    faltando
  };
}

function minutesToHHMM(min: number): string {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}
function minutesToHHMMSS(min: number): string {
  return `${minutesToHHMM(min)}:00`;
}

/* ===== API ===== */
async function buscarPontos(): Promise<void> {
  if (!mesSelecionado.value) return;
  loading.value = true;
  try {
    const me = await api.get('/me/colaborador', { withCredentials: true });
    const colaboradorId = me.data.id as number;

    const [anoStr, mesStr] = mesSelecionado.value.split('-');
    const ano = Number(anoStr);
    const mes = Number(mesStr);

    const inicio = `${ano}-${String(mes).padStart(2, '0')}-01`;
    const lastDay = new Date(ano, mes, 0).getDate();
    const fim = `${ano}-${String(mes).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

    const res = await api.get('/pontos/por-data', {
      params: { colaborador_id: colaboradorId, inicio, fim },
      withCredentials: true
    });

    const raw = res.data as unknown;
    registros.value = Array.isArray(raw) ? (raw as RegistroApi[]).map(normalize) : [];
  } catch (e) {
    console.error(e);
    registros.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao buscar seus pontos' });
  } finally {
    loading.value = false;
  }
}

/* ===== Watch: busca automática ao trocar mês ===== */
watch(mesSelecionado, () => { void buscarPontos(); });

/* ===== Totais e saldo (8h/dia) ===== */
//const JORNADA_ALVO_MIN = 8 * 60;

function countBusinessDaysOfMonth(yyyy: number, mm1to12: number, limitToToday = true): number {
  const first = new Date(yyyy, mm1to12 - 1, 1);
  const last  = new Date(yyyy, mm1to12, 0);
  const today = new Date();
  const end = (limitToToday && today.getFullYear() === yyyy && (today.getMonth() + 1) === mm1to12)
    ? new Date(yyyy, mm1to12 - 1, today.getDate())
    : last;

  let count = 0;
  for (let d = new Date(first); d <= end; d.setDate(d.getDate() + 1)) {
    const dow = d.getDay(); // 0=dom,6=sáb
    if (dow !== 0 && dow !== 6) count++;
  }
  return count;
}

const totalMesMin     = computed(() => registros.value.reduce((acc, r) => acc + r._total_min, 0));
const totalMesHHMM    = computed(() => minutesToHHMM(totalMesMin.value));
const totalMesHHMMSS  = computed(() => minutesToHHMMSS(totalMesMin.value));

const diasUteisConsiderados = computed(() => {
  if (!mesSelecionado.value) return 0;
  const [yStr, mStr] = mesSelecionado.value.split('-');
  const y = Number(yStr), m = Number(mStr);
  if (!y || !m) return 0;
  return countBusinessDaysOfMonth(y, m, true);
});

//const esperadoMesMin    = computed(() => diasUteisConsiderados.value * JORNADA_ALVO_MIN);
//const esperadoMesHHMM   = computed(() => minutesToHHMM(esperadoMesMin.value));
//const saldoMesMin       = computed(() => totalMesMin.value - esperadoMesMin.value);
//const saldoMesHHMM      = computed(() => minutesToHHMM(Math.abs(saldoMesMin.value)));
//const saldoPrefix       = computed(() => (saldoMesMin.value >= 0 ? '+' : '-'));
//const saldoColor        = computed(() => (saldoMesMin.value > 0 ? 'positive' : (saldoMesMin.value < 0 ? 'negative' : 'grey')));

const limiteContagemLabel = computed(() => {
  if (!mesSelecionado.value) return '';
  const [yStr, mStr] = mesSelecionado.value.split('-');
  const y = Number(yStr), m = Number(mStr);
  const today = new Date();
  const isCurrent = today.getFullYear() === y && (today.getMonth() + 1) === m;
  return isCurrent ? today.toLocaleDateString('pt-BR') : new Date(y, m, 0).toLocaleDateString('pt-BR');
});

/* ===== Init ===== */
onMounted(() => {
  const hoje = new Date();
  const yyyy = hoje.getFullYear();
  const mm = String(hoje.getMonth() + 1).padStart(2, '0');
  mesSelecionado.value = `${yyyy}-${mm}`; // dispara watch -> buscarPontos()
});
</script>
