# Generated by Django 3.2.12 on 2022-04-03 07:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('social_distribution', '0004_inboxitem_date_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_author_id', models.UUIDField(default=None, editable=False, null=True)),
                ('source_author_url', models.URLField(editable=False, max_length=1000)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('target_author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Follower',
            },
        ),
    ]
