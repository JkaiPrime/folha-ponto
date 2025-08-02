<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Visualizar pontos por colaborador</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="q-gutter-md">
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
            @update:model-value="buscarPontos"
          />

          <q-input
            v-model="mesSelecionado"
            label="Selecionar mês"
            filled
            dense
          >
            <template #append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy>
                  <q-date
                    v-model="mesSelecionado"
                    mask="YYYY-MM"
                    minimal
                    default-view="Months"
                    emit-immediately
                    @update:model-value="buscarPontos"
                  />
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>

          <q-btn
            label="Exportar para Excel"
            color="secondary"
            @click="exportarExcel"
            :disable="registros.length === 0"
          />
        </div>
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
        >
          <template v-slot:body-cell-status="props">
            <q-td :props="props" class="text-center">
              <q-badge
                :color="getStatusColor(props.row.status)"
                :label="capitalize(props.row.status)"
                class="text-uppercase"
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
import * as XLSX from 'xlsx';
import type { QTableColumn } from 'quasar';

interface RegistroPonto {
  id: number;
  data?: string;
  entrada?: string;
  saida_almoco?: string;
  volta_almoco?: string;
  saida?: string;
  arquivo?: string | null;
  alterado_por?: { id: number; nome: string } | null;
  avaliador?: { id: number; nome: string } | null;
  status?: string;

}

interface Colaborador {
  code: string;
  nome: string;
}

const colaboradores = ref<Colaborador[]>([]);
const colaboradorSelecionado = ref<string | null>(null);
const mesSelecionado = ref<string | null>(null);
const registros = ref<RegistroPonto[]>([]);

const columns: QTableColumn<RegistroPonto>[] = [
  { name: 'data', label: 'Data', field: row => formatDate(row.data), align: 'center' },
  { name: 'entrada', label: 'Entrada', field: row => formatTime(row.entrada), align: 'center' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: row => formatTime(row.saida_almoco), align: 'center' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: row => formatTime(row.volta_almoco), align: 'center' },
  { name: 'saida', label: 'Saída', field: row => formatTime(row.saida), align: 'center' },
  /*{
    name: 'anexo',
    label: 'Anexo',
    align: 'center',
    field: () => '',
    format: (_val, row) => {
      return row.arquivo
        ? `<a href="http://localhost:8000/justificativas/arquivo/${row.arquivo}" target="_blank" download>📎</a>`
        : '';
    },
  },{
    name: 'status',
    label: 'Status',
    field: row => row.status || '-',
    align: 'center'
  },*/
  {
    name: 'alterado_por',
    label: 'Alterado por',
    field: row => row.alterado_por?.nome || '-',
    align: 'center'
  },/*
  {
    name: 'avaliador',
    label: 'Avaliador',
    field: row => row.avaliador?.nome || '-',
    align: 'center'
  }*/
];


function formatDate(iso: unknown): string {
  if (typeof iso !== 'string') return '-';
  const [ano, mes, dia] = (iso.split('T')[0]?.split('-') ?? []);
  return ano && mes && dia ? `${dia}/${mes}/${ano}` : '-';
}

function formatTime(iso: string | null | undefined): string {
  if (!iso) return '-';
  const date = new Date(iso);
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'America/Sao_Paulo'
  });
}


function getStatusColor(status: string | undefined) {
  switch (status) {
    case 'aprovada': return 'positive'
    case 'rejeitada': return 'negative'
    case 'pendente': return 'warning'
    default: return 'grey'
  }
}

function capitalize(str: string | undefined) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : '-'
}


async function carregarColaboradores() {
  try {
    const res = await api.get('/colaboradores');
    colaboradores.value = res.data;
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaboradores' });
  }
}

async function buscarPontos() {
  if (!colaboradorSelecionado.value || !mesSelecionado.value) return;

  const [ano, mes] = mesSelecionado.value.split('-');
  const inicio = `${ano}-${mes}-01`;
  const fim = new Date(Number(ano), Number(mes), 0).toISOString().split('T')[0];

  try {
    const res = await api.get('/pontos/por-data', {
      params: {
        colaborador_id: colaboradorSelecionado.value,
        inicio,
        fim
      }
    });
    registros.value = res.data;
  } catch {
    registros.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao buscar pontos do colaborador' });
  }
}

function exportarExcel() {
  type Registro = {
    id: number;
    data?: string;
    entrada?: string;
    saida_almoco?: string;
    volta_almoco?: string;
    saida?: string;
  };

  // Montar dados por dia
  const dados = registros.value.map((reg: Registro) => ([
    reg.data ? formatDate(reg.data) : '',
    reg.data ? new Date(reg.data).toLocaleDateString('pt-BR', { weekday: 'short' }).toUpperCase() : '',
    reg.entrada ? formatTime(reg.entrada) : '',
    reg.saida_almoco ? formatTime(reg.saida_almoco) : '',
    reg.volta_almoco ? formatTime(reg.volta_almoco) : '',
    reg.saida ? formatTime(reg.saida) : '',
    calcularTotalDia(reg)
  ]));

  // Somatório total mensal (em minutos)
  const totalMinutos = registros.value.reduce((total: number, reg: Registro) => {
    return total + calcularMinutosDia(reg);
  }, 0);

  const horasMes = Math.floor(totalMinutos / 60);
  const minutosMes = totalMinutos % 60;
  const totalMes = `${String(horasMes).padStart(2, '0')}:${String(minutosMes).padStart(2, '0')}:00`;

  // Cabeçalho + Dados + Total Mensal
  const wsData = [
    ['DATA', 'DIA', 'Entrada', 'Almoço saída', 'Almoço retorno', 'Saída', 'Total DIA'],
    ...dados,
    ['', '', '', '', '', 'TOTAL MÊS', totalMes]
  ];

  // Criar a planilha
  const ws = XLSX.utils.aoa_to_sheet(wsData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Folha - Ponto');

  // Nome do colaborador no arquivo
  const colaborador = colaboradores.value.find(c => c.code === colaboradorSelecionado.value);
  const nomeArquivo = colaborador ? colaborador.nome.replace(/\s+/g, '_') : colaboradorSelecionado.value;

  XLSX.writeFile(wb, `FOLHA-PONTO_${nomeArquivo}.xlsx`);
}

function calcularTotalDia(reg: {entrada?: string, saida?: string, saida_almoco?: string, volta_almoco?: string}): string {
  const totalMin = calcularMinutosDia(reg);
  const horas = Math.floor(totalMin / 60);
  const minutos = totalMin % 60;
  return `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}:00`;
}

function calcularMinutosDia(reg: {entrada?: string, saida?: string, saida_almoco?: string, volta_almoco?: string}): number {
  if (!reg.entrada || !reg.saida) return 0;

  const inicio = new Date(`1970-01-01T${reg.entrada}`);
  const fim = new Date(`1970-01-01T${reg.saida}`);
  let totalMs = fim.getTime() - inicio.getTime();

  if (reg.saida_almoco && reg.volta_almoco) {
    const almoco1 = new Date(`1970-01-01T${reg.saida_almoco}`);
    const almoco2 = new Date(`1970-01-01T${reg.volta_almoco}`);
    totalMs -= (almoco2.getTime() - almoco1.getTime());
  }

  return Math.floor(totalMs / 60000); // Retorna minutos totais
}





onMounted(carregarColaboradores);
</script>
