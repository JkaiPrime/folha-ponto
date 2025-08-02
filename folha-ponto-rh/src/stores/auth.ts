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
  const userLoaded = ref(false)

  // ✅ Inicializa se houver token salvo (compatibilidade)
  if (token.value) {
    try {
      const decoded = jwtDecode<JwtPayload>(token.value)
      role.value = decoded.role

      api.get('/me/colaborador', {
        headers: { Authorization: `Bearer ${token.value}` },
        withCredentials: true
      }).then(res => {
        colaboradorId.value = res.data.code
        role.value = res.data.role || decoded.role
      }).catch(() => {
        colaboradorId.value = null
      }).finally(() => {
        userLoaded.value = true
      })
    } catch {
      userLoaded.value = true
    }
  } else {
    userLoaded.value = true
  }

  // ✅ Sessão via cookies HttpOnly
  async function fetchUser() {
    console.log('[DEBUG] Iniciando fetchUser()...');
    try {
      const res = await api.get('/me/colaborador', { withCredentials: true });
      console.log('[DEBUG] /me/colaborador response:', res.data);

      colaboradorId.value = res.data.code;
      role.value = res.data.role;
      console.log('[DEBUG] Role setada:', role.value);
    } catch (error) {
      console.error('[DEBUG] Erro em fetchUser:', error);
      colaboradorId.value = null;
      role.value = null;
    } finally {
      userLoaded.value = true;
      console.log('[DEBUG] userLoaded:', userLoaded.value);
    }
  }

  async function login(novoToken: string) {
    console.log('[DEBUG] Iniciando login()...');
    token.value = novoToken;
    localStorage.setItem('token', novoToken);

    try {
      const decoded = jwtDecode<JwtPayload>(novoToken);
      role.value = decoded.role;
      console.log('[DEBUG] Token decodificado:', decoded);

      const res = await api.get('/me/colaborador', {
        headers: { Authorization: `Bearer ${novoToken}` },
        withCredentials: true
      });
      console.log('[DEBUG] Dados do colaborador via token:', res.data);

      colaboradorId.value = res.data.code;
      role.value = res.data.role || decoded.role;
    } catch (error) {
      console.error('[DEBUG] Erro no login (me/colaborador):', error);
      colaboradorId.value = null;
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout', null, { withCredentials: true })
    } catch (e) {
      console.warn('Falha ao invalidar sessão no servidor', e)
    }

    token.value = null
    role.value = null
    colaboradorId.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    role,
    colaboradorId,
    userLoaded,
    login,
    logout,
    fetchUser
  }
})
