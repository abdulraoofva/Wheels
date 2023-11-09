# Generated by Django 4.2.6 on 2023-11-06 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_carowner_proposal_status_carowner_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carowner',
            name='is_active',
        ),
        migrations.AddField(
            model_name='carowner',
            name='proposal_status',
            field=models.CharField(default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='carowner',
            name='contact_number',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='carowner',
            name='document',
            field=models.FileField(upload_to='car_owner_documents/'),
        ),
        migrations.AlterField(
            model_name='carowner',
            name='location',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='carowner',
            name='venue_name',
            field=models.CharField(max_length=100),
        ),
    ]
