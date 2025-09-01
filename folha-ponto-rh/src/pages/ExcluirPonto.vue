<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 1000px;">
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Excluir Registros de Ponto</div>
        <!-- (removido) botão de exportar -->
      </q-card-section>

      <q-separator />

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

          <div class="col-12">
            <q-btn
              label="Buscar pontos"
              color="primary"
              icon="search"
              :disable="!colaboradorSelecionado || !mesSelecionado"
              :loading="loadingPontos"
              @click="buscarPontos"
            />
          </div>
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section v-if="pontos.length">
        <q-table
          :rows="pontos"
          :columns="columns"
          row-key="id"
          dense
          flat
          bordered
          :loading="loadingPontos"
          :rows-per-page-options="[0, 20, 50, 0]"
        >
          <template #body-cell-data="props">
            <q-td :props="props" class="text-center">{{ props.row._data_fmt }}</q-td>
          </template>
          <template #body-cell-entrada="props">
            <q-td :props="props" class="text-center">{{ formatarHora(props.row.entrada) }}</q-td>
          </template>
          <template #body-cell-saida_almoco="props">
            <q-td :props="props" class="text-center">{{ formatarHora(props.row.saida_almoco) }}</q-td>
          </template>
          <template #body-cell-volta_almoco="props">
            <q-td :props="props" class="text-center">{{ formatarHora(props.row.volta_almoco) }}</q-td>
          </template>
          <template #body-cell-saida="props">
            <q-td :props="props" class="text-center">{{ formatarHora(props.row.saida) }}</q-td>
          </template>
          <template #body-cell-alterado_por="props">
            <q-td :props="props" class="text-center">{{ props.row.alterado_por?.nome || '-' }}</q-td>
          </template>
          <template #body-cell-acoes="props">
            <q-td :props="props" class="text-center">
              <q-btn
                dense
                flat
                icon="delete"
                color="negative"
                @click="confirmarExclusao(props.row.id)"
              />
            </q-td>
          </template>

          <template #bottom>
            <div class="full-width row justify-end q-pa-sm">
              <q-chip color="grey-3" text-color="dark">
                Registros: {{ pontos.length }}
              </q-chip>
            </div>
          </template>
        </q-table>
      </q-card-section>

      <q-card-section v-else class="text-center text-grey q-mt-lg">
        Nenhum registro de ponto encontrado para o período selecionado.
      </q-card-section>
    </q-card>

    <!-- Diálogo de Confirmação -->
    <q-dialog v-model="mostrarDialogo">
      <q-card>
        <q-card-section class="text-h6">
          Confirmar Exclusão
        </q-card-section>
        <q-card-section>
          Tem certeza de que deseja excluir este registro de ponto? Esta ação é irreversível.
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn flat label="Excluir" color="negative" @click="removerPonto" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { QTableColumn } from 'quasar';

/* ========================= Tipos ========================= */
type IsoStr = string | null | undefined;

interface UsuarioMin {
  id: number;
  nome: string;
}
interface RegistroApi {
  id: number;
  data: string;
  entrada: IsoStr;
  saida_almoco: IsoStr;
  volta_almoco: IsoStr;
  saida: IsoStr;
  alterado_por?: UsuarioMin | null;
}
interface RegistroFront extends RegistroApi {
  _data_fmt: string; // dd/MM/yyyy
}
interface Colaborador {
  id: number;
  nome: string;
}
interface ColaboradorApi {
  id?: number | string;
  code?: number | string;
  nome?: string;
}

/* ========================= State ========================= */
const colaboradores = ref<Colaborador[]>([]);
const colaboradorSelecionado = ref<number | null>(null);
const mesSelecionado = ref<string | null>(null);
const pontos = ref<RegistroFront[]>([]);

const loadingColaboradores = ref(false);
const loadingPontos = ref(false);

const mostrarDialogo = ref(false);
const pontoSelecionado = ref<number | null>(null);

/* ========================= Colunas ========================= */
const columns: QTableColumn<RegistroFront>[] = [
  { name: 'data',          label: 'Data',          field: (r) => r._data_fmt, align: 'center' },
  { name: 'entrada',       label: 'Entrada',       field: (r) => r.entrada, align: 'center' },
  { name: 'saida_almoco',  label: 'Saída Almoço',  field: (r) => r.saida_almoco, align: 'center' },
  { name: 'volta_almoco',  label: 'Volta Almoço',  field: (r) => r.volta_almoco, align: 'center' },
  { name: 'saida',         label: 'Saída',         field: (r) => r.saida, align: 'center' },
  { name: 'alterado_por',  label: 'Alterado por',  field: (r) => r.alterado_por?.nome || '-', align: 'center' },
  { name: 'acoes',         label: 'Ações',         field: () => '', align: 'center' }
];

/* ========================= Helpers de data ========================= */
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function brDateFromIsoDateOnly(s?: string | null): string {
  if (!s) return '-';
  if (ISO_DATE_RE.test(s)) {
    const [y, m, d] = s.split('-') as [string, string, string];
    return `${d}/${m}/${y}`;
  }
  const d = new Date(s);
  return isNaN(d.getTime()) ? '-' : d.toLocaleDateString('pt-BR');
}

function dateSortKey(s?: string | null): number {
  if (!s) return 0;
  if (ISO_DATE_RE.test(s)) {
    const [yStr, mStr, dStr] = s.split('-');
    const y = parseInt(yStr as string, 10);
    const m = parseInt(mStr as string, 10);
    const d = parseInt(dStr as string, 10);
    return y * 10000 + m * 100 + d;
  }
  const d = new Date(s);
  return isNaN(d.getTime()) ? 0 : d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
}

function formatarHora(iso: IsoStr): string {
  if (!iso) return '-';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '-';
  return d.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'America/Sao_Paulo'
  });
}

function normalize(r: RegistroApi): RegistroFront {
  return { ...r, _data_fmt: brDateFromIsoDateOnly(r.data) };
}

/* ========================= API ========================= */
function isColaboradorApiArray(x: unknown): x is ColaboradorApi[] {
  return Array.isArray(x) && x.every(obj => obj && typeof obj === 'object');
}

async function carregarColaboradores(): Promise<void> {
  loadingColaboradores.value = true;
  try {
    const res = await api.get('/colaboradores');
    const raw = res.data as unknown;
    if (isColaboradorApiArray(raw)) {
      colaboradores.value = raw
        .map((c) => ({ id: Number(c.id ?? c.code ?? 0), nome: String(c.nome ?? '') }))
        .filter((c) => Number.isFinite(c.id) && c.nome.length > 0);
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

async function buscarPontos(): Promise<void> {
  if (!colaboradorSelecionado.value || !mesSelecionado.value) return;

  const [anoStr, mesStr] = mesSelecionado.value.split('-');
  const ano = Number(anoStr);
  const mes = Number(mesStr);
  if (!ano || !mes) return;

  const inicio = `${ano}-${String(mes).padStart(2, '0')}-01`;
  const lastDayNum = new Date(ano, mes, 0).getDate();
  const fim = `${ano}-${String(mes).padStart(2, '0')}-${String(lastDayNum).padStart(2, '0')}`;

  loadingPontos.value = true;
  try {
    const res = await api.get('/pontos/por-data', {
      params: { colaborador_id: Number(colaboradorSelecionado.value), inicio, fim }
    });

    const raw = res.data as unknown;
    if (Array.isArray(raw)) {
      pontos.value = (raw as RegistroApi[])
        .map(normalize)
        .sort((a, b) => dateSortKey(a.data) - dateSortKey(b.data));
    } else {
      pontos.value = [];
    }
  } catch (error) {
    console.error('Erro ao buscar pontos:', error);
    pontos.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao buscar pontos do colaborador' });
  } finally {
    loadingPontos.value = false;
  }
}

function confirmarExclusao(id: number): void {
  pontoSelecionado.value = id;
  mostrarDialogo.value = true;
}

async function removerPonto(): Promise<void> {
  if (!pontoSelecionado.value) return;
  try {
    await api.delete(`/pontos/${pontoSelecionado.value}`);
    Notify.create({ type: 'positive', message: 'Registro excluído com sucesso' });
    mostrarDialogo.value = false;
    await buscarPontos();
  } catch (error) {
    console.error('Erro ao excluir ponto:', error);
    Notify.create({ type: 'negative', message: 'Erro ao excluir ponto' });
  }
}

/* ========================= Lifecycle ========================= */
onMounted(async () => {
  await carregarColaboradores();
  const hoje = new Date();
  const yyyy = hoje.getFullYear();
  const mm = String(hoje.getMonth() + 1).padStart(2, '0');
  mesSelecionado.value = `${yyyy}-${mm}`;
});
</script>
