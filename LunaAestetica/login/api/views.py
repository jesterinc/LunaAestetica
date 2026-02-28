# login/urls.py
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from login.models import Users

from login.api.serializers import UserRegistrationSerializer

import traceback

class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        # Prendiamo email e password dal JSON
        email = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')

        # Autentichiamo (abbiamo visto che da shell funziona!)
        user = authenticate(username=email, password=password)

        if user:
            # Creiamo il token. Se la tabella non esiste, qui darà 500
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Credenziali non valide"}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordRecoverView(APIView):
  
  def post(self, request):
        
    email = request.data.get('email')        
    return Response({"message": "Se l'email esiste, riceverai le istruzioni."}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
  serializer_class = UserRegistrationSerializer
  permission_classes = [AllowAny] # Permette a chiunque di registrarsi

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)

    if serializer.is_valid():

      user = serializer.save()
      profile = user.users_User 
      return Response({
        "message": "Utente registrato con successo",
        "token": profile.token,
        "username": user.username
      }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    