# Generated by Django 5.1.1 on 2024-10-21 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0006_remove_user_password_hash_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell'), ('bs', 'bought_then_sold')], default='buy', max_length=4),
        ),
    ]