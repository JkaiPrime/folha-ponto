// src/router/routes.ts
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/LoginPage.vue'), meta: { public: true } },

      // 🔹 reset via link (pública)
      { path: 'reset-password', component: () => import('pages/ResetPasswordLink.vue'), meta: { public: true } },

      // 🔹 alterar senha logado (autenticada)
      { path: 'alterar-senha', component: () => import('pages/ResetPassword.vue'), meta: { requiresAuth: true } },

      { path: 'bater-ponto', component: () => import('pages/BaterPonto.vue') },
      { path: 'meus-pontos', component: () => import('pages/MeusPontos.vue') },
      { path: 'dashboard', component: () => import('pages/DashboardPage.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'visualizar', component: () => import('pages/VisualizarPontos.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'editar', component: () => import('pages/EditarPontos.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'excluir', component: () => import('pages/ExcluirPonto.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'cadastrar-colaborador', component: () => import('pages/CadastrarColaborador.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'criar-acesso', component: () => import('pages/GerenciarAcesso.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'listar-colaboradores', component: () => import('pages/GerenciarColaboradores.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'gerenciar-justificativa', component: () => import('pages/GerenciarJustificativas.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'insert-ponto', component: () => import('pages/InsertNewPonto.vue'), meta: { requiresAuth: true, role: 'gestao' } },
      { path: 'acesso-negado', component: () => import('pages/AcessoNegado.vue'), meta: { public: true } }
    ]
  },
  { path: '/:catchAll(.*)*', component: () => import('pages/ErrorNotFound.vue') }
]
export default routes
