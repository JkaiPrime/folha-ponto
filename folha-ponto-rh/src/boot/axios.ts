// boot/axios.ts
import { boot } from 'quasar/wrappers';
import axios, { type AxiosError, type AxiosRequestConfig } from 'axios';
import { Notify } from 'quasar';
import { useAuthStore } from 'src/stores/auth';

/** Augmenta o tipo do Axios para aceitarmos a flag de skip */
declare module 'axios' {
  export interface AxiosRequestConfig {
    __skipAuthRedirect?: boolean;
  }
}
//baseURL: 'http://localhost:8000',
//baseURL: 'https://folha-ponto.onrender.com',
const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
});

export default boot(({ router }) => {
  api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const status = error.response?.status;
      const cfg: AxiosRequestConfig | undefined = error.config;
      const current = router.currentRoute.value;

      const isPublic = current.matched.some((r) => r.meta?.public === true);
      const skip = cfg?.__skipAuthRedirect === true;

      if (status === 401 && !isPublic && !skip) {
        const auth = useAuthStore();
        void auth.logout();

        Notify.create({
          type: 'warning',
          message: 'Sessão expirada. Faça login novamente.',
          position: 'top',
        });

        void router.push('/');
      }

      return Promise.reject(
        error instanceof Error
          ? error
          : new Error((error as Error)?.message || 'Erro desconhecido'),
      );
    },
  );
});

export { api };
