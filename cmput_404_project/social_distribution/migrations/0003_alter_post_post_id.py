# Generated by Django 3.2.12 on 2022-02-22 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_distribution', '0002_alter_author_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_id',
            field=models.SlugField(max_length=64, primary_key=True, serialize=False, unique=True),
        ),
    ]
