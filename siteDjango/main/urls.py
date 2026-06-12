from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main.views import (
    CondominioViewSet,
    DemandaViewSet,
    SupervisorViewSet,
    ProfissionalViewSet,
    AnexoViewSet # Adicione aqui
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
]