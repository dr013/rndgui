from django.core.management.base import BaseCommand, CommandError
from pymongo import MongoClient
from django.contrib.auth.models import User
from prd.models import Product, Build, Release, BuildRevision, ReleasePart


def sync_build(release, prod_jira):
    client = MongoClient('mongodb://sv2.bpc.in:27017')
    db = client['ci']
    product = 'sv'
    author = User.objects.get(pk=1)
    release_obj = Release.objects.get(name=release, product__jira=prod_jira)
    curs = db.release_list.find({'product': product, 'release': release, 'date_release': {'$ne': None}})\
        .sort('date_release')
    for rec in curs:
        print (rec['release'], rec['build'])
        build, created = Build.objects.get_or_create(release=release_obj, name=rec['build'], author=author)
        build.released = True
        build.author = author
        build.date_released = rec['date_release']
        for rec2 in ReleasePart.objects.filter(product=release_obj.product):
            for rec3 in rec['component']:
                if rec3['name'] == rec2.name:
                    revision = BuildRevision(build=build, release_part=rec2, revision=rec3['revision'])
                    revision.save()

        build.save()
        print (build, created)


class Command(BaseCommand):
    help = 'Get all tags from GitLab and save in Build models'

    def add_arguments(self, parser):
        parser.add_argument('product', nargs='?', type=str)
        parser.add_argument('release', nargs='?', type=str)

    def handle(self, *args, **options):
        jira = options['product'].upper()
        release = options['release']
        try:
            product = Product.objects.get(jira=jira)
            self.stdout.write('Product found {}'.format(product.title))
            sync_build(release, jira)

        except Product.DoesNotExist:
            raise CommandError('Product "%s" does not exist' % jira)

        # poll.opened = False
        # poll.save()

        self.stdout.write(self.style.SUCCESS('Successfully added build "%s"' % jira))
