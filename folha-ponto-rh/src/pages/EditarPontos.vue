<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Editar pontos por colaborador</div>
      </q-card-section>

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
        </div>
      </q-card-section>

      <q-card-section>
        <q-table
          :rows="registros"
          :columns="columns"
          row-key="id"
          dense
          flat
          bordered
        >
          <template v-slot:body-cell-entrada="props">
            <q-td>
              <template v-if="props.row.id">
                <q-input
                  v-model="props.row.entrada"
                  type="datetime-local"
                  dense
                  outlined
                />
              </template>
              <template v-else>
                <div class="text-italic text-primary">
                  Justificativa: {{ props.row.justificativa || 'Sem motivo informado' }}
                </div>
              </template>
            </q-td>
          </template>

          <template v-slot:body-cell-saida_almoco="props">
            <q-td>
              <template v-if="props.row.id">
                <q-input
                  v-model="props.row.saida_almoco"
                  type="datetime-local"
                  dense
                  outlined
                />
              </template>
              <template v-else>
                <div class="text-grey-6">—</div>
              </template>
            </q-td>
          </template>

          <template v-slot:body-cell-volta_almoco="props">
            <q-td>
              <template v-if="props.row.id">
                <q-input
                  v-model="props.row.volta_almoco"
                  type="datetime-local"
                  dense
                  outlined
                />
              </template>
              <template v-else>
                <div class="text-grey-6">—</div>
              </template>
            </q-td>
          </template>

          <template v-slot:body-cell-saida="props">
            <q-td>
              <template v-if="props.row.id">
                <q-input
                  v-model="props.row.saida"
                  type="datetime-local"
                  dense
                  outlined
                />
              </template>
              <template v-else>
                <div class="text-grey-6">—</div>
              </template>
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td align="center">
              <q-btn
                label="Salvar"
                color="positive"
                size="sm"
                :disable="!props.row.id"
                @click="salvarAlteracao(props.row)"
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
import { useAuthStore } from 'src/stores/auth';
import type { QTableColumn } from 'quasar';

interface Registro {
  id: number | null;
  entrada: string | null;
  saida_almoco: string | null;
  volta_almoco: string | null;
  saida: string | null;
  justificativa?: string | null;
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

const columns: QTableColumn[] = [
  { name: 'entrada', label: 'Entrada', field: 'entrada', align: 'center' },
  { name: 'saida_almoco', label: 'Saída Almoço', field: 'saida_almoco', align: 'center' },
  { name: 'volta_almoco', label: 'Volta Almoço', field: 'volta_almoco', align: 'center' },
  { name: 'saida', label: 'Saída', field: 'saida', align: 'center' },
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
  console.log(colaboradorSelecionado.value)
  const [ano, mes] = mesSelecionado.value.split('-');
  const inicio = `${ano}-${mes}-01`;
  const fim = new Date(Number(ano), Number(mes), 0).toISOString().split('T')[0];

  try {
    const res = await api.get('/pontos/por-data', {
      params: {
        colaborador_id: colaboradorSelecionado.value, // aqui já é o ID
        inicio,
        fim
      },
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    registros.value = res.data.map((r: Registro) => ({
      ...r,
      entrada: r.entrada?.slice(0, 16) ?? null,
      saida_almoco: r.saida_almoco?.slice(0, 16) ?? null,
      volta_almoco: r.volta_almoco?.slice(0, 16) ?? null,
      saida: r.saida?.slice(0, 16) ?? null
    }));
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar pontos do colaborador' });
    registros.value = [];
  }
}


async function salvarAlteracao(registro: Registro) {
  if (!registro.id) return;

  try {
    await api.put(`/pontos/${registro.id}`, {
      entrada: registro.entrada,
      saida_almoco: registro.saida_almoco,
      volta_almoco: registro.volta_almoco,
      saida: registro.saida
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    Notify.create({ type: 'positive', message: 'Registro atualizado com sucesso!' });
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao atualizar registro' });
  }
}

onMounted(carregarColaboradores);
</script>
