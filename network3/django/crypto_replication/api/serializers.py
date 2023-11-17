from rest_framework import serializers
from crypto_replication.api.models import *


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'owner', 'common_name', 'serial_number', 'fingerprint', 'cert_b64', 'expiration_date']