// src/router/routes.ts
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'login', component: () => import('pages/LoginPage.vue'), meta: { public: true } },

    
      { path: 'acesso-negado', name: 'forbidden', component: () => import('pages/AcessoNegado.vue'), meta: { public: true } },

      // autenticadas (qualquer usuário logado)
      { path: 'alterar-senha', name: 'alterar-senha', component: () => import('pages/ResetPassword.vue'), meta: { requiresAuth: true } },
      { path: 'bater-ponto', name: 'bater-ponto', component: () => import('pages/BaterPonto.vue'), meta: { requiresAuth: true } },
      { path: 'meus-pontos', name: 'meus-pontos', component: () => import('pages/MeusPontos.vue'), meta: { requiresAuth: true } },

      // somente gestão
      { path: 'dashboard', name: 'dashboard', component: () => import('pages/DashboardPage.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'visualizar', name: 'visualizar', component: () => import('pages/VisualizarPontos.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'editar', name: 'editar', component: () => import('pages/EditarPontos.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'excluir', name: 'excluir', component: () => import('pages/ExcluirPonto.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'cadastrar-colaborador', name: 'cadastrar-colaborador', component: () => import('pages/CadastrarColaborador.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'criar-acesso', name: 'criar-acesso', component: () => import('pages/GerenciarAcesso.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'listar-colaboradores', name: 'listar-colaboradores', component: () => import('pages/GerenciarColaboradores.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'gerenciar-justificativa', name: 'gerenciar-justificativa', component: () => import('pages/GerenciarJustificativas.vue'), meta: { requiresAuth: true, roles: ['gestao'] } },
      { path: 'insert-ponto', name: 'insert-ponto', component: () => import('pages/InsertNewPonto.vue'), meta: { requiresAuth: true, roles: ['gestao'] } }
    ]
  },
  { path: '/:catchAll(.*)*', name: 'not-found', component: () => import('pages/ErrorNotFound.vue') }
]
export default routes
