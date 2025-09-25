from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import Topic
from ..serializers import TopicSerializer

@api_view(['GET'])
def topic_detail(request, pk):
    """Get a single topic by ID"""
    topic = get_object_or_404(Topic, pk=pk)
    serializer = TopicSerializer(topic)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def topic_create(request):
    """Create a topic (staff only)"""
    if not request.user.is_superuser:
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    serializer = TopicSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)