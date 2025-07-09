<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 800px;">
      <q-card-section>
        <div class="text-h6">Visualizar Registros de Ponto</div>
      </q-card-section>

      <q-card-section class="q-gutter-md">
        <q-option-group
          v-model="modo"
          :options="[
            { label: 'Selecionar Dia', value: 'dia' },
            { label: 'Selecionar Mês', value: 'mes' }
          ]"
          color="primary"
          inline
        />

        <q-input
          v-if="modo === 'dia'"
          filled
          v-model="dataSelecionada"
          label="Data"
          type="date"
        />

        <q-input
          v-if="modo === 'mes'"
          filled
          v-model="mesSelecionado"
          label="Mês"
          type="text"
          mask="####-##"
          hint="Formato: YYYY-MM"
        />

        <q-btn label="Buscar pontos" color="primary" @click="buscarPontos" />
      </q-card-section>

      <q-card-section v-if="pontos.length">
        <q-markup-table flat bordered>
          <thead>
            <tr>
              <th class="text-center">Data</th>
              <th class="text-center">Entrada</th>
              <th class="text-center">Saída Almoço</th>
              <th class="text-center">Volta Almoço</th>
              <th class="text-center">Saída</th>
              <th class="text-center">Justificativa</th>
              <th class="text-center">Anexo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pontos" :key="p.id">
              <td class="text-center">{{ p.data }}</td>
              <td class="text-center">{{ formatar(p.entrada) }}</td>
              <td class="text-center">{{ formatar(p.saida_almoco) }}</td>
              <td class="text-center">{{ formatar(p.volta_almoco) }}</td>
              <td class="text-center">{{ formatar(p.saida) }}</td>
              <td class="text-center">{{ p.justificativa || '-' }}</td>
              <td class="text-center">
                <a
                  v-if="p.arquivo"
                  :href="`http://localhost:8000/justificativas/arquivo/${p.arquivo}`"
                  target="_blank"
                  download
                >
                  📎
                </a>
              </td>
            </tr>
          </tbody>
        </q-markup-table>
      </q-card-section>
      <q-card-section v-else class="text-center text-grey q-mt-lg">
        Nenhum registro de ponto encontrado para o período selecionado.
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import dayjs from 'dayjs'

const auth = useAuthStore()

const modo = ref<'dia' | 'mes'>('dia')
const dataSelecionada = ref(dayjs().format('YYYY-MM-DD'))
const mesSelecionado = ref(dayjs().format('YYYY-MM'))

interface Registro {
  id: number
  data: string
  entrada: string | null
  saida_almoco: string | null
  volta_almoco: string | null
  saida: string | null
  justificativa?: string
  arquivo?: string
}

const pontos = ref<Registro[]>([])  // <- Correção aqui

function formatar(data: string | null | undefined) {
  return data ? dayjs(data).format('HH:mm') : '-'
}

async function buscarPontos() {
  const colaborador_id = auth.colaboradorId
  if (!colaborador_id) {
    Notify.create({ type: 'negative', message: 'Você não está vinculado a um colaborador.' })
    return
  }

  try {
    let inicio = ''
    let fim = ''

    if (modo.value === 'dia') {
      inicio = fim = dataSelecionada.value
    } else {
      const [ano, mes] = mesSelecionado.value.split('-')
      inicio = dayjs(`${ano}-${mes}-01`).startOf('month').format('YYYY-MM-DD')
      fim = dayjs(`${ano}-${mes}-01`).endOf('month').format('YYYY-MM-DD')
    }

    const res = await api.get('/pontos/por-data', {
      params: {
        colaborador_id,
        inicio,
        fim
      },
      headers: { Authorization: `Bearer ${auth.token}` }
    })

    pontos.value = res.data
  } catch {
    pontos.value = []
    Notify.create({ type: 'negative', message: 'Erro ao buscar registros de ponto' })
  }
}
</script>
