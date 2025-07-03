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

        <q-btn
          label="Buscar pontos"
          color="primary"
          @click="buscarPontos"
          :disable="!colaboradorSelecionado"
        />
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

function formatTime(iso: string | null | undefined) {
  if (!iso) return '-';
  const date = new Date(iso); // isso interpreta o horário como UTC (e pode ajustar)
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
      message: 'Erro ao buscar pontos do colaborador'
    });
  }
}

onMounted(carregarColaboradores);
</script>
