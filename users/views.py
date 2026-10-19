
import os
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UsersSerializer, RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UsersSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        credential = request.data.get("credential")

        if not isinstance(credential, str) or not credential:
            return Response(
                {"detail": "Google credential is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")

        if not client_id:
            return Response(
                {"detail": "Google login is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            google_user = id_token.verify_oauth2_token(
                credential,
                GoogleRequest(),
                audience=client_id
            )
        except  Exception:
            return Response(
                {"detail": "Invalid or expired Google credential."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        google_sub = google_user.get("sub")
        email = google_user.get("email", "").strip().lower()
        email_verified = google_user.get("email_verified", False)
        name = google_user.get("name") or email.split("@")[0]

        if not google_sub or not email or email_verified is not True:
            return Response(
                {"detail": "A verified Google email is required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = User.objects.get(google_sub=google_sub)
        except User.DoesNotExist:
            user = None

        if user is None:
            # Never automatically link a Google identity to an existing
            # password account based only on a matching email address.
            if User.objects.filter(email__iexact=email).exists():
                return Response(
                    {
                        "detail": (
                            "An account with this email already exists. "
                            "Log in using that account before linking Google."
                        )
                    },
                    status=status.HTTP_409_CONFLICT
                )

            username = f"google_{uuid.uuid4().hex}"

            user = User.objects.create_user(
                username=username,
                email=email,
                name=name[:100],
                password=None,
                google_sub=google_sub,
                role="adventure_seeker"
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UsersSerializer(user).data
        }, status=status.HTTP_200_OK)
