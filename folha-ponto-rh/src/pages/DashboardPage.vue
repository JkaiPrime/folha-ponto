<template>
  <q-page class="dashboard-page flex flex-center">
    <q-card class="dashboard-card q-pa-md full-width" style="max-width: 1200px">
      <q-card-section>
        <div class="text-h6 text-primary text-center q-mb-md">Registros de Ponto</div>

        <q-table
          flat bordered
          :rows="registros"
          :columns="columns"
          row-key="id"
          :loading="loading"
          class="q-mb-md"
        >
          <template v-slot:body-cell-actions="props">
            <q-td align="right">
              <q-btn dense flat icon="edit" @click="edit(props.row as RegistroPonto)" />
              <q-btn dense flat icon="delete" color="negative" @click="remove((props.row as RegistroPonto).id)" />
            </q-td>
          </template>
        </q-table>
      </q-card-section>

      <q-dialog v-model="showModal">
        <q-card>
          <q-card-section>
            <div class="text-h6">Editar Registro</div>
            <q-input v-model="form.entrada" label="Entrada" type="datetime-local" class="q-mb-sm" />
            <q-input v-model="form.saida_almoco" label="Saída Almoço" type="datetime-local" class="q-mb-sm" />
            <q-input v-model="form.volta_almoco" label="Volta Almoço" type="datetime-local" class="q-mb-sm" />
            <q-input v-model="form.saida" label="Saída" type="datetime-local" class="q-mb-sm" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn label="Cancelar" flat v-close-popup />
            <q-btn label="Salvar" color="primary" @click="update" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useAuthStore } from 'src/stores/auth';
import { useRouter } from 'vue-router';
import { Notify } from 'quasar';

interface RegistroPonto {
  id: number;
  colaborador_id: string;
  data: string;
  entrada?: string;
  saida_almoco?: string;
  volta_almoco?: string;
  saida?: string;
}

const auth = useAuthStore();
const router = useRouter();
const registros = ref<RegistroPonto[]>([]);
const loading = ref(true);
const showModal = ref(false);
const selectedId = ref<number | null>(null);
const form = ref({
  entrada: '',
  saida_almoco: '',
  volta_almoco: '',
  saida: ''
});

function toInputFormat(dt: string | undefined) {
  if (!dt) return '';
  return dt.slice(0, 16);
}

const columns = [
  { name: 'id', label: 'ID', field: 'id' },
  { name: 'colaborador_id', label: 'Código', field: 'colaborador_id' },
  { name: 'data', label: 'Data', field: 'data' },
  { name: 'entrada', label: 'Entrada', field: 'entrada' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: 'saida_almoco' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: 'volta_almoco' },
  { name: 'saida', label: 'Saída', field: 'saida' },
  { name: 'actions', label: '', field: 'actions' }
];

async function fetchPontos() {
  loading.value = true;
  if (!auth.token) {
    Notify.create({
      type: 'warning',
      message: 'Sessão expirada. Por favor, faça login novamente.',
      position: 'top'
    });
    void router.push('/');
    return;
  }

  try {
    const { data } = await api.get('http://localhost:8000/pontos', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    registros.value = data;
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao buscar pontos' });
  } finally {
    loading.value = false;
  }
}

function edit(row: RegistroPonto) {
  selectedId.value = row.id;
  form.value = {
    entrada: toInputFormat(row.entrada),
    saida_almoco: toInputFormat(row.saida_almoco),
    volta_almoco: toInputFormat(row.volta_almoco),
    saida: toInputFormat(row.saida)
  };
  showModal.value = true;
}

async function update() {
  try {
    await api.put(`http://localhost:8000/pontos/${selectedId.value}`, form.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    Notify.create({ type: 'positive', message: 'Atualizado com sucesso' });
    showModal.value = false;
    await fetchPontos();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar' });
  }
}

async function remove(id: number) {
  if (!confirm('Deseja excluir este ponto?')) return;
  try {
    await api.delete(`http://localhost:8000/pontos/${id}`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    Notify.create({ type: 'positive', message: 'Excluído com sucesso' });
    await fetchPontos();
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao excluir' });
  }
}

onMounted(fetchPontos);
</script>

<style scoped>
.dashboard-page {
  background: linear-gradient(to right, #e3f2fd, #bbdefb);
  min-height: 100vh;
  padding: 24px;
}

.dashboard-card {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  background: white;
}
</style>