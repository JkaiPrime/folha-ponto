<template>
  <q-page class="q-pa-md">

    <!-- ===== INSERÇÃO PONTUAL (seu fluxo atual) ===== -->
    <q-card class="q-mb-lg">
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
            outlined dense stack-label hide-bottom-space
            :rules="[v => !!v || 'Selecione um colaborador']"
          />

          <q-input
            v-model="data"
            label="Data"
            outlined dense stack-label hide-bottom-space
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

          <div class="row items-center">
            <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
              <q-input
                v-model="horaEntrada"
                label="Entrada"
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
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
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
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
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
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
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
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
            outlined dense stack-label hide-bottom-space
          />

          <q-banner v-if="erroOrdem" class="bg-orange-2 text-orange-10">
            A ordem dos horários está inconsistente (entrada ≤ saída almoço ≤ volta almoço ≤ saída).
          </q-banner>

          <div class="row q-gutter-sm">
            <q-btn label="Inserir registro" color="primary" :loading="loading" @click="inserir" />
            <q-btn flat label="Limpar" color="grey" @click="resetForm" />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- ===== INSERÇÃO POR PERÍODO ===== -->
    <q-card>
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Inserir ponto em período</div>
        <q-badge color="primary" outline>Somente Gestão</q-badge>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="q-gutter-md">
          <q-select
            v-model="periodoColabCode"
            :options="colabOptions"
            option-value="value"
            option-label="label"
            emit-value map-options
            label="Selecionar colaborador"
            outlined dense stack-label hide-bottom-space
            :rules="[v => !!v || 'Selecione um colaborador']"
          />

          <div class="row q-col-gutter-sm">
            <div class="col-12 col-md-6">
              <q-input
                v-model="periodoRangeLabel"
                label="Período"
                outlined dense stack-label hide-bottom-space readonly
              >
                <template #append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="periodoRange" mask="YYYY-MM-DD" range />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>

            <div class="col-12 col-md-6 row items-center">
              <q-checkbox v-model="incluirSabado" label="Incluir sábado" class="q-mr-md" />
              <q-checkbox v-model="incluirDomingo" label="Incluir domingo" class="q-mr-md" />
              <q-checkbox v-model="pularFeriados" label="Pular feriados" />
            </div>
          </div>

          <div class="row items-center">
            <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
              <q-input
                v-model="pEntrada"
                label="Entrada"
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
              >
                <template #append>
                  <q-icon name="schedule" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="pEntrada" format24h :minute-options="minuteOpts" now-btn />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>

            <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
              <q-input
                v-model="pSaidaAlmoco"
                label="Saída almoço"
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
              >
                <template #append>
                  <q-icon name="schedule" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="pSaidaAlmoco" format24h :minute-options="minuteOpts" now-btn />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>

            <div class="col-12 col-sm-6 col-md-3 q-pr-sm">
              <q-input
                v-model="pVoltaAlmoco"
                label="Volta almoço"
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
              >
                <template #append>
                  <q-icon name="schedule" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="pVoltaAlmoco" format24h :minute-options="minuteOpts" now-btn />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-input
                v-model="pSaida"
                label="Saída"
                outlined dense mask="time" clearable placeholder="hh:mm"
                stack-label hide-bottom-space class="time-field"
              >
                <template #append>
                  <q-icon name="schedule" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="pSaida" format24h :minute-options="minuteOpts" now-btn />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </div>

          <q-input
            v-model="pJustificativa"
            type="textarea"
            autogrow
            label="Justificativa (opcional)"
            outlined dense stack-label hide-bottom-space
          />

          <q-banner v-if="pErroOrdem" class="bg-orange-2 text-orange-10">
            A ordem dos horários está inconsistente (entrada ≤ saída almoço ≤ volta almoço ≤ saída).
          </q-banner>

          <div class="row q-gutter-sm">
            <q-btn label="Inserir período" color="primary" :loading="pLoading" @click="inserirPeriodo" />
            <q-btn flat label="Limpar" color="grey" @click="resetPeriodo" />
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

/** Tipos */
interface Colaborador {
  code: string
  nome: string
}
interface ColabOption {
  label: string
  value: string
}
interface ApiColaborador {
  code: string
  nome: string
}
interface RegistroPontoManualCreate {
  code: string
  data: string
  entrada?: string
  saida_almoco?: string
  volta_almoco?: string
  saida?: string
  justificativa?: string | null
}
type Range = { from: string; to: string } | null

/** State compartilhado */
const colaboradores = ref<Colaborador[]>([])
const colabOptions = computed<ColabOption[]>(() =>
  colaboradores.value.map(c => ({ label: `${c.nome} — ${c.code}`, value: c.code }))
)
const minuteOpts = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55] as const

/** ====== BLOCO PONTUAL ====== */
const colaboradorCode = ref<string | null>(null)
const data = ref<string>('')

const horaEntrada = ref<string>('')       // hh:mm
const horaSaidaAlmoco = ref<string>('')   // hh:mm
const horaVoltaAlmoco = ref<string>('')   // hh:mm
const horaSaida = ref<string>('')         // hh:mm

const justificativa = ref<string>('')
const loading = ref(false)

/** ====== BLOCO PERÍODO ====== */
const periodoColabCode = ref<string | null>(null)
const periodoRange = ref<Range>(null)
const periodoRangeLabel = computed(() => {
  const r = periodoRange.value
  if (!r) return ''
  return r.from === r.to ? r.from : `${r.from} → ${r.to}`
})
const incluirSabado = ref(false)
const incluirDomingo = ref(false)
const pularFeriados = ref(true)

const pEntrada = ref<string>('')
const pSaidaAlmoco = ref<string>('')
const pVoltaAlmoco = ref<string>('')
const pSaida = ref<string>('')
const pJustificativa = ref<string>('')
const pLoading = ref(false)

/** Utils */
function isValidHHMM (v: string): boolean {
  return !!v && !v.includes('_') && /^\d{2}:\d{2}$/.test(v)
}
function toMaybeMinutes (hhmm: string): number | null {
  if (!isValidHHMM(hhmm)) return null
  const [h, m] = hhmm.split(':')
  const n = Number(h) * 60 + Number(m)
  return Number.isFinite(n) ? n : null
}
function joinISO (d: string, hhmm: string): string {
  return `${d}T${hhmm}:00`
}

/** Validações de ordem */
const erroOrdem = computed<boolean>(() => {
  const t0 = toMaybeMinutes(horaEntrada.value)
  const t1 = toMaybeMinutes(horaSaidaAlmoco.value)
  const t2 = toMaybeMinutes(horaVoltaAlmoco.value)
  const t3 = toMaybeMinutes(horaSaida.value)
  const ok = (a: number | null, b: number | null) => (a === null || b === null || a <= b)
  return !(ok(t0, t1) && ok(t1, t2) && ok(t2, t3))
})
const pErroOrdem = computed<boolean>(() => {
  const t0 = toMaybeMinutes(pEntrada.value)
  const t1 = toMaybeMinutes(pSaidaAlmoco.value)
  const t2 = toMaybeMinutes(pVoltaAlmoco.value)
  const t3 = toMaybeMinutes(pSaida.value)
  const ok = (a: number | null, b: number | null) => (a === null || b === null || a <= b)
  return !(ok(t0, t1) && ok(t1, t2) && ok(t2, t3))
})



/** Carregar colaboradores */
async function carregarColaboradores(): Promise<void> {
  try {
    const { data } = await api.get<ApiColaborador[]>('/colaboradores')
    colaboradores.value = data
      .map((c) => ({ code: c.code, nome: c.nome }))
      .filter((c) => /^\d{6}$/.test(c.code) && c.nome.trim().length > 0)
  } catch {
    colaboradores.value = []
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaboradores' })
  }
}

/** Ações — pontual */
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
    ...(justificativa.value.trim() ? { justificativa: justificativa.value.trim() } : {})
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

/** Ações — período */
function resetPeriodo (): void {
  periodoColabCode.value = null
  periodoRange.value = null
  incluirSabado.value = false
  incluirDomingo.value = false
  pularFeriados.value = true
  pEntrada.value = ''
  pSaidaAlmoco.value = ''
  pVoltaAlmoco.value = ''
  pSaida.value = ''
  pJustificativa.value = ''
}
async function inserirPeriodo (): Promise<void> {
  if (!periodoColabCode.value) {
    Notify.create({ type: 'warning', message: 'Selecione um colaborador' })
    return
  }
  if (!periodoRange.value) {
    Notify.create({ type: 'warning', message: 'Selecione o período' })
    return
  }
  const anyTime =
    isValidHHMM(pEntrada.value) ||
    isValidHHMM(pSaidaAlmoco.value) ||
    isValidHHMM(pVoltaAlmoco.value) ||
    isValidHHMM(pSaida.value)

  if (!anyTime) {
    Notify.create({ type: 'warning', message: 'Informe pelo menos um horário válido' })
    return
  }
  if (pErroOrdem.value) {
    Notify.create({ type: 'warning', message: 'A ordem dos horários está inconsistente' })
    return
  }

  const payload = {
    code: periodoColabCode.value,
    inicio: periodoRange.value.from,
    fim: periodoRange.value.to,
    ...(isValidHHMM(pEntrada.value)      ? { entrada:      pEntrada.value }      : {}),
    ...(isValidHHMM(pSaidaAlmoco.value)  ? { saida_almoco: pSaidaAlmoco.value }  : {}),
    ...(isValidHHMM(pVoltaAlmoco.value)  ? { volta_almoco: pVoltaAlmoco.value }  : {}),
    ...(isValidHHMM(pSaida.value)        ? { saida:        pSaida.value }        : {}),
    incluir_sabado: incluirSabado.value,
    incluir_domingo: incluirDomingo.value,
    pular_feriados: pularFeriados.value,
    ...(pJustificativa.value.trim() ? { justificativa: pJustificativa.value.trim() } : {})
  }

  pLoading.value = true
  try {
    const { data } = await api.post('/pontos/inserir-periodo', payload)
    const ok = Number(data?.sucesso ?? 0)
    const skip = Number(data?.pulados ?? 0)
    const tot = Number(data?.total ?? 0)
    Notify.create({ type: 'positive', message: `Período processado: ${ok}/${tot} dias inseridos (${skip} pulados)` })
    resetPeriodo()
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao inserir período' })
  } finally {
    pLoading.value = false
  }
}

onMounted(() => { void carregarColaboradores() })
</script>

<style scoped>
.time-field.q-field--dense .q-field__control { min-height: 36px; height: 36px; }
.time-field .q-field__marginal,
.time-field .q-field__append,
.time-field .q-field__prepend { height: 36px; }
.time-field .q-field__native { padding-top: 2px; padding-bottom: 2px; }
</style>
