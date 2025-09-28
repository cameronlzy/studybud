from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers import RoomSerializer
from base.models import Room, Message

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

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def room_messages(request, pk):
    """
    Paginated messages for a room.
    Query params:
      - offset (int, default 0)
      - limit  (int, default 10)
    Returns newest-first.
    """
    try:
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 10))
        limit = max(1, min(limit, 100))  # guardrails
    except ValueError:
        offset, limit = 0, 10

    qs = (Message.objects
          .filter(room_id=pk)
          .select_related("user__profile")
          .order_by("-created"))

    total = qs.count()
    items = list(qs[offset:offset+limit])

    data = []
    for m in items:
        img = getattr(getattr(m.user, "profile", None), "profile_img", None)
        data.append({
            "id": m.id,
            "user": m.user_id,
            "username": m.user.username,
            "body": m.body,
            "created": m.created.isoformat(),
            "profile_img": (img.url if img else None),
        })

    return Response({
        "messages": data,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + len(items) < total),
    })