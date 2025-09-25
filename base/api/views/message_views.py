# base/api/message_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import Message
from ..serializers import MessageSerializer

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def message_detail(request, pk):
    msg = get_object_or_404(Message, pk=pk)

    if request.method == 'GET':
        return Response(MessageSerializer(msg).data)

    # DELETE only by author or staff
    if not (request.user.is_superuser or request.user == msg.user):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    msg.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)