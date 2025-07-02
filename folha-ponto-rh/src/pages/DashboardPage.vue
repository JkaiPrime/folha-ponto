<template>
  <q-page class="bg-light-blue-1 flex flex-center">
    <q-card class="q-pa-lg" style="width: 100%; max-width: 1000px; border-radius: 16px;">
      <q-card-section class="text-center">
        <div class="text-h6 text-primary">Registros de Ponto</div>
      </q-card-section>

      <q-separator />

      <q-table
        :rows="registros"
        :columns="columns"
        row-key="id"
        flat
        bordered
        class="q-mt-md"
        :loading="loading"
      />
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import { useAuthStore } from 'src/stores/auth';
import { useRouter } from 'vue-router';
import { api } from 'boot/axios';
import type { QTableColumn } from 'quasar';


const auth = useAuthStore();
const router = useRouter();


const loading = ref(true);
interface RegistroPonto {
  id: number;
  colaborador_id: string;
  colaborador?: {
    nome?: string;
  };
  data?: string;
  entrada?: string;
  saida_almoco?: string;
  volta_almoco?: string;
  saida?: string;
}

const registros = ref<RegistroPonto[]>([]);
const columns: QTableColumn<RegistroPonto>[] = [
  { name: 'colaborador_id', label: 'Código', field: 'colaborador_id', align: 'left' },
  { name: 'colaborador_nome', label: 'Nome', field: (row) => row.colaborador?.nome || '—', align: 'left' },
  { name: 'data', label: 'Data', field: (row) => formatDate(row.data), align: 'center' },
  { name: 'entrada', label: 'Entrada', field: (row) => formatTime(row.entrada), align: 'center' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: (row) => formatTime(row.saida_almoco), align: 'center' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: (row) => formatTime(row.volta_almoco), align: 'center' },
  { name: 'saida', label: 'Saída', field: (row) => formatTime(row.saida), align: 'center' }
];

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR');
}

function formatTime(dateStr: string | undefined): string {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

async function fetchPontos() {
  if (!auth.token) {
    Notify.create({ type: 'warning', message: 'Sessão expirada.', position: 'top' });
    void router.push('/');
    return;
  }

  loading.value = true;
  try {
    const res = await api.get('/pontos', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    registros.value = res.data;
  } catch{
    Notify.create({ type: 'negative', message: 'Erro ao carregar os pontos.' });
  } finally {
    loading.value = false;
  }
}

onMounted(fetchPontos);
</script>

<style scoped>
.bg-light-blue-1 {
  background: linear-gradient(to bottom right, #e3f2fd, #bbdefb);
  min-height: 100vh;
}
</style>
