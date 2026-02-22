from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Project


SAMPLE_STEP = {
    'id': 'step-1',
    'title': 'Intro',
    'description': 'First step',
    'modelPath': 'box',
    'cameraPosition': {'x': 5, 'y': 5, 'z': 5},
    'shapeType': 'cube',
}


def _project_payload(name='My Model', **overrides):
    """Build a flat project payload matching the serializer contract."""
    return {
        'name': name,
        'projectType': 'builder',
        'steps': [],
        'connections': [],
        'guide': [],
        'nodePositions': {},
        **overrides,
    }


class ProjectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass'
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass'
        )
        self.client.force_authenticate(user=self.user)

    def _create_project(self, name='My Model', **overrides):
        data = _project_payload(name, **overrides)
        return self.client.post('/api/projects', data, format='json')

    # ------------------------------------------------------------------
    # List  GET /api/projects
    # ------------------------------------------------------------------

    def test_list_own_projects(self):
        Project.objects.create(owner=self.user, name='P1')
        Project.objects.create(owner=self.other_user, name='P2')
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'P1')

    def test_list_has_flat_shape(self):
        Project.objects.create(owner=self.user, name='P1')
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertIn('id', item)
        self.assertIn('name', item)
        self.assertIn('projectType', item)
        self.assertIn('nodePositions', item)
        self.assertIn('lastModified', item)
        self.assertIsInstance(item['lastModified'], int)
        # must NOT have the nested 'project' key
        self.assertNotIn('project', item)

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_also_works_with_trailing_slash(self):
        """Django serves /api/projects/ via the include() prefix too."""
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # Create  POST /api/projects
    # ------------------------------------------------------------------

    def test_create_project(self):
        response = self._create_project('Assembly Guide')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Assembly Guide')
        self.assertIn('id', response.data)

    def test_create_project_id_is_server_assigned(self):
        response = self._create_project()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(response.data['id'], 0)

    def test_create_project_with_steps(self):
        response = self._create_project(steps=[SAMPLE_STEP])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['steps'][0]['id'], 'step-1')

    def test_create_project_camel_case_response(self):
        response = self._create_project(projectType='upload', projectModelUrl='https://example.com/m.glb')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['projectType'], 'upload')
        self.assertEqual(response.data['projectModelUrl'], 'https://example.com/m.glb')

    def test_create_project_null_model_url(self):
        response = self._create_project(projectModelUrl=None)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['projectModelUrl'])

    # ------------------------------------------------------------------
    # Retrieve  GET /api/projects/:id
    # ------------------------------------------------------------------

    def test_get_own_project(self):
        proj = Project.objects.create(owner=self.user, name='Mine')
        response = self.client.get(f'/api/projects/{proj.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mine')

    def test_get_other_user_project_returns_404(self):
        proj = Project.objects.create(owner=self.other_user, name='NotMine')
        response = self.client.get(f'/api/projects/{proj.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------
    # Replace  PUT /api/projects/:id
    # ------------------------------------------------------------------

    def test_update_project(self):
        proj = Project.objects.create(owner=self.user, name='Old')
        data = _project_payload('New', projectType='upload')
        response = self.client.put(f'/api/projects/{proj.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New')
        self.assertEqual(response.data['projectType'], 'upload')

    def test_update_replaces_node_positions(self):
        proj = Project.objects.create(owner=self.user, name='P')
        payload = _project_payload('P', nodePositions={'step-1': {'x': 10, 'y': 20}})
        response = self.client.put(f'/api/projects/{proj.id}', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nodePositions']['step-1']['x'], 10)

    # ------------------------------------------------------------------
    # Delete  DELETE /api/projects/:id
    # ------------------------------------------------------------------

    def test_delete_project(self):
        proj = Project.objects.create(owner=self.user, name='ToDelete')
        response = self.client.delete(f'/api/projects/{proj.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=proj.id).exists())

    def test_delete_other_user_project_returns_404(self):
        proj = Project.objects.create(owner=self.other_user, name='NotMine')
        response = self.client.delete(f'/api/projects/{proj.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(pk=proj.id).exists())

    # ------------------------------------------------------------------
    # Public  GET /api/projects/:id/public
    # ------------------------------------------------------------------

    def test_public_get_project(self):
        proj = Project.objects.create(owner=self.user, name='Shared')
        public_client = APIClient()  # no authentication
        response = public_client.get(f'/api/projects/{proj.id}/public')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Shared')
        self.assertIn('nodePositions', response.data)
        self.assertIn('lastModified', response.data)

    def test_public_get_missing_project_returns_404(self):
        public_client = APIClient()
        response = public_client.get('/api/projects/999999/public')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

