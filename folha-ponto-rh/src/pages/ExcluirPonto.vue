<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 800px;">
      <q-card-section>
        <div class="text-h6">Excluir Registros de Ponto</div>
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
              <th class="text-center">Ações</th>
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
              <td class="text-center">
                <q-btn
                  dense
                  flat
                  icon="delete"
                  color="negative"
                  @click="confirmarExclusao(p.id)"
                />
              </td>
            </tr>
          </tbody>
        </q-markup-table>
      </q-card-section>

      <q-card-section v-else class="text-center text-grey q-mt-lg">
        Nenhum registro de ponto encontrado para o período selecionado.
      </q-card-section>
    </q-card>

    <!-- Diálogo de Confirmação -->
    <q-dialog v-model="mostrarDialogo">
      <q-card>
        <q-card-section class="text-h6">
          Confirmar Exclusão
        </q-card-section>
        <q-card-section>
          Tem certeza de que deseja excluir este registro de ponto? Esta ação é irreversível.
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn flat label="Excluir" color="negative" @click="removerPonto" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import dayjs from 'dayjs'

const mesSelecionado = ref(dayjs().format('YYYY-MM'))
const pontos = ref<Registro[]>([])
const mostrarDialogo = ref(false)
const pontoSelecionado = ref<number | null>(null)

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

function formatar(data: string | null | undefined) {
  return data ? dayjs(data).format('HH:mm') : '-'
}

async function buscarPontos() {
  try {
    const colaboradorRes = await api.get('/me/colaborador', { withCredentials: true });
    const colaboradorId = colaboradorRes.data.id;

    const [ano, mes] = mesSelecionado.value.split('-');
    const inicio = `${ano}-${mes}-01`;
    const fim = new Date(Number(ano), Number(mes), 0).toISOString().split('T')[0];

    const res = await api.get('/pontos/por-data', {
      params: { colaborador_id: colaboradorId, inicio, fim },
      withCredentials: true
    });

    pontos.value = res.data;
  } catch (error) {
    console.error('Erro ao buscar pontos:', error);
    pontos.value = [];
    Notify.create({ type: 'negative', message: 'Erro ao buscar seus pontos' });
  }
}

function confirmarExclusao(id: number) {
  pontoSelecionado.value = id
  mostrarDialogo.value = true
}

async function removerPonto() {
  if (!pontoSelecionado.value) return

  try {
    await api.delete(`/pontos/${pontoSelecionado.value}`, { withCredentials: true })
    Notify.create({ type: 'positive', message: 'Registro excluído com sucesso' })
    mostrarDialogo.value = false
    await buscarPontos()
  } catch (error) {
    console.error('Erro ao excluir ponto:', error)
    Notify.create({ type: 'negative', message: 'Erro ao excluir ponto' })
  }
}
</script>
