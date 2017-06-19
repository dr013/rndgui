from django.core.management.base import BaseCommand, CommandError
from pymongo import MongoClient
from django.contrib.auth.models import User

from acm.models import Membership
from prd.models import Product, Build, ReleasePart, HotFix, HotFixRevision


def sync_hotfix(prod_jira):
    client = MongoClient('mongodb://sv2.bpc.in:27017')
    db = client['ci']
    product = 'sv'
    project = 'core'

    product_obj = Product.objects.get(jira=prod_jira)
    curs = db.hotfix_list.find({'product': product, 'project': project}).sort('date_hotfix')

    for rec in curs:
        print (rec['release'], rec['build'], rec['hotfix'])
        build = Build.objects.get(release__product__jira=project.upper(), release__name=rec['release'],
                                  name=rec['build'])

        # if user in list - author = user

        author, created = User.objects.get_or_create(username=rec['author'], email='{}@bpcbt.com'.format(rec['author']))
        if created:
            membership = Membership(is_head=False, group_id=1, user=author)
            membership.save()
            print "created user ", author.username

        hotfix, created = HotFix.objects.get_or_create(name=rec['hotfix'], build=build, author=author)
        if created:
            hotfix.jira = rec['hotfix_task']
            hotfix.author = author
            hotfix.date_released = rec['date_hotfix']
            hotfix.save()
        for rec2 in rec['component']:
            if  'name' in rec2 and 'revision' in rec2:
                try:
                    release_part = ReleasePart.objects.get(product=product_obj, name=rec2['name'])
                except ReleasePart.DoesNotExist:
                    print rec2['name'], ' - skip'
                    continue
                hotfix_rev = HotFixRevision(hotfix=hotfix, revision=rec2['revision'], release_part=release_part)
                hotfix_rev.save()


class Command(BaseCommand):
    help = 'Get all tags from GitLab and save in Build models'

    def add_arguments(self, parser):
        parser.add_argument('product', nargs='?', type=str)

    def handle(self, *args, **options):
        jira = options['product'].upper()
        try:
            product = Product.objects.get(jira=jira)
            self.stdout.write('Product found {}'.format(product.title))
            sync_hotfix(jira)

        except Product.DoesNotExist:
            raise CommandError('Product "%s" does not exist' % jira)

        # poll.opened = False
        # poll.save()

        self.stdout.write(self.style.SUCCESS('Successfully added build "%s"' % jira))
