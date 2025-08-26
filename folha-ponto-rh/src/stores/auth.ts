import { defineStore } from 'pinia'
import { ref } from 'vue'
import { jwtDecode } from 'jwt-decode'
import { api } from 'boot/axios'

/** Perfis suportados no app */
export type Role = 'gestao' | 'funcionario' | 'admin' | 'administrador'

/** Resposta de /me/colaborador */
export interface MeColaborador {
  id: number
  code: string
  nome: string
  email: string
  role: Role
}

/** Payload do JWT que você disse emitir hoje */
interface JwtPayload {
  sub: string
  role: 'gestao' | 'funcionario'
}

/** Converte valor desconhecido para Role válida, senão null */
function normalizeRole(value: unknown): Role | null {
  if (typeof value !== 'string') return null
  const v = value.toLowerCase()
  if (v === 'gestao') return 'gestao'
  if (v === 'funcionario') return 'funcionario'
  if (v === 'admin') return 'admin'
  if (v === 'administrador') return 'administrador'
  return null
}

export const useAuthStore = defineStore('auth', () => {
  /** Token legado (compat), sessão principal via cookie HttpOnly */
  const token = ref<string | null>(localStorage.getItem('token'))

  /** Papel atual para liberar menus/rotas */
  const role = ref<Role | null>(null)

  /** Code do colaborador (ex.: "116987") */
  const colaboradorId = ref<string | null>(null)

  /** Objeto com os dados do usuário logado (fonte de verdade para o app) */
  const me = ref<Partial<MeColaborador>>({})

  /** Flag de bootstrap de usuário (evita re-fetch desnecessário) */
  const userLoaded = ref(false)

  /** Atualiza o store com um patch parcial de /me/colaborador (sem passar role: undefined) */
  function setMe(payload: Partial<MeColaborador>): void {
    const norm = normalizeRole((payload as { role?: unknown }).role)

    // Monta patch SEM incluir role quando não houver valor válido
    const patch: Partial<MeColaborador> = {
      ...(typeof payload.id === 'number' ? { id: payload.id } : {}),
      ...(typeof payload.code === 'string' ? { code: payload.code } : {}),
      ...(typeof payload.nome === 'string' ? { nome: payload.nome } : {}),
      ...(typeof payload.email === 'string' ? { email: payload.email } : {}),
      ...(norm ? { role: norm } : {})
    }

    me.value = { ...me.value, ...patch }

    if (typeof patch.code === 'string') {
      colaboradorId.value = patch.code
    }
    if (patch.role) {
      role.value = patch.role
    }
  }

  // Bootstrap por token salvo (compatibilidade com fluxo antigo)
  if (token.value) {
    try {
      const decoded = jwtDecode<JwtPayload>(token.value)
      const norm = normalizeRole(decoded.role)
      if (norm) role.value = norm

      api.get<MeColaborador>('/me/colaborador', {
        headers: { Authorization: `Bearer ${token.value}` },
        withCredentials: true
      })
        .then((res) => {
          setMe(res.data)
        })
        .catch(() => {
          colaboradorId.value = null
        })
        .finally(() => {
          userLoaded.value = true
        })
    } catch {
      userLoaded.value = true
    }
  } else {
    userLoaded.value = true
  }

  /** Busca os dados do usuário usando cookie HttpOnly */
  async function fetchUser(): Promise<void> {
    try {
      const res = await api.get<Partial<MeColaborador>>('/me/colaborador', { withCredentials: true })
      setMe(res.data ?? {})
    } catch {
      me.value = {}
      colaboradorId.value = null
      role.value = null
    } finally {
      userLoaded.value = true
    }
  }

  /** Login (salva token legado e sincroniza /me) */
  async function login(novoToken: string): Promise<void> {
    token.value = novoToken
    localStorage.setItem('token', novoToken)

    try {
      const decoded = jwtDecode<JwtPayload>(novoToken)
      const decodedNorm = normalizeRole(decoded.role)
      if (decodedNorm) role.value = decodedNorm

      const res = await api.get<Partial<MeColaborador>>('/me/colaborador', {
        headers: { Authorization: `Bearer ${novoToken}` },
        withCredentials: true
      })

      // Normaliza role escolhendo a do backend (se houver) senão a do token
      const normalized = normalizeRole(res.data?.role ?? decoded.role)

      // >>>>>>> AQUI O AJUSTE IMPORTANTE <<<<<<<
      // NUNCA passe role: undefined com exactOptionalPropertyTypes!
      setMe({
        ...(res.data ?? {}),
        ...(normalized ? { role: normalized } as Pick<MeColaborador, 'role'> : {})
      })
    } catch {
      colaboradorId.value = null
    }
  }

  /** Logout (invalida sessão no servidor e limpa cliente) */
  async function logout(): Promise<void> {
    try {
      await api.post('/auth/logout', null, { withCredentials: true })
    } catch {
      /* noop */
    }
    token.value = null
    role.value = null
    colaboradorId.value = null
    me.value = {}
    localStorage.removeItem('token')
  }

  return {
    // state
    token,
    role,
    colaboradorId,
    me,
    userLoaded,
    // actions
    fetchUser,
    login,
    logout,
    setMe
  }
})
