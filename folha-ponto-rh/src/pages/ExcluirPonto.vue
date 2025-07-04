<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Excluir ponto de colaborador</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="q-gutter-md">
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
          <template v-slot:body-cell-actions="props">
            <q-td align="center">
              <q-btn
                icon="delete"
                color="negative"
                dense
                flat
                @click="removerPonto(props.row.id)"
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
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { useAuthStore } from 'src/stores/auth';
import type { QTableColumn } from 'quasar';

interface Registro {
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
const mesSelecionado = ref<string | null>(null);
const registros = ref<Registro[]>([]);

function formatDate(iso: string | undefined): string {
  if (!iso) return '-';
  const date = new Date(iso);
  return date.toLocaleDateString('pt-BR');
}

function formatTime(iso: string | undefined): string {
  if (!iso) return '-';
  const date = new Date(iso);
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
}

const columns: QTableColumn<Registro>[] = [
  { name: 'data', label: 'Data', field: row => formatDate(row.data), align: 'center' },
  { name: 'entrada', label: 'Entrada', field: row => formatTime(row.entrada), align: 'center' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: row => formatTime(row.saida_almoco), align: 'center' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: row => formatTime(row.volta_almoco), align: 'center' },
  { name: 'saida', label: 'Saída', field: row => formatTime(row.saida), align: 'center' },
  { name: 'actions', label: 'Ações', field: () => '', align: 'center' }
];

async function carregarColaboradores() {
  try {
    const res = await api.get('/colaboradores', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
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
      },
      headers: {
        Authorization: `Bearer ${auth.token}`
      }
    });
    registros.value = res.data;
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao buscar pontos do colaborador' });
    registros.value = [];
  }
}

async function removerPonto(id: number) {
  if (!confirm('Tem certeza que deseja excluir este ponto?')) return;

  try {
    await api.delete(`/pontos/${id}`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    Notify.create({ type: 'positive', message: 'Ponto excluído com sucesso' });
    await buscarPontos();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir ponto' });
  }
}

onMounted(carregarColaboradores);
</script>
