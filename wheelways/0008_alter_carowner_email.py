# Generated by Django 4.2.6 on 2023-11-06 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_carowner_id_alter_carowner_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carowner',
            name='email',
            field=models.EmailField(max_length=254, primary_key=True, serialize=False, unique=True),
        ),
    ]