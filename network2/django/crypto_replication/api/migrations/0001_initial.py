# Generated by Django 4.2.6 on 2023-11-01 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(blank=True, max_length=255, null=True)),
                ('common_name', models.CharField(blank=True, max_length=255, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=255, null=True)),
                ('fingerprint', models.CharField(blank=True, max_length=255, null=True)),
                ('cert_b64', models.CharField(blank=True, max_length=5000, null=True)),
                ('expiration_date', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'certificates',
            },
        ),
    ]
