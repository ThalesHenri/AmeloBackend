from rest_framework import permissions

class IsGestorOnly(permissions.BasePermission):
    """Libera acesso apenas se o usuário for explicitamente um Gestor."""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'GESTOR'
        )

class IsSupervisorOrGestor(permissions.BasePermission):
    """Regra flexível para demandas."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.role == 'GESTOR':
            return True
            
        if request.user.role == 'SUPERVISOR' and request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return True
            
        return False