<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md q-mx-auto" style="max-width: 560px;">
      <!-- Cabeçalho: logo + hora -->
      <q-card-section class="column items-center">
        <img src="src/assets/logo.svg" alt="PontoX" style="max-width: 160px" />
        <div class="text-h4 q-mt-sm" aria-live="polite">{{ horaAtual }}</div>
        <div class="text-caption text-grey-6">Horário local (America/Sao_Paulo)</div>
      </q-card-section>

      <!-- Info do colaborador -->
      <q-card-section>
        <div class="row items-center q-gutter-md">
          <q-avatar size="44px" class="bg-primary-1 text-primary">
            {{ initials }}
          </q-avatar>
          <div class="col">
            <div class="text-body1 text-weight-medium ellipsis">{{ nomeColaborador || 'Usuário' }}</div>
            <div class="text-caption text-grey-7">
              Código: <span class="text-weight-medium">{{ codigoColaborador || '—' }}</span>
              <q-separator vertical spaced inset />
              <span class="text-grey-7">{{ emailColaborador || '' }}</span>
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Status -->
      <q-card-section class="q-pt-none">
        <q-banner
          v-if="statusLoaded && statusMsg"
          :class="canPunch ? 'bg-green-1 text-green-9' : 'bg-amber-1 text-amber-9'"
          rounded
          dense
        >
          <template #avatar>
            <q-icon :name="canPunch ? 'task_alt' : 'schedule'" :color="canPunch ? 'green' : 'amber-9'" />
          </template>
          {{ statusMsg }}
        </q-banner>

        <q-skeleton v-else type="rect" height="36px" class="rounded-borders" />
      </q-card-section>

      <!-- CTA -->
      <q-card-section>
        <q-btn
          class="full-width"
          color="primary"
          size="lg"
          :unelevated="true"
          :loading="loading"
          :disable="disableButton"
          label="BATER PONTO"
          @click="baterPonto"
          aria-label="Bater ponto"
        />
        <div class="text-caption text-grey-6 q-mt-xs">
          Dica: pressione <kbd>Enter</kbd> para bater o ponto.
        </div>

        <transition name="fade">
          <q-banner v-if="mensagemSucesso" class="bg-green-1 text-green q-mt-md" rounded dense>
            <template #avatar><q-icon name="check_circle" color="green" /></template>
            {{ mensagemSucesso }}
          </q-banner>
        </transition>

        <transition name="fade">
          <q-banner v-if="mensagemInfo" class="bg-blue-1 text-blue q-mt-sm" rounded dense>
            <template #avatar><q-icon name="info" color="blue" /></template>
            {{ mensagemInfo }}
          </q-banner>
        </transition>

        <transition name="fade">
          <q-banner v-if="mensagemErro" class="bg-red-1 text-red q-mt-sm" rounded dense>
            <template #avatar><q-icon name="error" color="red" /></template>
            {{ mensagemErro }}
          </q-banner>
        </transition>
      </q-card-section>

      <!-- Batidas de hoje -->
      <q-separator />
      <q-card-section>
        <div class="row items-center justify-between q-mb-sm">
          <div class="text-subtitle2">Batidas de hoje</div>
          <q-btn flat dense icon="refresh" @click="carregarBatidasHoje" :loading="loadingBatidas" aria-label="Atualizar batidas" />
        </div>

        <div v-if="loadingBatidas">
          <q-skeleton type="text" width="80%" />
          <q-skeleton type="text" width="60%" />
          <q-skeleton type="text" width="40%" />
        </div>

        <div v-else-if="batidasHoje.length === 0" class="text-caption text-grey-7">
          Nenhuma batida registrada hoje ainda.
        </div>

        <q-timeline v-else color="primary" layout="dense">
          <q-timeline-entry
            v-for="b in batidasHoje"
            :key="b.id + '-' + b.tipo + '-' + b.hora"
            :title="b.tipoLabel"
            :subtitle="b.hora"
            :icon="b.icon"
            :color="b.color"
          >
            <div class="text-caption text-grey-7">{{ b.obs || '—' }}</div>
          </q-timeline-entry>
        </q-timeline>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { api } from 'boot/axios'
import { Notify } from 'quasar'
import dayjs from 'dayjs'
import type { AxiosError } from 'axios'

/** Types */
interface ErrorResponse { detail?: string; message?: string }
interface RegistroHojeApi {
  id: number
  data: string
  entrada?: string | null
  saida_almoco?: string | null
  volta_almoco?: string | null
  saida?: string | null
  justificativa?: string | null
}
interface BatidaUI {
  id: number
  tipo: string
  tipoLabel: string
  hora: string
  color: string
  icon: string
  obs?: string
}

/** State */
const horaAtual = ref(dayjs().format('HH:mm:ss'))
const tick = ref<number | null>(null)

const loading = ref(false)
const mensagemErro = ref('')
const mensagemSucesso = ref('')
const mensagemInfo = ref('')

const nomeColaborador = ref('')
const emailColaborador = ref('')
const codigoColaborador = ref('')
const colaboradorId = ref<number | null>(null)

const statusLoaded = ref(false)
const canPunch = ref(false)
const statusMsg = ref('')

const loadingBatidas = ref(false)
const batidasHoje = ref<BatidaUI[]>([])

/** Derivados */
const initials = computed(() => {
  const parts = (nomeColaborador.value || '').trim().split(/\s+/).filter(Boolean)
  const first = parts.length > 0 ? parts[0]!.charAt(0) : 'U'
  const lastPart = parts.length > 1 ? parts[parts.length - 1] : undefined
  const last = lastPart ? lastPart.charAt(0) : ''
  return (first + last).toUpperCase()
})
const disableButton = computed(() => loading.value || (statusLoaded.value && !canPunch.value))

/** Lifecycle */
onMounted(async () => {
  iniciarRelogio()
  await carregarColaborador()
  await verificarStatusJanela()
  await carregarBatidasHoje()
  document.addEventListener('keydown', onKeypress)
})
onBeforeUnmount(() => {
  pararRelogio()
  document.removeEventListener('keydown', onKeypress)
})

function iniciarRelogio() {
  pararRelogio()
  tick.value = window.setInterval(() => {
    horaAtual.value = dayjs().format('HH:mm:ss')
  }, 1000)
}
function pararRelogio() {
  if (tick.value !== null) {
    clearInterval(tick.value)
    tick.value = null
  }
}
function onKeypress(e: KeyboardEvent) {
  if (e.key === 'Enter' && !disableButton.value) {
    void baterPonto()
  }
}

/** API: /me/colaborador */
async function carregarColaborador() {
  try {
    const res = await api.get('/me/colaborador', { withCredentials: true })
    nomeColaborador.value = res.data?.nome || ''
    emailColaborador.value = res.data?.email || ''
    codigoColaborador.value = res.data?.code || ''
    colaboradorId.value = typeof res.data?.id === 'number' ? res.data.id : null
  } catch {
    Notify.create({ type: 'negative', message: 'Erro ao carregar colaborador' })
  }
}

/** API: /pontos/status (opcional – se não existir, mantemos fallback) */
async function verificarStatusJanela() {
  statusLoaded.value = false
  mensagemInfo.value = ''
  try {
    const res = await api.get('/pontos/status', { withCredentials: true })
    canPunch.value = Boolean(res.data?.allowed)
    statusMsg.value = String(res.data?.message || (canPunch.value ? 'Liberado para bater ponto.' : 'Indisponível'))
  } catch {
    // se ainda não implementou /pontos/status, deixa habilitado com msg neutra
    canPunch.value = true
    statusMsg.value = 'Status indisponível no momento.'
  } finally {
    statusLoaded.value = true
  }
}

/** Util: mapa de tipo -> rótulos */
function mapTipo(tipo: string): { label: string; color: string; icon: string } {
  switch (tipo) {
    case 'entrada': return { label: 'Entrada', color: 'primary', icon: 'login' }
    case 'saida_almoco': return { label: 'Saída almoço', color: 'orange-8', icon: 'lunch_dining' }
    case 'volta_almoco': return { label: 'Volta almoço', color: 'teal-7', icon: 'restaurant' }
    case 'saida': return { label: 'Saída', color: 'deep-orange-8', icon: 'logout' }
    default: return { label: 'Batida', color: 'grey-7', icon: 'schedule' }
  }
}
function addIfPresent(
  list: BatidaUI[],
  registroId: number,
  tipo: 'entrada' | 'saida_almoco' | 'volta_almoco' | 'saida',
  iso?: string | null,
  obs?: string | null
) {
  if (!iso) return
  const map = mapTipo(tipo)
  const item: BatidaUI = {
    id: registroId,
    tipo,
    tipoLabel: map.label,
    color: map.color,
    icon: map.icon,
    hora: dayjs(iso).isValid() ? dayjs(iso).format('HH:mm:ss') : '--:--:--'
  }
  if (obs) item.obs = obs
  list.push(item)
}

/** API: /pontos/hoje/me → apenas do usuário logado */
async function carregarBatidasHoje() {
  loadingBatidas.value = true
  try {
    const res = await api.get('/pontos/hoje/me', { withCredentials: true })
    const rows: RegistroHojeApi[] = Array.isArray(res.data) ? res.data : []

    const items: BatidaUI[] = []
    for (const r of rows) {
      const rid = Number(r.id || 0)
      addIfPresent(items, rid, 'entrada', r.entrada, r.justificativa ?? null)
      addIfPresent(items, rid, 'saida_almoco', r.saida_almoco, r.justificativa ?? null)
      addIfPresent(items, rid, 'volta_almoco', r.volta_almoco, r.justificativa ?? null)
      addIfPresent(items, rid, 'saida', r.saida, r.justificativa ?? null)
    }
    items.sort((a, b) => a.hora.localeCompare(b.hora))
    batidasHoje.value = items
  } catch {
    batidasHoje.value = []
  } finally {
    loadingBatidas.value = false
  }
}

/** POST /pontos/bater-ponto */
async function baterPonto() {
  mensagemErro.value = ''
  mensagemSucesso.value = ''
  mensagemInfo.value = ''
  loading.value = true

  const payload = colaboradorId.value ? { colaborador_id: colaboradorId.value } : {}

  try {
    const res = await api.post('/pontos/bater-ponto', payload, { withCredentials: true })
    if (res?.data?.tipo) {
      mensagemSucesso.value = `Ponto registrado: ${String(res.data.tipo).toUpperCase()}`
    } else {
      mensagemSucesso.value = 'Ponto registrado com sucesso.'
    }
    await Promise.all([verificarStatusJanela(), carregarBatidasHoje()])
  } catch (err) {
    const ax = err as AxiosError<ErrorResponse>
    const detail = ax?.response?.data?.detail || ax?.response?.data?.message
    mensagemErro.value = detail || 'Erro ao registrar ponto.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
