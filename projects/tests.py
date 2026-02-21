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

    def _create_project(self, name='My Model', **kwargs):
        data = {
            'name': name,
            'project_type': 'builder',
            'steps': [],
            'connections': [],
            'guide': [],
            'node_positions': {},
            **kwargs,
        }
        return self.client.post('/api/projects/', data, format='json')

    # List
    def test_list_own_projects(self):
        Project.objects.create(owner=self.user, name='P1')
        Project.objects.create(owner=self.other_user, name='P2')
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'P1')

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Create
    def test_create_project(self):
        response = self._create_project('Assembly Guide')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Assembly Guide')
        self.assertIn('id', response.data)

    def test_create_project_with_steps(self):
        response = self._create_project(steps=[SAMPLE_STEP])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['steps'][0]['id'], 'step-1')

    # Retrieve
    def test_get_own_project(self):
        proj = Project.objects.create(owner=self.user, name='Mine')
        response = self.client.get(f'/api/projects/{proj.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mine')

    def test_get_other_user_project_returns_404(self):
        proj = Project.objects.create(owner=self.other_user, name='NotMine')
        response = self.client.get(f'/api/projects/{proj.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Update
    def test_update_project(self):
        proj = Project.objects.create(owner=self.user, name='Old')
        response = self.client.put(
            f'/api/projects/{proj.id}/',
            {
                'name': 'New',
                'project_type': 'upload',
                'steps': [],
                'connections': [],
                'guide': [],
                'node_positions': {},
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New')

    def test_partial_update_project(self):
        proj = Project.objects.create(owner=self.user, name='Old')
        response = self.client.patch(
            f'/api/projects/{proj.id}/', {'name': 'Patched'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Patched')

    # Delete
    def test_delete_project(self):
        proj = Project.objects.create(owner=self.user, name='ToDelete')
        response = self.client.delete(f'/api/projects/{proj.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=proj.id).exists())

    def test_delete_other_user_project_returns_404(self):
        proj = Project.objects.create(owner=self.other_user, name='NotMine')
        response = self.client.delete(f'/api/projects/{proj.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(pk=proj.id).exists())

