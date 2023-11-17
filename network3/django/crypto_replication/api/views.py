from rest_framework import viewsets
from crypto_replication.api.models import *
from crypto_replication.api.serializers import *

# Create your views here.

class CertificateViewSet(viewsets.ModelViewSet):

    queryset = Certificate.objects.all().order_by('id')
    serializer_class = CertificateSerializer
    http_method_names = ['get', 'post', 'head', 'patch','delete']
