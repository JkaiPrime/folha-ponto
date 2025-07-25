// boot/axios.ts

import { boot } from 'quasar/wrappers';
import axios from 'axios';
import { Notify } from 'quasar';
import { useAuthStore } from 'src/stores/auth';

const api = axios.create({
  baseURL: 'https://folha-ponto.onrender.com'
});

export default boot(({ router }) => {
  api.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        const auth = useAuthStore();
        auth.logout();

        Notify.create({
          type: 'warning',
          message: 'Sessão expirada. Faça login novamente.',
          position: 'top'
        });

        void router.push('/');
      }

      return Promise.reject(
        error instanceof Error ? error : new Error(error?.message || 'Erro desconhecido')
      );
    }
  );
});

export { api };
