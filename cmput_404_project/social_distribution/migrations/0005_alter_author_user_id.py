# Generated by Django 3.2.12 on 2022-02-22 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_distribution', '0004_alter_author_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='user_id',
            field=models.CharField(max_length=64, primary_key=True, serialize=False, unique=True),
        ),
    ]
