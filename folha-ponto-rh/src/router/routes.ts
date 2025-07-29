
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/LoginPage.vue') },
      { path: 'justificativas', component: () => import('pages/JustificativaPonto.vue') },
      { path: 'bater-ponto', component: () => import('pages/BaterPonto.vue') },
      { path: 'meus-pontos', component: () => import('pages/MeusPontos.vue') },
      { path: 'dashboard', component: () => import('pages/DashboardPage.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'visualizar', component: () => import('pages/VisualizarPontos.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'editar', component: () => import('pages/EditarPontos.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'excluir', component: () => import('pages/ExcluirPonto.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'cadastrar-colaborador', component: () => import('pages/CadastrarColaborador.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'criar-acesso',component: () => import('pages/GerenciarAcesso.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'listar-colaboradores',component: () => import('pages/GerenciarColaboradores.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: 'gerenciar-justificativa',component: () => import('pages/GerenciarJustificativas.vue') , meta: { requiresAuth: true , role: 'gestao' } },
      { path: '/acesso-negado', component: () => import('pages/AcessoNegado.vue')}
    ]
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
];


export default routes;
