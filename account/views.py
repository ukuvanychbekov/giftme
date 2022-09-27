from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from .models import User, UserProfile, Subscription
from .serializer import RegisterSerilaliser, UserProfileSerializer, SubscriptionSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerilaliser

    def perform_create(self, serializer):
        user = serializer.save()
        if user:
            UserProfile.objects.create(user=user)

class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = SessionAuthentication, TokenAuthentication



class SubscribeView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, ]
    serializer_class = SubscriptionSerializer

    def get(self, request, profile_id):
        profile = get_object_or_404(UserProfile, id=profile_id)
        try:
            Subscription.objects.create(followed=profile, follower=request.user.profile)
        except IntegrityError:
            subscription = Subscription.objects.get(followed=profile, follower=request.user.profile)
            subscription.delete()
            data = {'message': f'You successfully unsubscribed from {profile.user.username}'}
            this_status = status.HTTP_204_NO_CONTENT
        else:
            data = {'message': f'You successfully subscribed to {profile.user.username}'}
            this_status = status.HTTP_201_CREATED

        return Response(data, status=this_status)