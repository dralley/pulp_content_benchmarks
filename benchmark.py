import argparse
import hashlib
import time
import django
import uuid
import benchmark
from django.db import transaction
# from django.conf import settings
# settings.configure(default_settings=benchmark.settings, DEBUG=True)
django.setup()

from flat.models import FileContent as FlatFileContent
from flat.models import Artifact as FlatArtifact

from inherited.models import FileContent as InheritedFileContent
from inherited.models import Artifact as InheritedArtifact

from flat_no_uuid.models import FileContent as FlatNoUUIDFileContent
from flat_no_uuid.models import Artifact as FlatNoUUIDArtifact



parser = argparse.ArgumentParser()
parser.add_argument('--num', default=1000)


def make_artifact(seed, cls):
    artifact_dict = {}
    artifact_dict['size'] = 1
    artifact_dict['md5'] = hashlib.md5(str(seed).encode('ascii')).hexdigest()
    artifact_dict['sha1'] = hashlib.sha1(str(seed).encode('ascii')).hexdigest()
    artifact_dict['sha224'] = hashlib.sha224(str(seed).encode('ascii')).hexdigest()
    artifact_dict['sha256'] = hashlib.sha256(str(seed).encode('ascii')).hexdigest()
    artifact_dict['sha384'] = hashlib.sha384(str(seed).encode('ascii')).hexdigest()
    artifact_dict['sha512'] = hashlib.sha512(str(seed).encode('ascii')).hexdigest()
    artifact_dict['sha224'] = hashlib.sha224(str(seed).encode('ascii')).hexdigest()
    return cls(**artifact_dict)

def make_content(cls, artifact):
    content_dict = {}
    content_dict['type'] = 'file'
    content_dict['digest'] = artifact.sha256
    content_dict['relative_path'] = str(uuid.uuid4())
    return cls(**content_dict)

def get_new_artifacts_and_reset(args, cls):
    cls.objects.all().delete()
    artifacts = [
        make_artifact(i, cls) for i in range(int(args.num))
    ]
    cls.objects.bulk_create(artifacts)
    return cls.objects.all()

def get_new_content_and_reset(cls, artifacts):
    cls.objects.all().delete()
    content = [
        make_content(cls, artifact) for artifact in artifacts
    ]
    return content


def main():
    args = parser.parse_args()

    inherited_artifacts = get_new_artifacts_and_reset(args, InheritedArtifact)
    inherited_content = get_new_content_and_reset(InheritedFileContent, inherited_artifacts)

    start = time.time()
    for content in inherited_content:
        content.save()
    end = time.time()

    diff = end - start
    print('{num} units: indidvidual save in seconds: {diff}'.format(diff=diff, num=args.num))


    inherited_artifacts = get_new_artifacts_and_reset(args, InheritedArtifact)
    inherited_content = get_new_content_and_reset(InheritedFileContent, inherited_artifacts)

    start = time.time()
    with transaction.atomic():
        for content in inherited_content:
            content.save()
    end = time.time()

    diff = end - start
    print('{num} units: indidvidual save w/ transaction in seconds: {diff}'.format(diff=diff, num=args.num))


    flat_artifacts = get_new_artifacts_and_reset(args, FlatArtifact)
    flat_content = get_new_content_and_reset(FlatFileContent, flat_artifacts)

    start = time.time()
    FlatFileContent.objects.bulk_create(flat_content)
    end = time.time()

    diff = end - start
    print('{num} units: bulk save in seconds: {diff}'.format(diff=diff, num=args.num))


    # flat_no_uuid_artifacts = get_new_artifacts_and_reset(args, FlatNoUUIDArtifact)
    # flat_no_uuid_content = get_new_content_and_reset(FlatNoUUIDFileContent, flat_no_uuid_artifacts)

    # start = time.time()
    # FlatNoUUIDFileContent.objects.bulk_create(flat_no_uuid_content)
    # end = time.time()

    # diff = end - start
    # print('{num} units: bulk save in seconds: {diff}'.format(diff=diff, num=args.num))


    # start = time.time()
    # FlatNoUUIDFileContent.objects.bulk_create(flat_no_uuid_content)
    # end = time.time()

    # diff = end - start
    # print('{num} units: bulk save in seconds: {diff}'.format(diff=diff, num=args.num))


    # start = time.time()
    # list(FlatFileContent.objects.filter(relative_path__startswith='b'))
    # end = time.time()

    # diff = end - start
    # print('uuid-pk search in {diff} seconds'.format(diff=diff))


    # start = time.time()
    # list(FlatNoUUIDFileContent.objects.filter(relative_path__startswith='b'))
    # end = time.time()

    # diff = end - start
    # print('default-pk search in {diff} seconds'.format(diff=diff))

    print()


if __name__ == '__main__':
    main()
