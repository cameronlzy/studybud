from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers import RoomSerializer
from base.models import Room

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def rooms(request):
    if request.method == 'GET':
        qs = Room.objects.all()
        serializer = RoomSerializer(qs, many=True)
        return Response(serializer.data)

    # CREATE
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = RoomSerializer(room, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    room.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)