import time
from django.db import connection
from ..models import Condominio, Demanda

# Guarda o momento em que a aplicação iniciou
START_TIME = time.time()

class HealthService:
    @staticmethod
    def check_system_health() -> dict:
        db_ok = True
        condominios_count = 0
        demandas_ativas = 0

        try:
            # Força o teste de conexão ativa com o BD
            connection.ensure_connection()
            condominios_count = Condominio.objects.count()
            demandas_ativas = Demanda.objects.exclude(status='concluida').count()
        except Exception:
            db_ok = False

        return {
            "is_healthy": db_ok,
            "data": {
                "status": "UP" if db_ok else "DOWN",
                "database": "OK" if db_ok else "ERROR",
                "metrics": {
                    "total_condominios": condominios_count if db_ok else 0,
                    "demandas_ativas": demandas_ativas if db_ok else 0,
                },
                "uptime_seconds": round(time.time() - START_TIME, 2)
            }
        }