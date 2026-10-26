from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from main.models import Condominio, Demanda, Profissional, Supervisor


User = get_user_model()


class SupervisorAndProfessionalPermissionTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='test-pass')
        self.manager.role = 'GESTOR'
        self.manager.save(update_fields=['role'])

        self.other_manager = User.objects.create_user(
            username='other-manager', password='test-pass'
        )
        self.other_manager.role = 'GESTOR'
        self.other_manager.save(update_fields=['role'])

        self.supervisor_user = User.objects.create_user(
            username='supervisor', password='test-pass'
        )
        self.supervisor_user.role = 'SUPERVISOR'
        self.supervisor_user.save(update_fields=['role'])
        self.supervisor = Supervisor.objects.create(
            usuario=self.supervisor_user,
            gestor=self.manager,
        )

        self.assigned_condo = self._create_condo(self.manager, 'Carteira')
        self.unassigned_condo = self._create_condo(self.manager, 'Fora da carteira')
        self.foreign_condo = self._create_condo(self.other_manager, 'Outro gestor')
        self.supervisor.condominios.add(self.assigned_condo)

    @staticmethod
    def _create_condo(owner, name):
        return Condominio.objects.create(
            usuario=owner,
            nome=name,
            endereco='Rua de teste, 10',
            cidade='São Paulo',
            estado='SP',
            cep='01000-000',
        )

    def test_supervisor_sees_all_manager_condos_but_not_other_managers(self):
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.get('/api/v1/condominios/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual({item['id'] for item in response.data}, {
            self.assigned_condo.id,
            self.unassigned_condo.id,
        })
        self.assertNotIn(self.foreign_condo.id, {item['id'] for item in response.data})

    def test_supervisor_created_condominium_belongs_to_manager_and_is_assigned(self):
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.post('/api/v1/condominios/', {
            'nome': 'Novo condomínio',
            'endereco': 'Rua Nova, 20',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '02000-000',
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        condo = Condominio.objects.get(pk=response.data['id'])
        self.assertEqual(condo.usuario, self.manager)
        self.assertTrue(self.supervisor.condominios.filter(pk=condo.pk).exists())

    def test_supervisor_can_edit_and_delete_demands_of_their_manager(self):
        demand = Demanda.objects.create(
            condominio=self.unassigned_condo,
            titulo='Título inicial',
            descricao='Descrição',
            criadoPor=self.manager,
        )
        self.client.force_authenticate(self.supervisor_user)

        edit_response = self.client.patch(
            f'/api/v1/demandas/{demand.id}/',
            {'titulo': 'Título revisado'},
            format='json',
        )
        self.assertEqual(edit_response.status_code, 200, edit_response.data)
        demand.refresh_from_db()
        self.assertEqual(demand.titulo, 'Título revisado')

        delete_response = self.client.delete(f'/api/v1/demandas/{demand.id}/')
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Demanda.objects.filter(pk=demand.pk).exists())

    def test_supervisor_cannot_read_or_mutate_other_managers_demands(self):
        demand = Demanda.objects.create(
            condominio=self.foreign_condo,
            titulo='Demanda privada de outro gestor',
            descricao='Descrição',
            criadoPor=self.other_manager,
        )
        self.client.force_authenticate(self.supervisor_user)

        list_response = self.client.get('/api/v1/demandas/')
        self.assertEqual(list_response.status_code, 200)
        self.assertNotIn(demand.id, {item['id'] for item in list_response.data})

        detail_response = self.client.get(f'/api/v1/demandas/{demand.id}/')
        self.assertEqual(detail_response.status_code, 404)

        edit_response = self.client.patch(
            f'/api/v1/demandas/{demand.id}/',
            {'titulo': 'Alteração indevida'},
            format='json',
        )
        self.assertEqual(edit_response.status_code, 404)

    def test_supervisor_cannot_create_demand_for_another_manager(self):
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.post('/api/v1/demandas/', {
            'condominio': self.foreign_condo.id,
            'titulo': 'Criação cruzada',
            'descricao': 'Não deve ser permitida',
            'urgencia': 'URGENTE',
        }, format='json')

        self.assertEqual(response.status_code, 403)

    def test_supervisor_dashboard_only_counts_demands_of_their_manager(self):
        Demanda.objects.create(
            condominio=self.assigned_condo,
            titulo='Demanda do meu gestor',
            descricao='Descrição',
            criadoPor=self.manager,
            status='PENDENTE',
        )
        Demanda.objects.create(
            condominio=self.foreign_condo,
            titulo='Demanda de outro gestor',
            descricao='Descrição',
            criadoPor=self.other_manager,
            status='CONCLUIDA',
            urgencia='URGENTE',
        )
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.get('/api/v1/dashboard/summary/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['abertas'], 1)
        self.assertEqual(response.data['concluidas'], 0)
        self.assertEqual(response.data['urgentes'], 0)

    def test_supervisor_can_create_professionals_shared_with_manager(self):
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.post('/api/v1/profissionais/', {
            'nome': 'Profissional A',
            'especialidade': 'Elétrica',
            'telefone': '11999990000',
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        professional = Profissional.objects.get(pk=response.data['id'])
        self.assertEqual(professional.usuario, self.manager)

        demand = Demanda.objects.create(
            condominio=self.assigned_condo,
            titulo='Demanda para atribuição',
            descricao='Descrição',
            criadoPor=self.manager,
        )
        assignment_response = self.client.patch(
            f'/api/v1/demandas/{demand.id}/',
            {'profissionalAcionado': professional.id},
            format='json',
        )
        self.assertEqual(assignment_response.status_code, 200, assignment_response.data)
        demand.refresh_from_db()
        self.assertEqual(demand.profissionalAcionado, professional)

        self.client.force_authenticate(self.manager)
        manager_list = self.client.get('/api/v1/profissionais/')
        self.assertEqual(manager_list.status_code, 200)
        self.assertEqual(manager_list.data[0]['id'], professional.id)

    def test_completed_demand_metric_counts_by_professional(self):
        professional = Profissional.objects.create(
            usuario=self.manager,
            nome='Profissional B',
            especialidade='Hidráulica',
            telefone='11999990001',
        )
        Demanda.objects.create(
            condominio=self.assigned_condo,
            titulo='Concluída',
            descricao='Descrição',
            criadoPor=self.manager,
            profissionalAcionado=professional,
            status='CONCLUIDA',
        )
        Demanda.objects.create(
            condominio=self.assigned_condo,
            titulo='Aberta',
            descricao='Descrição',
            criadoPor=self.manager,
            profissionalAcionado=professional,
            status='PENDENTE',
        )
        Demanda.objects.create(
            condominio=self.foreign_condo,
            titulo='Concluída de outro gestor',
            descricao='Descrição',
            criadoPor=self.other_manager,
            profissionalAcionado=professional,
            status='CONCLUIDA',
        )
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.get('/api/v1/dashboard/metricas-profissionais/')

        self.assertEqual(response.status_code, 200)
        result = next(item for item in response.data if item['id'] == professional.id)
        self.assertEqual(result['demandas_concluidas'], 1)

    def test_supervisor_cannot_assign_professional_from_another_manager(self):
        professional = Profissional.objects.create(
            usuario=self.other_manager,
            nome='Profissional externo',
            especialidade='Elétrica',
            telefone='11999990002',
        )
        demand = Demanda.objects.create(
            condominio=self.assigned_condo,
            titulo='Demanda',
            descricao='Descrição',
            criadoPor=self.manager,
        )
        self.client.force_authenticate(self.supervisor_user)

        response = self.client.patch(
            f'/api/v1/demandas/{demand.id}/',
            {'profissionalAcionado': professional.id},
            format='json',
        )

        self.assertEqual(response.status_code, 403)
