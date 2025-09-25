from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import Profile, User
from ..serializers import ProfileSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def public_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    serializer = ProfileSerializer(user.profile, context={"request": request})
    return Response(serializer.data)

@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def me_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "GET":
        return Response(ProfileSerializer(profile, context={"request": request}).data)

    partial = request.method == "PATCH"
    ser = ProfileSerializer(profile, data=request.data, partial=partial, context={"request": request})
    if ser.is_valid():
        ser.save()
        return Response(ser.data)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)