# Generated by Django 3.1.6 on 2022-02-22 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0005_auto_20220222_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='display_name',
            field=models.CharField(default=None, max_length=20, primary_key=True, serialize=False),
        ),
    ]
