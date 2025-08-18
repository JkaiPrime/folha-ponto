declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: string;
    VUE_ROUTER_MODE: 'hash' | 'history' | 'abstract' | undefined;
    VUE_ROUTER_BASE: string | undefined;
  }
  interface ImportMetaEnv {
  readonly DEV: boolean
  readonly PROD: boolean
  // adicione aqui suas VITE_*
  readonly VITE_API_BASE?: string
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}
