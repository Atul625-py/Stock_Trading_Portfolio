# Generated by Django 5.1.1 on 2024-10-21 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0005_alter_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='password_hash',
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='Trader', max_length=50, unique=True),
        ),
    ]
