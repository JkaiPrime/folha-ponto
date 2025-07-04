<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Colaboradores Cadastrados</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-table
          :rows="colaboradores"
          :columns="columns"
          row-key="code"
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
                @click="removerColaborador(props.row.code)"
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

interface Colaborador {
  code: string;
  nome: string;
}

const colaboradores = ref<Colaborador[]>([]);
const auth = useAuthStore();

const columns: QTableColumn<Colaborador>[] = [
  { name: 'code', label: 'Código', field: 'code', align: 'center' },
  { name: 'nome', label: 'Nome', field: 'nome', align: 'center' },
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

async function removerColaborador(code: string) {
  if (!confirm('Tem certeza que deseja excluir este colaborador?')) return;

  try {
    await api.delete(`/colaboradores/${code}`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    Notify.create({ type: 'positive', message: 'Colaborador excluído com sucesso' });
    await carregarColaboradores();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir colaborador' });
  }
}

onMounted(carregarColaboradores);
</script>
