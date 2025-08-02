<template>
  <q-page class="q-pa-md">
    <q-card flat bordered>
      <q-card-section>
        <div class="text-h6">Gerenciar Justificativas Pendentes</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-table
          :rows="justificativas"
          :columns="columns"
          row-key="id"
          dense
          flat
          bordered
          :loading="carregando"
        >
          <template v-slot:body-cell-anexo="props">
            <q-td :props="props" class="text-center">
              <a
                v-if="props.row.arquivo"
                :href="`https://folha-ponto.onrender.com/justificativas/arquivo/${props.row.arquivo}`"
                target="_blank"
                download
              >📎</a>
            </q-td>
          </template>

          <template v-slot:body-cell-status="props">
            <q-td :props="props" class="text-center">
              <q-badge
                :color="props.row.status === 'pendente' ? 'warning' : 'grey'"
                :label="props.row.status"
                class="text-uppercase"
              />
            </q-td>
          </template>

          <template v-slot:body-cell-acoes="props">
            <q-td :props="props" class="text-center">
              <q-btn
                color="positive"
                icon="check"
                size="sm"
                dense
                @click="avaliar(props.row.id, 'aprovado')"
              />
              <q-btn
                color="negative"
                icon="close"
                size="sm"
                dense
                class="q-ml-sm"
                @click="avaliar(props.row.id, 'negado')"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import type { QTableColumn } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

interface Justificativa {
  id: number
  colaborador_id: string
  justificativa: string
  arquivo?: string
  data_envio: string
  data_referente: string
  status: 'pendente' | 'aprovado' | 'negado'
  colaborador?: {
    nome: string
  }
}

const justificativas = ref<Justificativa[]>([])
const carregando = ref(false)
const auth = useAuthStore()


const columns: QTableColumn<Justificativa>[] = [
  { name: 'colaborador', label: 'Colaborador', field: row => row.colaborador?.nome || '-', align: 'center' as const },
  { name: 'data_referente', label: 'Data', field: 'data_referente', align: 'center' as const },
  { name: 'justificativa', label: 'Justificativa', field: 'justificativa', align: 'left' as const },
  { name: 'anexo', label: 'Anexo', field: 'arquivo', align: 'center' as const },
  { name: 'status', label: 'Status', field: 'status', align: 'center' as const },
  { name: 'acoes', label: 'Ações', field: 'id', align: 'center' as const }
]


async function carregarPendentes() {
  carregando.value = true
  try {
    const res = await api.get('/justificativas/pendentes')
    justificativas.value = res.data
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar justificativas pendentes' })
  } finally {
    carregando.value = false
  }
}



async function avaliar(id: number, status: 'aprovado' | 'negado') {
  try {
    const statusConvertido = status === 'aprovado' ? 'aprovada' : 'rejeitada'
    await api.patch(`/justificativas/${id}/avaliar`, { status: statusConvertido }, {
      headers: {
        Authorization: `Bearer ${auth.token}`
      }
    })
    Notify.create({ type: 'positive', message: `Justificativa ${status}` })
    await carregarPendentes()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao avaliar justificativa' })
  }
}


onMounted(carregarPendentes)
</script>
