# Generated by Django 4.2.6 on 2023-11-06 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_carowner_proposal_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='carowner',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
