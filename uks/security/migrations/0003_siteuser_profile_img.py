# Generated by Django 3.1.5 on 2021-01-26 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0002_siteuser_repositories'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteuser',
            name='profile_img',
            field=models.ImageField(default='profile_default.png', upload_to=''),
        ),
    ]
