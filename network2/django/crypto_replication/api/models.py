from django.db import models

# Create your models here.

# Models constants
DEFAULT_VARCHAR_SIZE = 255

class Certificate(models.Model):
    """
    certificates
    """

    class Meta:
        db_table = 'certificates'

    owner = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    common_name = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    serial_number = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    fingerprint = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
    cert_b64 = models.CharField(max_length=5000, null=True, blank=True)
    expiration_date = models.CharField(max_length=DEFAULT_VARCHAR_SIZE, null=True, blank=True)
