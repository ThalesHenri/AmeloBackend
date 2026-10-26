from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main.views import (
    CondominioViewSet,
    DemandaViewSet,
    SupervisorViewSet,
    ProfissionalViewSet,
    AnexoViewSet,
    HealthCheckView,
    DashboardSummaryView,
    AtividadesSupervisoresView,
    MetricasProfissionaisView,
)

router = DefaultRouter()
router.register(r'condominios', CondominioViewSet, basename='condominio')
router.register(r'demandas', DemandaViewSet, basename='demanda')
router.register(r'supervisores', SupervisorViewSet, basename='supervisor')
router.register(r'profissionais', ProfissionalViewSet, basename='profissional')
# 🔥 Registrando a rota de anexos
router.register(r'anexos', AnexoViewSet, basename='anexo') 

urlpatterns = [
    path('', include(router.urls)),
    path('health/',HealthCheckView.as_view(), name='health-check'),
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/atividades-supervisores/', AtividadesSupervisoresView.as_view(), name='dashboard-atividades-supervisores'),
    path('dashboard/metricas-profissionais/', MetricasProfissionaisView.as_view(), name='dashboard-metricas-profissionais'),
]