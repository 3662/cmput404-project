# Generated by Django 3.2.12 on 2022-02-22 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_distribution', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='user_id',
            field=models.SlugField(max_length=64, unique=True),
        ),
    ]