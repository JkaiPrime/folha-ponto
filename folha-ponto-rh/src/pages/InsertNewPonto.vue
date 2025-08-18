<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Inserir ponto manual</div>
        <q-badge color="primary" outline>Somente Gestão</q-badge>
      </q-card-section>

      <q-separator />

      <q-card-section>
  <div class="q-gutter-md">

    <q-select
      v-model="colaboradorCode"
      :options="colabOptions"
      option-value="value"
      option-label="label"
      emit-value
      map-options
      label="Selecionar colaborador"
      outlined
      dense
      stack-label
      hide-bottom-space
      :rules="[v => !!v || 'Selecione um colaborador']"
    />

    <q-input
      v-model="data"
      label="Data"
      outlined
      dense
      stack-label
      hide-bottom-space
      :rules="[v => !!v || 'Informe a data']"
      readonly
    >
      <template #append>
        <q-icon name="event" class="cursor-pointer">
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-date v-model="data" mask="YYYY-MM-DD" />
          </q-popup-proxy>
        </q-icon>
      </template>
    </q-input>

    <!-- Linha dos horários 100% alinhada às bordas -->
    <div class="row items-center">
      <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
        <q-input
          v-model="horaEntrada"
          label="Entrada"
          outlined
          dense
          mask="time"
          clearable
          placeholder="hh:mm"
          stack-label
          hide-bottom-space
          class="time-field"
        >
          <template #append>
            <q-icon name="schedule" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-time v-model="horaEntrada" format24h :minute-options="minuteOpts" now-btn />
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </div>

      <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
        <q-input
          v-model="horaSaidaAlmoco"
          label="Saída almoço"
          outlined
          dense
          mask="time"
          clearable
          placeholder="hh:mm"
          stack-label
          hide-bottom-space
          class="time-field"
        >
          <template #append>
            <q-icon name="schedule" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-time v-model="horaSaidaAlmoco" format24h :minute-options="minuteOpts" now-btn />
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </div>

      <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
        <q-input
          v-model="horaVoltaAlmoco"
          label="Volta almoço"
          outlined
          dense
          mask="time"
          clearable
          placeholder="hh:mm"
          stack-label
          hide-bottom-space
          class="time-field"
        >
          <template #append>
            <q-icon name="schedule" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-time v-model="horaVoltaAlmoco" format24h :minute-options="minuteOpts" now-btn />
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-input
          v-model="horaSaida"
          label="Saída"
          outlined
          dense
          mask="time"
          clearable
          placeholder="hh:mm"
          stack-label
          hide-bottom-space
          class="time-field"
        >
          <template #append>
            <q-icon name="schedule" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-time v-model="horaSaida" format24h :minute-options="minuteOpts" now-btn />
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </div>
    </div>

    <q-input
      v-model="justificativa"
      type="textarea"
      autogrow
      label="Justificativa (opcional)"
      outlined
      dense
      stack-label
      hide-bottom-space
    />

    <q-banner v-if="erroOrdem" class="bg-orange-2 text-orange-10">
      A ordem dos horários está inconsistente. Verifique a sequência (entrada ≤ saída almoço ≤ volta almoço ≤ saída).
    </q-banner>

    <div class="row q-gutter-sm">
      <q-btn label="Inserir registro" color="primary" :loading="loading" @click="inserir" />
      <q-btn flat label="Limpar" color="grey" @click="resetForm" />
    </div>
  </div>
</q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Notify } from 'quasar'
import { api } from 'boot/axios'

/** Tipos fortes */
interface Colaborador {
  code: string
  nome: string
}
interface ColabOption {
  label: string
  value: string
}
interface RegistroPontoManualCreate {
  code: string
  data: string              // YYYY-MM-DD
  entrada?: string          // ISO local: 2025-08-18T09:00:00
  saida_almoco?: string
  volta_almoco?: string
  saida?: string
  justificativa?: string | null
}

/** State */
const colaboradores = ref<Colaborador[]>([])
const colabOptions = computed<ColabOption[]>(() =>
  colaboradores.value.map(c => ({
    label: `${c.nome} — ${c.code}`,
    value: c.code
  }))
)
const colaboradorCode = ref<string | null>(null)
const data = ref<string>('') // YYYY-MM-DD

const horaEntrada = ref<string>('')       // hh:mm (máscara)
const horaSaidaAlmoco = ref<string>('')   // hh:mm
const horaVoltaAlmoco = ref<string>('')   // hh:mm
const horaSaida = ref<string>('')         // hh:mm

const justificativa = ref<string>('')
const loading = ref(false)

/** Minutos em passos de 5 para o QTime */
const minuteOpts = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55] as const

/** Carrega colaboradores (tipado) */
async function carregarColaboradores (): Promise<void> {
  try {
    const res = await api.get<Colaborador[]>('/colaboradores')
    colaboradores.value = res.data
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaboradores' })
  }
}

/** Utilitários seguros */
function isValidHHMM (v: string): boolean {
  return !!v && !v.includes('_') && /^\d{2}:\d{2}$/.test(v)
}
function toMinutes (hhmm: string): number {
  const [hStr = '0', mStr = '0'] = hhmm.split(':')
  const h = Number(hStr)
  const m = Number(mStr)
  return h * 60 + m
}
function toMaybeMinutes (hhmm: string): number | null {
  if (!isValidHHMM(hhmm)) return null
  const n = toMinutes(hhmm)
  return Number.isFinite(n) ? n : null
}

/** Validação de ordem dos horários */
const erroOrdem = computed<boolean>(() => {
  const [t0, t1, t2, t3]: [number | null, number | null, number | null, number | null] = [
    toMaybeMinutes(horaEntrada.value),
    toMaybeMinutes(horaSaidaAlmoco.value),
    toMaybeMinutes(horaVoltaAlmoco.value),
    toMaybeMinutes(horaSaida.value)
  ]
  const check = (a: number | null, b: number | null) => (a === null || b === null || a <= b)
  return !(check(t0, t1) && check(t1, t2) && check(t2, t3))
})

/** Monta ISO local (sem TZ; backend normaliza Brasília) */
function joinISO (d: string, hhmm: string): string {
  return `${d}T${hhmm}:00`
}

function resetForm (): void {
  colaboradorCode.value = null
  data.value = ''
  horaEntrada.value = ''
  horaSaidaAlmoco.value = ''
  horaVoltaAlmoco.value = ''
  horaSaida.value = ''
  justificativa.value = ''
}

async function inserir (): Promise<void> {
  if (!colaboradorCode.value) {
    Notify.create({ type: 'warning', message: 'Selecione um colaborador' })
    return
  }
  if (!data.value) {
    Notify.create({ type: 'warning', message: 'Informe a data' })
    return
  }

  const validEntrada = isValidHHMM(horaEntrada.value)
  const validSaidaAlmoco = isValidHHMM(horaSaidaAlmoco.value)
  const validVoltaAlmoco = isValidHHMM(horaVoltaAlmoco.value)
  const validSaida = isValidHHMM(horaSaida.value)

  if (!validEntrada && !validSaidaAlmoco && !validVoltaAlmoco && !validSaida) {
    Notify.create({ type: 'warning', message: 'Informe pelo menos um horário válido' })
    return
  }
  if (erroOrdem.value) {
    Notify.create({ type: 'warning', message: 'A ordem dos horários está inconsistente' })
    return
  }

  const payload: RegistroPontoManualCreate = {
    code: colaboradorCode.value,
    data: data.value,
    ...(validEntrada      ? { entrada:      joinISO(data.value, horaEntrada.value) }      : {}),
    ...(validSaidaAlmoco  ? { saida_almoco: joinISO(data.value, horaSaidaAlmoco.value) }  : {}),
    ...(validVoltaAlmoco  ? { volta_almoco: joinISO(data.value, horaVoltaAlmoco.value) }  : {}),
    ...(validSaida        ? { saida:        joinISO(data.value, horaSaida.value) }        : {}),
    ...(justificativa.value.trim()
        ? { justificativa: justificativa.value.trim() }
        : {})
  }

  loading.value = true
  try {
    await api.post('/pontos/inserir-manual', payload)
    Notify.create({ type: 'positive', message: 'Registro inserido/atualizado com sucesso!' })
    resetForm()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao inserir registro' })
  } finally {
    loading.value = false
  }
}

onMounted(() => { void carregarColaboradores() })
</script>

<style scoped>
/* Reduz e iguala a altura dos inputs de horário */
.time-field.q-field--dense .q-field__control {
  min-height: 36px;
  height: 36px;
}
.time-field .q-field__marginal,
.time-field .q-field__append,
.time-field .q-field__prepend {
  height: 36px;
}
.time-field .q-field__native {
  padding-top: 2px;
  padding-bottom: 2px;
}

</style>
