from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BlockRequest
from .permissions import IsAuthenticatedToRead
from .serializers import BlockRequestSerializer
from .utils import get_ip_address, send_notification


class BlockRequestListView(APIView):
    permission_classes = (IsAuthenticatedToRead,)

    def dispatch(self, *args, **kwargs):
        return super(BlockRequestListView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request):
        domain = request.GET.get('domain')
        resolved = request.GET.get('resolved')
        block_requests = BlockRequest.objects.all()
        if domain is not None:
            block_requests = block_requests.filter(website__domain__icontains=domain)
        if resolved is not None:
            try:
                resolved = bool(int(resolved))
            except TypeError:
                return Response({'errors': 'incorrect type of parameter resolved. Need to be 0 or 1.'},
                                status=status.HTTP_400_BAD_REQUEST)
            block_requests = block_requests.exclude(is_accepted__isnull=resolved)
        block_requests_serializer = BlockRequestSerializer(block_requests, many=True)
        return Response(block_requests_serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        ip = get_ip_address(request)
        request.data['ip'] = ip
        block_request_serializer = BlockRequestSerializer(data=request.data, context={'user': request.user})
        if block_request_serializer.is_valid():
            block_request_serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(block_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlockRequestDetailView(APIView):
    permission_classes = (IsAdminUser,)

    def dispatch(self, *args, **kwargs):
        kwargs['block_request'] = get_object_or_404(BlockRequest, pk=kwargs.pop('pk', None))
        return super(BlockRequestDetailView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, block_request):
        block_request_serializer = BlockRequestSerializer(block_request)
        return Response(block_request_serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def patch(request, block_request):
        old_is_accepted = block_request.is_accepted
        block_request_serializer = BlockRequestSerializer(block_request, data=request.data, partial=True,
                                                          context={'user': request.user})
        if block_request_serializer.is_valid():
            block_request_serializer.save()
            if old_is_accepted is None and block_request.is_accepted is not None:
                send_notification(block_request)
            return Response(block_request_serializer.data, status=status.HTTP_200_OK)
        return Response(block_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request, block_request):
        old_is_accepted = block_request.is_accepted
        block_request_serializer = BlockRequestSerializer(block_request, data=request.data,
                                                          context={'user': request.user})
        if block_request_serializer.is_valid():
            block_request_serializer.save()
            if old_is_accepted is None and block_request.is_accepted is not None:
                send_notification(block_request)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(block_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, block_request):
        block_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
