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
        :rows-per-page-options="[0]"
      >
        <template v-slot:body-cell-anexo="props">
          <q-td :props="props">
            <span v-html="props.value" />
          </q-td>
        </template>
      </q-table>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import dayjs from 'dayjs'
import type { QTableColumn } from 'quasar'

interface Registro {
  id: number
  data: string
  entrada: string | null
  saida_almoco: string | null
  volta_almoco: string | null
  saida: string | null
  justificativa?: string
  arquivo?: string
  colaborador: {
    nome: string
  }
}

const registros = ref<Registro[]>([])

onMounted(async () => {
  try {
    const res = await api.get('/pontos/hoje', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    registros.value = res.data
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar registros de hoje' })
  }
})

function formatTime(valor: string | null | undefined): string {
  return valor ? dayjs(valor).format('HH:mm') : '-'
}

const columns: QTableColumn<Registro>[] = [
  {
    name: 'nome',
    label: 'Nome',
    field: row => row.colaborador?.nome || '-',
    align: 'center' as const
  },
  {
    name: 'entrada',
    label: 'Entrada',
    field: row => formatTime(row.entrada),
    align: 'center' as const
  },
  {
    name: 'saida_almoco',
    label: 'Saída Almoço',
    field: row => formatTime(row.saida_almoco),
    align: 'center' as const
  },
  {
    name: 'volta_almoco',
    label: 'Volta Almoço',
    field: row => formatTime(row.volta_almoco),
    align: 'center' as const
  },
  {
    name: 'saida',
    label: 'Saída',
    field: row => formatTime(row.saida),
    align: 'center' as const
  },
  {
    name: 'anexo',
    label: 'Anexo',
    align: 'center',
    field: () => '',
    format: (_val: unknown, row: Registro) => {
      return row.arquivo
        ? `<a href="http://localhost:8000/justificativas/arquivo/${row.arquivo}" target="_blank" download>📎</a>`
        : ''
    }
  }
]
</script>

<style scoped>
.bg-light-blue-1 {
  background: linear-gradient(to bottom right, #e3f2fd, #bbdefb);
  min-height: 100vh;
}
</style>
