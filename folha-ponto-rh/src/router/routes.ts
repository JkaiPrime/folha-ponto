
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/LoginPage.vue') },
      { path: 'dashboard', component: () => import('pages/DashboardPage.vue') },
      { path: 'visualizar', component: () => import('pages/VisualizarPontos.vue') },
      { path: 'editar', component: () => import('pages/EditarPontos.vue') }
    ]
  },

  // Rota 404 (sempre por último)
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
];


export default routes;
