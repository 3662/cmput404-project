# Generated by Django 3.2.12 on 2022-03-09 02:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('social_distribution', '0004_auto_20220308_0111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='recepient',
            field=models.UUIDField(choices=[(uuid.UUID('6f9251fe-d195-48f5-8443-6c40259bd6d9'), 'try this'), (uuid.UUID('ab59474d-8c2e-404a-bd34-dce351980765'), 'try try'), (uuid.UUID('6e93d092-79ed-4d05-a5bb-2b205145f215'), 'Jejoon Ryu'), (uuid.UUID('518f649b-1e65-480a-a128-fb176f031df7'), 'Felipe Rodriguez')], default=None, null=True),
        ),
        migrations.CreateModel(
            name='InboxItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_type', models.CharField(choices=[('POST', 'Post'), ('COMMENT', 'Comment'), ('FOLLOW', 'Follow'), ('LIKE', 'like')], default='POST', max_length=7)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('inbox', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_distribution.inbox')),
            ],
        ),
    ]
