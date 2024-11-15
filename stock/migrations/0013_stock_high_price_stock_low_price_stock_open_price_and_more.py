# Generated by Django 5.1.1 on 2024-11-01 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0012_alter_portfolio_portfolio_id_alter_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='high_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='low_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='open_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='previous_close',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
