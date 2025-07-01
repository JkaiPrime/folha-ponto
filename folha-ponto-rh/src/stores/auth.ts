import { defineStore } from 'pinia';
import { login as apiLogin } from 'src/services/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null as string | null
  }),

  actions: {
    async login(email: string, password: string) {
      const response = await apiLogin(email, password); // chama função da services
      this.token = response.access_token;
      localStorage.setItem('token', response.access_token);
    },

    logout() {
      this.token = null;
      localStorage.removeItem('token');
    }
  }
});
