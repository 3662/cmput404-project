# Generated by Django 3.2.12 on 2022-02-22 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_distribution', '0003_alter_post_post_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='post_id',
            new_name='id',
        ),
        migrations.RemoveField(
            model_name='author',
            name='user_id',
        ),
        migrations.AlterField(
            model_name='author',
            name='id',
            field=models.SlugField(max_length=64, primary_key=True, serialize=False, unique=True),
        ),
    ]
