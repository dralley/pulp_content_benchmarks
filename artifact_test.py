import argparse
import hashlib
import time

import django
django.setup()
from django.db import transaction

from pulpcore.plugin.models import Artifact


parser = argparse.ArgumentParser()
parser.add_argument('--num', default=1000)


def make_artifact(seed):
        artifact_dict = {}
        artifact_dict['size'] = 1
        artifact_dict['md5'] = hashlib.md5(str(seed).encode('ascii')).hexdigest()
        artifact_dict['sha1'] = hashlib.sha1(str(seed).encode('ascii')).hexdigest()
        artifact_dict['sha224'] = hashlib.sha224(str(seed).encode('ascii')).hexdigest()
        artifact_dict['sha256'] = hashlib.sha256(str(seed).encode('ascii')).hexdigest()
        artifact_dict['sha384'] = hashlib.sha384(str(seed).encode('ascii')).hexdigest()
        artifact_dict['sha512'] = hashlib.sha512(str(seed).encode('ascii')).hexdigest()
        artifact_dict['sha224'] = hashlib.sha224(str(seed).encode('ascii')).hexdigest()
        return Artifact(**artifact_dict)

def get_new_artifacts_and_reset(args):
    Artifact.objects.all().delete()
    artifacts = []
    for i in range(int(args.num)):
        artifacts.append(make_artifact(i))
    return artifacts


def main():
    args = parser.parse_args()

    artifacts = get_new_artifacts_and_reset(args)
    start = time.time()
    for artifact in artifacts:
        artifact.save()
    end = time.time()

    diff = end - start
    print('{num} artifacts: individual save in seconds: {diff}'.format(diff=diff, num=args.num))


    artifacts = get_new_artifacts_and_reset(args)
    start = time.time()
    with transaction.atomic():
        for artifact in artifacts:
            artifact.save()
    end = time.time()

    diff = end - start
    print('{num} artifacts: individual save w/ single transaction in seconds: {diff}'.format(diff=diff, num=args.num))


    artifacts = get_new_artifacts_and_reset(args)
    start = time.time()
    Artifact.objects.bulk_create(artifacts)
    end = time.time()

    diff = end - start
    print('{num} artifacts: bulk save in seconds: {diff}'.format(diff=diff, num=args.num))

    print()



if __name__=='__main__':
    main()

