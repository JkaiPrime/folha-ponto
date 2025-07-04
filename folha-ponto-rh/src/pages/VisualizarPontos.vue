<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Visualizar pontos por colaborador</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-select
          v-model="colaboradorSelecionado"
          :options="colaboradores"
          option-value="code"
          option-label="nome"
          emit-value
          map-options
          label="Selecionar colaborador"
          filled
          dense
          class="q-mb-md"
        />
        <div class="row q-gutter-sm">
          <q-btn
            label="Buscar pontos"
            color="primary"
            @click="buscarPontos"
            :disable="!colaboradorSelecionado"
          />
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
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import { api } from 'boot/axios';
import { useAuthStore } from 'src/stores/auth';
import * as XLSX from 'xlsx';
import type { QTableColumn } from 'quasar';

interface RegistroPonto {
  id: number;
  data?: string;
  entrada?: string;
  saida_almoco?: string;
  volta_almoco?: string;
  saida?: string;
}

interface Colaborador {
  code: string;
  nome: string;
}

const auth = useAuthStore();

const colaboradores = ref<Colaborador[]>([]);
const colaboradorSelecionado = ref<string | null>(null);
const registros = ref<RegistroPonto[]>([]);

const columns: QTableColumn<RegistroPonto>[] = [
  { name: 'data', label: 'Data', field: row => formatDate(row.data), align: 'center' },
  { name: 'entrada', label: 'Entrada', field: row => formatTime(row.entrada), align: 'center' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: row => formatTime(row.saida_almoco), align: 'center' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: row => formatTime(row.volta_almoco), align: 'center' },
  { name: 'saida', label: 'Saída', field: row => formatTime(row.saida), align: 'center' }
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

async function carregarColaboradores() {
  try {
    const res = await api.get('/colaboradores', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    colaboradores.value = res.data;
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Erro ao carregar colaboradores'
    });
  }
}

async function buscarPontos() {
  if (!colaboradorSelecionado.value) return;

  try {
    const res = await api.get(`/pontos/${colaboradorSelecionado.value}`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    registros.value = res.data;
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Colaborador não possui nenhum registro'
    });
    registros.value = [];
    colaboradorSelecionado.value = null
  }
}

function exportarExcel() {
  const dados = registros.value.map(reg => ({
    Data: formatDate(reg.data),
    Entrada: formatTime(reg.entrada),
    'Saída Almoço': formatTime(reg.saida_almoco),
    'Volta Almoço': formatTime(reg.volta_almoco),
    Saída: formatTime(reg.saida),
  }));

  const ws = XLSX.utils.json_to_sheet(dados);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Pontos');

  const colaborador = colaboradores.value.find(c => c.code === colaboradorSelecionado.value);
  const nomeArquivo = colaborador ? colaborador.nome.replace(/\s+/g, '_') : colaboradorSelecionado.value;
  XLSX.writeFile(wb, `pontos_${nomeArquivo}.xlsx`);
}

onMounted(carregarColaboradores);
</script>
