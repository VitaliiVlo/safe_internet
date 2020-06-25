import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import BlockRequest, Website
from .serializers import BlockRequestSerializer


class GetAllRequestsTest(APITestCase):
    """ Test module for GET all block requests API """

    def setUp(self):
        user = User.objects.create_superuser('test', 'test@example.com', 'test')
        self.client.force_authenticate(user=user)
        website = Website.objects.create(domain='http://example.com')
        website2 = Website.objects.create(domain='http://example2.com')
        BlockRequest.objects.create(description='test desc 1', email='test1@mail.com',
                                    ip='192.0.0.1', is_accepted=None, website=website)
        BlockRequest.objects.create(description='test desc 2', email='test2@mail.com',
                                    ip='192.0.0.2', is_accepted=None, website=website2)
        BlockRequest.objects.create(description='test desc 3', email='test3@mail.com',
                                    ip='192.0.0.3', is_accepted=None, website=website2)

    def test_get_all_requests(self):
        response = self.client.get(reverse('block_request_list'))
        block_requests = BlockRequest.objects.all()
        serializer = BlockRequestSerializer(block_requests, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleRequestTest(APITestCase):
    """ Test module for GET single block request API """

    def setUp(self):
        user = User.objects.create_superuser('test', 'test@example.com', 'test')
        self.client.force_authenticate(user=user)
        website = Website.objects.create(domain='http://example.com')
        self.block_request = BlockRequest.objects.create(description='test desc 1', email='test1@mail.com',
                                                         ip='192.0.0.1', is_accepted=None, website=website)

    def test_get_valid_single_request(self):
        response = self.client.get(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}))
        block_request = BlockRequest.objects.get(pk=self.block_request.pk)
        serializer = BlockRequestSerializer(block_request)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_request(self):
        response = self.client.get(
            reverse('block_request_detail', kwargs={'pk': 3000}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateNewRequestTest(APITestCase):
    """ Test module for inserting a new block request """

    def setUp(self):
        self.valid_payload = {
            'description': 'test desc 1',
            'email': 'test1@mail.com',
            'ip': '192.0.0.1',
            'is_accepted': None,
            'website': {'domain': 'http://example.com'}
        }

        self.invalid_payload = {
            'description': 'test desc 1',
            'email': 'test1@mail.com',
            'ip': '192.0.1',
            'is_accepted': None,
            'website': {'domain': ''}
        }

    def test_create_valid_request(self):
        response = self.client.post(
            reverse('block_request_list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlockRequest.objects.count(), 1)
        self.assertEqual(Website.objects.count(), 1)

    def test_create_invalid_request(self):
        response = self.client.post(
            reverse('block_request_list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BlockRequest.objects.count(), 0)
        self.assertEqual(Website.objects.count(), 0)


class UpdateSingleRequestTest(APITestCase):
    """ Test module for updating an existing block request record """

    def setUp(self):
        user = User.objects.create_superuser('test', 'test@example.com', 'test')
        self.client.force_authenticate(user=user)
        website = Website.objects.create(domain='http://example.com')
        self.block_request = BlockRequest.objects.create(description='test desc 1', email='test1@mail.com',
                                                         ip='192.0.0.1', is_accepted=None, website=website)
        self.valid_payload = {
            'description': 'test',
            'email': 'test2@mail.com',
            'ip': '192.0.0.22',
            'is_accepted': True,
            'website': {'domain': 'http://example2.com'}
        }

        self.invalid_payload = {
            'description': 'test',
            'email': 'test1@mail.com',
            'ip': '192.0.0',
            'is_accepted': None,
            'website': {'domain': ''}
        }

    def test_valid_update_request(self):
        response = self.client.put(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_update_request(self):
        response = self.client.put(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PartialUpdateSingleRequestTest(APITestCase):
    """ Test module for partial updating an existing block request record """

    def setUp(self):
        user = User.objects.create_superuser('test', 'test@example.com', 'test')
        self.client.force_authenticate(user=user)
        website = Website.objects.create(domain='http://example.com')
        self.block_request = BlockRequest.objects.create(description='test desc 1', email='test1@mail.com',
                                                         ip='192.0.0.1', is_accepted=None, website=website)
        self.valid_payload = {
            'is_accepted': True,
            'website': {'domain': 'http://example2.com'}
        }

        self.invalid_payload = {
            'is_accepted': None,
            'website': {'domain': ''}
        }

    def test_valid_partial_update_request(self):
        response = self.client.patch(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_partial_update_request(self):
        response = self.client.patch(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteSingleRequestTest(APITestCase):
    """ Test module for deleting an existing block request record """

    def setUp(self):
        user = User.objects.create_superuser('test', 'test@example.com', 'test')
        self.client.force_authenticate(user=user)
        website = Website.objects.create(domain='http://example.com')
        self.block_request = BlockRequest.objects.create(description='test desc 1', email='test1@mail.com',
                                                         ip='192.0.0.1', is_accepted=None, website=website)

    def test_valid_delete_request(self):
        response = self.client.delete(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlockRequest.objects.count(), 0)

    def test_invalid_delete_request(self):
        response = self.client.delete(
            reverse('block_request_detail', kwargs={'pk': 3000}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
