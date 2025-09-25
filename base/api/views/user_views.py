from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserSerializer

User = get_user_model()

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def users(request):
    if request.method == 'GET':
        data = UserSerializer(User.objects.all(), many=True).data
        return Response(data)

    # POST (register)
    ser = UserSerializer(data=request.data)
    if ser.is_valid():
        # If your serializer includes password: make sure it hashes it in create()
        user = ser.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Only the user themselves (or staff) can modify/delete
    if request.method in ['PATCH', 'DELETE'] and not (request.user.is_superuser or request.user == user):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return Response(UserSerializer(user).data)

    if request.method == 'PATCH':
        ser = UserSerializer(user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)