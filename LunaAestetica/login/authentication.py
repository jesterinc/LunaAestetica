# login/authentication.py
# login/authentication.py
from rest_framework import authentication
from rest_framework import exceptions
from .models import Users

class CustomTokenAuthentication(authentication.BaseAuthentication):
    
  def authenticate(self, request):
  
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Token '):

      return None

    try:

      token_uuid = auth_header.split(' ')[1]
      profile = Users.objects.select_related('user').get(token=token_uuid, active=True)
      return (profile.user, None)
        
    except (Users.DoesNotExist, IndexError):

      raise exceptions.AuthenticationFailed('Token non valido o scaduto')