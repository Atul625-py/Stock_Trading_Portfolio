# Generated by Django 5.1.1 on 2024-10-18 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(default='./static/stock/images/profile.jpg', upload_to=''),
        ),
    ]
