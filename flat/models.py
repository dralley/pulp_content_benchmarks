from django.db import models
import uuid
from itertools import chain
from django.db.models import FileField
from django.core.files.uploadedfile import TemporaryUploadedFile
import os
import errno
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage


class FileSystem(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            raise OSError(errno.EEXIST, "File Exists")
        else:
            return name

    def save(self, name, content, max_length=None):
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        try:
            name = self.get_available_name(name, max_length=max_length)
            return self._save(name, content)
        except OSError as e:
            if e.errno == errno.EEXIST:
                return name
            else:
                raise


def get_artifact_path(sha256digest):
    return os.path.join(settings.MEDIA_ROOT, 'artifact', sha256digest[0:2], sha256digest[2:])


class Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        try:
            # if we have a name, use it
            return '<{}: {}>'.format(self._meta.object_name, self.name)
        except AttributeError:
            # if we don't, use the pk
            return '<{}: pk={}>'.format(self._meta.object_name, self.pk)

    def __repr__(self):
        return str(self)


class TemporaryDownloadedFile(TemporaryUploadedFile):
    def __init__(self, file, name=None):
        self.file = file
        if name is None:
            name = getattr(file, 'name', None)
        self.name = name


class ArtifactFileField(FileField):
    def pre_save(self, model_instance, add):
        file = super().pre_save(model_instance, add)
        if file and file._committed and add:
            file._file = TemporaryDownloadedFile(open(file.name, 'rb'))
            file._committed = False
        return super().pre_save(model_instance, add)


class Artifact(Model):

    def storage_path(self, name):
        return get_artifact_path(self.sha256)

    file = ArtifactFileField(blank=False, null=False, upload_to=storage_path, max_length=255)
    size = models.IntegerField(blank=False, null=False)
    md5 = models.CharField(max_length=32, blank=False, null=False, unique=False, db_index=True)
    sha1 = models.CharField(max_length=40, blank=False, null=False, unique=False, db_index=True)
    sha224 = models.CharField(max_length=56, blank=False, null=False, unique=False, db_index=True)
    sha256 = models.CharField(max_length=64, blank=False, null=False, unique=True, db_index=True)
    sha384 = models.CharField(max_length=96, blank=False, null=False, unique=True, db_index=True)
    sha512 = models.CharField(max_length=128, blank=False, null=False, unique=True, db_index=True)

    # All digest fields ordered by algorithm strength.
    DIGEST_FIELDS = (
        'sha512',
        'sha384',
        'sha256',
        'sha224',
        'sha1',
        'md5',
    )

    # Reliable digest fields ordered by algorithm strength.
    RELIABLE_DIGEST_FIELDS = DIGEST_FIELDS[:-3]

    def is_equal(self, other):
        for field in Artifact.RELIABLE_DIGEST_FIELDS:
            digest = getattr(self, field)
            if not digest:
                continue
            if digest == getattr(other, field):
                return True
        return False

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
            self.file.close()
        except Exception:
            self.file.close()
            raise

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.file.delete(save=False)


class FileContent(models.Model):
    TYPE = 'file'

    type = models.TextField(null=False, default=None)
    artifacts = models.ManyToManyField(Artifact, through='ContentArtifact')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        try:
            # if we have a name, use it
            return '<{}: {}>'.format(self._meta.object_name, self.name)
        except AttributeError:
            # if we don't, use the pk
            return '<{}: pk={}>'.format(self._meta.object_name, self.pk)

    def __repr__(self):
        return str(self)

    def save(self, *args, **kwargs):
        if not self.type:
            self.type = self.TYPE
        return super().save(*args, **kwargs)

    @classmethod
    def natural_key_fields(cls):
        return tuple(chain.from_iterable(cls._meta.unique_together))

    def natural_key(self):
        return tuple(getattr(self, f) for f in self.natural_key_fields())

    relative_path = models.TextField(blank=False, null=False)
    digest = models.TextField(blank=False, null=False)

    @property
    def artifact(self):
        return self.artifacts.get().pk

    @artifact.setter
    def artifact(self, artifact):
        if self.pk:
            ca = ContentArtifact(artifact=artifact,
                                 content=self,
                                 relative_path=self.relative_path)
            ca.save()

    class Meta:
        verbose_name_plural = 'content'
        unique_together = (
            'relative_path',
            'digest'
        )


class ContentArtifact(Model):
    artifact = models.ForeignKey(Artifact, on_delete=models.PROTECT, null=True)
    content = models.ForeignKey(FileContent, on_delete=models.CASCADE)
    relative_path = models.CharField(max_length=256)

    class Meta:
        unique_together = ('content', 'relative_path')
