# Generated by Django 5.1.1 on 2024-10-22 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_alter_portfolio_portfolio_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='profile_pictures/profile.jpg', upload_to='profile_pictures/'),
        ),
    ]
