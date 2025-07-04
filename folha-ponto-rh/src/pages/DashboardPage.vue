<template>
  <q-page class="bg-light-blue-1 flex flex-center">
    <q-card class="q-pa-lg" style="width: 100%; max-width: 1000px; border-radius: 16px;">
      <q-card-section class="text-center">
        <div class="text-h6 text-primary">Registros de Ponto - Hoje</div>
      </q-card-section>

      <q-separator />

      <q-table
        :rows="registros"
        :columns="columns"
        row-key="id"
        flat
        bordered
        class="q-mt-md"
      />
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useAuthStore } from 'src/stores/auth';
import { Notify } from 'quasar';
import type { QTableColumn } from 'quasar';

interface Registro {
  id: number;
  entrada?: string;
  saida_almoco?: string;
  volta_almoco?: string;
  saida?: string;
  colaborador?: {
    nome: string;
  };
}

const auth = useAuthStore();
const registros = ref<Registro[]>([]);

const columns: QTableColumn<Registro>[] = [
  { name: 'nome', label: 'Nome', field: row => row.colaborador?.nome || '-', align: 'center' },
  { name: 'entrada', label: 'Entrada', field: row => formatTime(row.entrada), align: 'center' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: row => formatTime(row.saida_almoco), align: 'center' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: row => formatTime(row.volta_almoco), align: 'center' },
  { name: 'saida', label: 'Saída', field: row => formatTime(row.saida), align: 'center' }
];

function formatTime(iso: string | undefined): string {
  if (!iso) return '-';
  const date = new Date(iso);
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'America/Sao_Paulo'
  });
}

async function carregarPontos() {
  try {
    const res = await api.get('/pontos/hoje', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    if (res.data.length === 0) {
      Notify.create({
        type: 'warning',
        message: 'Nenhum ponto foi registrado hoje.'
      });
    }

    registros.value = res.data;
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Erro ao carregar pontos do dia'
    });
  }
}

onMounted(carregarPontos);
</script>

<style scoped>
.bg-light-blue-1 {
  background: linear-gradient(to bottom right, #e3f2fd, #bbdefb);
  min-height: 100vh;
}
</style>
