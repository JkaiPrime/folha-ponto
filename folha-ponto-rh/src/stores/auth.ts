import { defineStore } from 'pinia'
import { ref } from 'vue'
import { jwtDecode } from 'jwt-decode'
import { api } from 'boot/axios'

interface JwtPayload {
  sub: string
  role: 'gestao' | 'funcionario'
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const role = ref<'gestao' | 'funcionario' | null>(null)
  const colaboradorId = ref<string | null>(null)

  if (token.value) {
    const decoded = jwtDecode<JwtPayload>(token.value)
    role.value = decoded.role

    // Opcional: recuperar colaboradorId se estiver em uso contínuo
    api.get('/me/colaborador', {
      headers: { Authorization: `Bearer ${token.value}` }
    }).then(res => {
      colaboradorId.value = res.data.code
    }).catch(() => {
      colaboradorId.value = null
    })
  }

  async function login(novoToken: string) {
    token.value = novoToken
    localStorage.setItem('token', novoToken)

    const decoded = jwtDecode<JwtPayload>(novoToken)
    role.value = decoded.role

    try {
      const res = await api.get('/me/colaborador', {
        headers: { Authorization: `Bearer ${novoToken}` }
      })
      colaboradorId.value = res.data.code
    } catch {
      colaboradorId.value = null
    }
  }

  function logout() {
    token.value = null
    role.value = null
    colaboradorId.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    role,
    colaboradorId,
    login,
    logout
  }
})
