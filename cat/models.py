# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404
from envrnmnt.models import Environment, WEBInstance, STLNInstance, DBInstance
from prd.models import Product, Release, ReleasePart
from django.contrib.auth.models import User
import logging
import datetime
from django.utils import timezone
from common.jenkins_wrapper import JenkinsWrapper
from common.func import create_hash
from django.conf import settings
import pymongo

STATUSES = (
    ('completed', 'Completed'),
    ('busy', 'Busy'),
    ('fail', 'Failed'),
    ('abort', 'Aborted'),
    ('timeout', 'Timeout'),
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


def make_json(release, envrnmnt):
    """
        Method for prepare JSON resource file for jenkins task
        :param release:   Model Instance
        :param envrnmnt:  Model Instance
    """
    logger.info("Request JSON project by release [{p}] and stand [{e}]".format(p=release.name, e=envrnmnt.name))
    data = {}
    component = list()

    # calculate WebDriver server for UI test
    if "test1" in envrnmnt.name or "test3" in envrnmnt.name:
        web_driver = "weblogic@rnd-sv2-manual1.bt.bpc.in"
    elif "test2" in envrnmnt.name or "test4" in envrnmnt.name:
        web_driver = "weblogic@rnd-sv2-manual2.bt.bpc.in"
    elif "test5" in envrnmnt.name or "test7" in envrnmnt.name:
        web_driver = "weblogic@rnd-sv2-manual3.bt.bpc.in"
    elif "test6" in envrnmnt.name or "test8" in envrnmnt.name:
        web_driver = "weblogic@rnd-sv2-manual4.bt.bpc.in"
    elif "test9" in envrnmnt.name or "test10" in envrnmnt.name:
        web_driver = "weblogic@rnd-sv2-manual5.bt.bpc.in"
    else:
        web_driver = ""

    #   COMPONENT part BACKOFFICE
    try:
        backoffice_instance = envrnmnt.dbinstances.get(release_part=ReleasePart.objects.get(name='backoffice').pk)
    except DBInstance.DoesNotExist, ReleasePart.DoesNotExist:
        backoffice_instance = False
    if backoffice_instance:
        backoffice = {
            'name': 'backoffice',
            'RND_PROJECT_ALL': True,
            'USE_TEST_CONF': True,
            'USE_CUSTOM': True,
            "DB_LOGIN": backoffice_instance.login,
            "DB_PASSWD": backoffice_instance.passwd,
            "DB_HOST": backoffice_instance.host,
            "DB_PORT": backoffice_instance.port,
            "DB_NAME": backoffice_instance.sid,
            "INSTANCE_NAME": "Test {r}".format(r=release.name),
            "SOURCE_CHECKOUT": release.dev_branch,
            "BUILD_MODE": "stand",
            "SOURCE_REPO": ReleasePart.objects.get(name='backoffice').gitlab_repo_html,
            "SYSTEM_LOGIN": backoffice_instance.sys_user,
            "SYSTEM_PASSWD": backoffice_instance.sys_passwd
            }
        component.append(backoffice)
        test_db = True
        db_instance = "{u}/{p}@{h}:{port}/{s}".format(u=backoffice_instance.login,
                                                      p=backoffice_instance.passwd,
                                                      h=backoffice_instance.host,
                                                      port= backoffice_instance.port,
                                                      s=backoffice_instance.sid)
    else:
        test_db = False
        db_instance = ""

    #   COMPONENT part SVWEB
    try:
        svweb_instance = envrnmnt.webinstances.get(release_part=ReleasePart.objects.get(name='svweb').pk)
    except WEBInstance.DoesNotExist, ReleasePart.DoesNotExist:
        svweb_instance = False
    if svweb_instance:
        svweb = {
            'name': 'svweb',
            "TARGET_HOST": svweb_instance.host,
            "HOST_LOGIN": svweb_instance.login,
            "WL_ADMIN": "t3://{h}:{p}".format(p=svweb_instance.port, h=svweb_instance.host),
            "WL_TGT_SERV": svweb_instance.target_server,
            "SOURCE_REPO": ReleasePart.objects.get(name='svweb').gitlab_repo_html,
            "SOURCE_CHECKOUT": release.dev_branch
        }
        component.append(svweb)
        wl_instance = "{u}@{h}".format(u=svweb_instance.login, h=svweb_instance.host)
        wi_test_host = "http://{host}:7002/sv/".format(host=svweb_instance.host)
    else:
        wl_instance = ''
        wi_test_host = ''

    #   COMPONENT part CAMEL
    try:
        camel_instance = envrnmnt.webinstances.get(release_part=ReleasePart.objects.get(name='camel').pk)
    except WEBInstance.DoesNotExist, ReleasePart.DoesNotExist:
        camel_instance = False
    if camel_instance:
        camel = {
            'name': 'camel',
            "TARGET_HOST": svweb_instance.host,
            "HOST_LOGIN": svweb_instance.login,
            "WL_ADMIN": "t3://{h}:{p}".format(p=svweb_instance.port, h=svweb_instance.host),
            "WL_TGT_SERV": svweb_instance.target_server,
            "SOURCE_REPO": ReleasePart.objects.get(name='camel').gitlab_repo_html,
            "SOURCE_CHECKOUT": release.dev_branch
        }
        component.append(camel)
        test_posting = True
        test_web_service = True
    else:
        test_posting = False
        test_web_service = False

    # COMPONENT part svfe_adapter
    try:
        adapter_instance = envrnmnt.stlninstances.get(release_part=ReleasePart.objects.get(name='svfe_adapter').pk)
    except STLNInstance.DoesNotExist, ReleasePart.DoesNotExist:
        adapter_instance = False
    if adapter_instance:
        svfe_adapter = {
            'name': 'svfe_adapter',
            "TARGET_HOST": "{u}@{h}".format(u=adapter_instance.user, h=adapter_instance.host),
            "HOST_LOGIN": adapter_instance.user,
            "SOURCE_TYPE": "get",
            "SOURCE_DIR": "/srv/share/builds/core/test-builds/sv/{r}/svfe_adapter".format(r=release.name)
        }
        component.append(svfe_adapter)

    # COMPONENT part svfe_front
    try:
        front_instance = envrnmnt.stlninstances.get(release_part=ReleasePart.objects.get(name='svfe_adapter').pk)
    except STLNInstance.DoesNotExist, ReleasePart.DoesNotExist:
        front_instance = False
    if front_instance:
        svfe_front = {
            'name': 'svfe_front',
            'SOURCE_DIR': "/srv/share/builds/core/svfe/",
            "TARGET_HOST": front_instance.host,
            "HOST_LOGIN": front_instance.user
        }
        component.append(svfe_front)
        test_fe = True
        fe_instance = "{u}@{h}".format(u=front_instance.user, h=front_instance.host)
    else:
        test_fe = False
        fe_instance = ''

    #   TEST part
    test = {
        "TL_PROJ": "SmartVista Core",
        "TL_APIKEY": "b2a87d044aa1c5ab282f314bd051c9e3",
        "WI_TEST_HOST": wi_test_host,
        "JMETER_BRANCH": release.name,
        "TARGET_HOST": envrnmnt.name,
        "TEST_BUILD": release.name,
        "FE_INSTANCE": fe_instance,
        "WL_INSTANCE": wl_instance,
        "WI_TEST_TARGET": wi_test_host,
        "WI_TEST_BRANCH": release.name,
        "RELEASE": release.name,
        "TEST_FE": test_fe,
        "TEST_DB": test_db,
        "BO_INSTANCE": db_instance,
        "TEST_POSTING": test_posting,
        "TEST_GUI2": False,
        "WD_HOST": web_driver,
        "TEST_WS": test_web_service,
        "UPLOAD_TARGET": wl_instance
    }

    #   MAIN part
    data['name'] = '{r}_{e}_auto_test'.format(r=release.name, e=envrnmnt.name)
    data['host'] = envrnmnt.name
    data['project'] = Product.objects.get(release=release).jira
    data['is_active'] = True
    data['product'] = Product.objects.get(release=release).title
    data['release'] = release.name
    data['component'] = component
    data['test'] = test
    return data


def get_project(release, envrnmnt):
    db = settings.DB_MONGO
    #   generate JSON data by RELEASE and Env
    json_data = make_json(release, envrnmnt)
    exist_data = db['resource_data'].find_one({'name': json_data['name']})
    if exist_data and 'name' in exist_data:
        logger.info("Project for release [{p}] and stand [{e}] already exists - [{pr}]".format(p=release.name,
                                                                                               e=envrnmnt.name,
                                                                                               pr=json_data['name']))
        return json_data['name']
    else:
        logger.info("Project for release [{p}] and stand [{e}] NOT exists, create it".format(p=release.name,
                                                                                             e=envrnmnt.name))
        try:
            res = db['resource_data'].insert(json_data)
        except pymongo.errors.OperationFailure, e:
            logger.error(e)
        if res:
            return json_data['name']


def get_next_release(product):
    #   get all releases from carousel
    """
        Get next release for testing by product
        :param product:
        :return: release for testing in string format
    """
    release = ''
    logger.info("Get Release for testing by product [{p}]".format(p=product.name))
    try:
        release = ReleaseCarousel.objects.all().filter(release__product=product,
                                                       is_active=True).order_by('count', 'last_used_at').first()
    except ReleaseCarousel.DoesNotExist, err:
        logger.error("Release for testing not found error - {e}".format(e=err))
    if release:
        logger.info("Release for testing is [{r}]".format(r=release))
        release.use()
        return release


class TestEnvironment(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    env = models.ForeignKey(Environment, verbose_name='Environment')
    prd = models.ForeignKey(Product, verbose_name='Product', null=True, blank=True)
    expire = models.CharField('Expire time', max_length=200, default=120)
    is_active = models.BooleanField("Is active", default=True)

    class Meta:
        permissions = (
            ("can_unlock", "Can force unlock stand"),
            ("can_run", "Can manual run stand"),
        )
        ordering = ['-is_active', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('test-env-detail', kwargs={'pk': self.pk})

    @property
    def is_env_active(self):
        env = Environment.objects.all().filter(name=self.env).values('is_active')
        return env[0]['is_active']

    @property
    def status(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at').first()
        if data:
            if "busy" not in data.status:
                return 'Ready'
            else:
                return 'Busy'
        else:
            return "Ready"

    @property
    def release_testing(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at').first()
        if data:
            if "busy" in data.status:
                return data.release.name
            else:
                return False
        else:
            return False

    @property
    def hash(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at').first()
        if data:
            if "busy" not in data.status:
                return False
            else:
                return data.hash
        else:
            return False

    def acquire(self, user=None, release=None):
        """
            Func for acquire stand for testing
            :param user:  Save authenticated user in database
            :param release: Release for testing
            :return: Stand for testing
        """
        jenkins = JenkinsWrapper()
        #   generate unique hash code
        stand_hash = create_hash()
        #   get the last usage info about the current stand
        usage_info_arr = UsageLog.objects.all().filter(stand=self)
        #   if the stand has previously been used
        if usage_info_arr.count() > 0:
            #   To the last record about the used stand
            last_usage_stand = usage_info_arr.order_by('-started_at')[0]
            # if the current stand in "busy" status - skip them
            if 'busy' in last_usage_stand.status:
                logger.info("Stand [{st}] - is busy".format(st=self.name))
            else:
                logger.info("Stand [{st}] - free, can use it".format(st=self.name))
                # get next release for testing by Product, if it not set in params
                if not release:
                    release = get_next_release(product=self.prd)
                    #   if releaseCarousel is empty
                    if not release:
                        logger.warning("Releases carousel is empty. There is nothing to test ")
                        return False

                #   generate resource_file for Jenkins task
                env = Environment.objects.get(name=self.env)
                prj = get_project(release=get_object_or_404(Release, name=release),
                                  envrnmnt=env)
                logger.info("Project name is [{pr}]".format(pr=prj))

                #   run Jenkins task on "free" stand
                task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                         param={'PROJECT': prj, 'HASH': stand_hash})
                #   save selected stand to database, and mark as 'busy'
                use = UsageLog(stand=self,
                               release=get_object_or_404(Release, name=release),
                               status='busy',
                               task=task,
                               author=user,
                               hash=stand_hash)
                use.save()
                return self
        #   if the stand has NOT previously been used
        else:
            logger.info("Stand [{st}] - free and it can use now".format(st=self.name))
            # get next release for testing by Product, if it not set in params
            if not release:
                logger.info("Releases not passed. Get it from carousel")
                release = get_next_release(product=self.prd)
                #   if releaseCarousel is empty
                if not release:
                    logger.warning("Releases carousel is empty. There is nothing to test ")
                    return False
            else:
                logger.info("Releases [{r}] is set in params".format(r=release))

            #   get Env by Stand
            env = Environment.objects.get(name=self.env)
            #   generate resource_file for Jenkins task
            prj = get_project(release=get_object_or_404(Release, name=release),
                              envrnmnt=env)
            logger.info("Project name is [{pr}]".format(pr=prj))

            #   run Jenkins task on "free" stand
            task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                     param={'PROJECT': prj, 'HASH': stand_hash})
            #   save selected stand to database, and mark as 'busy'
            use = UsageLog(stand=self,
                           release=get_object_or_404(Release, name=release),
                           status='busy',
                           task=task,
                           author=user,
                           hash=stand_hash)
            use.save()
            return self
        return False


class UsageLog(models.Model):
    stand = models.ForeignKey(TestEnvironment, verbose_name='Environment')
    release = models.ForeignKey(Release, verbose_name='Release')
    status = models.CharField('Statuses', choices=STATUSES, max_length=200, default='busy')
    started_at = models.DateTimeField(verbose_name='Start time', auto_now_add=True)
    finished_at = models.DateTimeField(verbose_name='Finish time', null=True, blank=True)
    task = models.CharField('Task', max_length=200, null=True, blank=True)
    hash = models.CharField(max_length=10, editable=False, unique=True)
    author = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return '{name}::{status}'.format(name=self.stand, status=self.status)

    def release_stand(self, status, force=False):
        """
            Method for release (unlock) 'busy' stand
            :param status: The status of the result testing on stand
            :param force: If set to 'true' Jenkins task will be aborted
            :return: self instance
        """
        #   set 'finished' time
        self.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        #   if 'force' - abort Jenkins jobs
        if force:
            jenkins = JenkinsWrapper()
            jenkins.stop_build(task_url=self.task)
        self.status = status
        self.save()
        logger.info("Stand [{st}] - was released".format(st=self.stand))
        return self


class ReleaseCarousel(models.Model):
    release = models.OneToOneField(Release, unique=True)
    count = models.IntegerField('Priority', null=True, blank=True, default=0)
    created_at = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    last_used_at = models.DateTimeField(verbose_name='Last used')
    sort = models.IntegerField('Sort', default=10)
    is_active = models.BooleanField("Is active", default=True)

    class Meta:
        ordering = ['-is_active', 'count', 'last_used_at', 'sort']

        permissions = (
            ("can_order", "Manual order priority"),
        )

    @property
    def testing_on(self):
        data = UsageLog.objects.all().filter(release=self.release).order_by('-started_at').first()
        if data:
            if "busy" in data.status:
                return data.stand
            else:
                return False
        else:
            return False

    @property
    def is_first(self):
        first_rec = ReleaseCarousel.objects.all().filter(is_active=True).order_by('count', 'last_used_at').first()
        if self == first_rec:
            return True
        else:
            return False

    @property
    def is_last(self):
        last_rec = ReleaseCarousel.objects.all().filter(is_active=True).order_by('count', 'last_used_at').last()
        if self == last_rec:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('rcarousel-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{r}'.format(r=self.release.name)

    def use(self):
        self.count += 1
        self.last_used_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        self.save()
