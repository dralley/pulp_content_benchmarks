# Generated by Django 2.0.7 on 2018-07-09 17:43

from django.db import migrations, models
import django.db.models.deletion
import inherited.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artifact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('file', inherited.models.ArtifactFileField(max_length=255, upload_to=inherited.models.Artifact.storage_path)),
                ('size', models.IntegerField()),
                ('md5', models.CharField(db_index=True, max_length=32)),
                ('sha1', models.CharField(db_index=True, max_length=40)),
                ('sha224', models.CharField(db_index=True, max_length=56)),
                ('sha256', models.CharField(db_index=True, max_length=64, unique=True)),
                ('sha384', models.CharField(db_index=True, max_length=96, unique=True)),
                ('sha512', models.CharField(db_index=True, max_length=128, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('type', models.TextField(default=None)),
            ],
            options={
                'verbose_name_plural': 'content',
            },
        ),
        migrations.CreateModel(
            name='ContentArtifact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('relative_path', models.CharField(max_length=256)),
                ('artifact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='inherited.Artifact')),
            ],
        ),
        migrations.CreateModel(
            name='FileContent',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inherited.Content')),
                ('relative_path', models.TextField()),
                ('digest', models.TextField()),
            ],
            bases=('inherited.content',),
        ),
        migrations.AddField(
            model_name='contentartifact',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inherited.Content'),
        ),
        migrations.AddField(
            model_name='content',
            name='artifacts',
            field=models.ManyToManyField(through='inherited.ContentArtifact', to='inherited.Artifact'),
        ),
        migrations.AlterUniqueTogether(
            name='filecontent',
            unique_together={('relative_path', 'digest')},
        ),
        migrations.AlterUniqueTogether(
            name='contentartifact',
            unique_together={('content', 'relative_path')},
        ),
    ]
