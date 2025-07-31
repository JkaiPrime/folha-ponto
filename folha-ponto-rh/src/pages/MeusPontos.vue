<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 800px;">
      <q-card-section>
        <div class="text-h6">Visualizar Registros de Ponto</div>
      </q-card-section>

      <q-card-section class="q-gutter-md">
        <q-input
          filled
          v-model="mesSelecionado"
          label="Selecione o Mês"
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
              <th class="text-center">Alterado por</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pontos" :key="p.id">
              <td class="text-center">{{ p.data }}</td>
              <td class="text-center">{{ formatar(p.entrada) }}</td>
              <td class="text-center">{{ formatar(p.saida_almoco) }}</td>
              <td class="text-center">{{ formatar(p.volta_almoco) }}</td>
              <td class="text-center">{{ formatar(p.saida) }}</td>
              <td class="text-center">{{ p.alterado_por?.nome || '-' }}</td>
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
  alterado_por?: { id: number, nome: string } | null
  avaliador?: { id: number, nome: string } | null
}

const pontos = ref<Registro[]>([])

function formatar(data: string | null | undefined) {
  return data ? dayjs(data).format('HH:mm') : '-'
}

async function buscarPontos() {
  try {
    const colaboradorRes = await api.get('/me/colaborador', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    const colaboradorId = colaboradorRes.data.id;

    const [ano, mes] = mesSelecionado.value.split('-');
    const inicio = `${ano}-${mes}-01`;
    const fim = new Date(Number(ano), Number(mes), 0).toISOString().split('T')[0];

    const res = await api.get('/pontos/por-data', {
      params: {
        colaborador_id: colaboradorId,
        inicio,
        fim
      },
      headers: { Authorization: `Bearer ${auth.token}` }
    });

    pontos.value = res.data;
  } catch (error) {
    console.error('Erro ao buscar pontos:', error);
    pontos.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao buscar seus pontos' });
  }
}
</script>
