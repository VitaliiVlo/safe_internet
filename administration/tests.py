import json

from django.contrib.auth.models import User
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APITestCase

from .models import BlockRequest, Website
from .serializers import BlockRequestSerializer


class GetAllRequestsTest(APITestCase):
    """ Test module for GET all block requests API """

    def setUp(self):
        user = mixer.blend(User, is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=user)
        mixer.cycle(10).blend(BlockRequest, is_accepted=mixer.sequence(True, False, None))

    def test_get_all_requests(self):
        response = self.client.get(reverse('block_request_list'))
        block_requests = BlockRequest.objects.all()
        serializer = BlockRequestSerializer(block_requests, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllRequestsParamTest(APITestCase):
    """ Test module for GET all block requests API with get params """

    def setUp(self):
        user = mixer.blend(User, is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=user)
        mixer.cycle(10).blend(BlockRequest, is_accepted=mixer.sequence(True, False, None))

    def test_get_all_requests_param(self):
        response = self.client.get(reverse('block_request_list'), {'resolved': 0})
        block_requests = BlockRequest.objects.exclude(is_accepted__isnull=False)
        serializer = BlockRequestSerializer(block_requests, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleRequestTest(APITestCase):
    """ Test module for GET single block request API """

    def setUp(self):
        user = mixer.blend(User, is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=user)
        self.block_request = mixer.blend(BlockRequest)

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
            'description': mixer.faker.text(max_nb_chars=500),
            'email': mixer.faker.email(),
            'ip': mixer.faker.ipv4(),
            'is_accepted': True,
            'website': {'domain': mixer.faker.url()}
        }

        self.invalid_payload = {
            'description': mixer.faker.text(max_nb_chars=500),
            'email': mixer.faker.text(),
            'ip': mixer.faker.ipv4(),
            'is_accepted': mixer.faker.null_boolean(),
            'website': {'domain': mixer.faker.text()}
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

        block_request = BlockRequest.objects.first()
        self.assertEqual(self.valid_payload['description'], block_request.description)
        self.assertEqual(self.valid_payload['email'], block_request.email)
        self.assertEqual(None, block_request.is_accepted)
        self.assertEqual(self.valid_payload['website']['domain'], block_request.website.domain)

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
        user = mixer.blend(User, is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=user)

        self.block_request = mixer.blend(BlockRequest)
        self.valid_payload = {
            'description': mixer.faker.text(max_nb_chars=500),
            'email': mixer.faker.email(),
            'ip': mixer.faker.ipv4(),
            'is_accepted': mixer.faker.null_boolean(),
            'website': {'domain': mixer.faker.url()}
        }
        self.invalid_payload = {
            'description': mixer.faker.text(max_nb_chars=500),
            'email': mixer.faker.text(),
            'ip': mixer.faker.ipv4(),
            'is_accepted': mixer.faker.null_boolean(),
            'website': {'domain': mixer.faker.text()}
        }

    def test_valid_update_request(self):
        response = self.client.put(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        block_request = BlockRequest.objects.first()
        self.assertEqual(self.valid_payload['description'], block_request.description)
        self.assertEqual(self.valid_payload['email'], block_request.email)
        self.assertEqual(self.valid_payload['ip'], block_request.ip)
        self.assertEqual(self.valid_payload['is_accepted'], block_request.is_accepted)
        self.assertEqual(self.valid_payload['website']['domain'], block_request.website.domain)

    def test_invalid_update_request(self):
        response = self.client.put(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        block_request = BlockRequest.objects.first()
        self.assertEqual(self.block_request.description, block_request.description)
        self.assertEqual(self.block_request.email, block_request.email)
        self.assertEqual(self.block_request.ip, block_request.ip)
        self.assertEqual(self.block_request.website.domain, block_request.website.domain)


class PartialUpdateSingleRequestTest(APITestCase):
    """ Test module for partial updating an existing block request record """

    def setUp(self):
        user = mixer.blend(User, is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=user)

        self.block_request = mixer.blend(BlockRequest)

        self.valid_payload = {
            'email': mixer.faker.email(),
            'website': {'domain': mixer.faker.url()}
        }
        self.invalid_payload = {
            'email': mixer.faker.text(),
            'website': {'domain': mixer.faker.text()}
        }

    def test_valid_partial_update_request(self):
        response = self.client.patch(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        block_request = BlockRequest.objects.first()
        self.assertEqual(self.valid_payload['email'], block_request.email)
        self.assertEqual(self.valid_payload['website']['domain'], block_request.website.domain)

    def test_invalid_partial_update_request(self):
        response = self.client.patch(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        block_request = BlockRequest.objects.first()
        self.assertEqual(self.block_request.email, block_request.email)
        self.assertEqual(self.block_request.website.domain, block_request.website.domain)


class DeleteSingleRequestTest(APITestCase):
    """ Test module for deleting an existing block request record """

    def setUp(self):
        user = mixer.blend(User, is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=user)

        self.block_request = mixer.blend(BlockRequest)

    def test_valid_delete_request(self):
        response = self.client.delete(
            reverse('block_request_detail', kwargs={'pk': self.block_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlockRequest.objects.count(), 0)

    def test_invalid_delete_request(self):
        response = self.client.delete(
            reverse('block_request_detail', kwargs={'pk': 3000}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(BlockRequest.objects.count(), 1)
