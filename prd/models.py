# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from simple_history.models import HistoricalRecords
from acm.models import Institution
from prd.api import GitLab, JiraProject

# Get an instance of a logger
logger = logging.getLogger(__name__)


def getkey(item):
    return item[1]


def gitlab_project_list():
    short_list = cache.get('gitlab_project_list')
    if not short_list:
        project_list = GitLab().project_list()
        short_list = ((x.id, x.name_with_namespace) for x in project_list)
        short_list = sorted(short_list, key=getkey)
        cache.set('gitlab_project_list', short_list, 60 * 60)
    return short_list


def gitlab_project(pid):
    obj = GitLab().get_project(pid)
    if obj:
        return obj
    else:
        return None


def check_jira_release(project, release):
    jira = JiraProject(project=project)
    task_name = 'Release {}'.format(release)
    issue = jira.search_issue(task_name)
    if not issue:
        issue = create_jira_release(project, release)
    return issue.key


def create_zero_tag(product, release, tag, author):
    # TODO add sql OR
    desc = "Zero tag for new release {}".format(release)
    release_module = ReleasePart.objects.filter(product__jira=product, release=release)
    if not release_module:
        release_module = ReleasePart.objects.filter(product__jira=product)
    for rec in release_module:
        GitLab().create_tag(project_id=rec.gitlab_id, tag=tag, ref=release.dev_branch, user=author.username,
                            desc=desc)


def check_jira_build(project, release, build):
    jira = JiraProject(project=project)
    build_name = 'Build {bld}'.format(bld=build)
    logger.debug("Check Jira build {bld} subtask in project {prj}".format(bld=build, prj=project))
    issue = jira.search_issue(build_name)
    if not issue:
        logger.debug("Task not found!")
        issue = create_jira_build(project, release, build)
    else:
        logger.debug("Task found!")
    return issue.key


def check_jira_task_status(task):
    jira = JiraProject(None)
    return jira.get_task_status(task)


def create_jira_release(project, release):
    jira = JiraProject(project=project)
    logger.info("Create Jira release task for project {}.".format(project))
    release_task = jira.create_release_task(release)
    return release_task


def create_jira_build(project, release, build):
    jira = JiraProject(project=project)
    release_task = check_jira_release(project, release)
    logger.info("Create new Jira Sub-task for build {}".format(build))
    build_task = jira.create_sub_task(release_task, build)
    return build_task


def jira_project_list(project=None):
    project_list_lov = cache.get('jira_project_list')
    if not project_list_lov:
        project_list = JiraProject(project=project).project_list()
        project_list_lov = []
        for rec in ((x.key, "{name}({key})".format(name=x.name, key=x.key)) for x in project_list):
            project_list_lov.append(rec)
        cache.set('jira_project_list', project_list_lov, 60 * 60)  # cache one hour
    return project_list_lov


class Product(models.Model):
    title = models.CharField("Product title", max_length=200, unique=True)
    desc = models.CharField("Product Description", max_length=200, null=True, blank=True)
    wiki_url = models.URLField("Wiki/Confluence URL", null=True, blank=True)
    jira = models.CharField(_("Jira project code"), max_length=20, choices=jira_project_list(), unique=True,
                            help_text="Jira project key")
    inst = models.ForeignKey(Institution, verbose_name='Group')
    owner = models.ForeignKey(User)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    specification_repo = models.IntegerField(_("Specifications repository"), null=True, blank=True,
                                             help_text="Gitlab repository for product specifications",
                                             choices=gitlab_project_list())
    history = HistoricalRecords()

    def __str__(self):
        return "{title}: {inst}".format(title=self.title, inst=self.inst)

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    @property
    def name(self):
        return self.jira.lower()

    @property
    def wiki_url_link(self):
        if self.wiki_url:
            res = '<a href="{url}" targer="_blank">{url}</a>'.format(url=self.wiki_url)
        else:
            res = ''
        return res

    @property
    def jira_url_link(self):
        if self.jira:
            res = '<a href="{url}projects/{jira}" target="_blank">{jira}</a>'.format(jira=self.jira,
                                                                                     url=settings.JIRA_URL)
        else:
            res = ''
        return res

    @property
    def gitlab_project_url(self):
        return gitlab_project(self.specification_repo).web_url

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.jira and not self.desc:
                self.desc = JiraProject(self.jira).get_project_desc()
        super(Product, self).save(*args, **kwargs)


class Release(models.Model):
    name = models.CharField(_("Release number"), max_length=20)
    product = models.ForeignKey(Product)
    jira = models.CharField(_("Jira task for release"), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    released = models.BooleanField(_("Is released"), default=False)
    author = models.ForeignKey(User)
    date_released = models.DateField(_("Release date"), null=True, blank=True)
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('name', 'product',)
        ordering = ['-created']

    def __str__(self):
        return "{rel} - {prd}".format(rel=self.name, prd=self.product)

    def get_absolute_url(self):
        return reverse('release-detail', kwargs={'pk': self.pk})

    @property
    def get_jira_url(self):
        if self.jira:
            res = '<a href="{url}/browse/{task}" target"_blank">{task}</a>' \
                .format(url=settings.JIRA_URL, task=self.jira)
        else:
            res = ''
        return res

    @property
    def jira_task_name(self):
        if self.jira:
            return 'Release {}'.format(self.name)
        else:
            return None

    @property
    def dev_branch(self):
        if self.released:
            ref_name = '{name}-develop'.format(name=self.name)
        else:
            ref_name = 'future'
        return ref_name

    @property
    def stable_branch(self):
        if self.released:
            ref_name = '{name}-master'.format(name=self.name)
        else:
            ref_name = 'future'
        return ref_name

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.jira:
                self.jira = check_jira_release(self.product.jira, self.name)
            super(Release, self).save(*args, **kwargs)
            bld0 = Build(name='0', release=self, author=self.author, released=True, date_released=datetime.date.today())
            bld0.save()
            bld1 = Build(name='1', release=self, author=self.author)
            bld1.save()
        else:
            super(Release, self).save(*args, **kwargs)


class Build(models.Model):
    name = models.CharField("Build number", max_length=20)
    release = models.ForeignKey(Release)
    jira = models.CharField(_("Jira subtask for build"), max_length=20, null=True, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    released = models.BooleanField(_("Is released"), default=False)
    author = models.ForeignKey(User)
    date_released = models.DateTimeField(_("Build date"), null=True, blank=True)
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('name', 'release',)
        ordering = ["-created"]

    def __str__(self):
        return "{prd} {rel}.{build}".format(rel=self.release.name, prd=self.release.product, build=self.name)

    def get_absolute_url(self):
        return reverse('build-detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return '{rel}.{bld}'.format(rel=self.release.name, bld=self.name)

    @property
    def git_name(self):
        return 'v' + self.full_name

    @property
    def get_jira_url(self):
        if self.jira:
            res = '<a href="{url}/browse/{task}" target"_blank">{task}</a>' \
                .format(url=settings.JIRA_URL, task=self.jira)
        else:
            res = ''
        return res

    def hotfix_list(self):
        """Returns the queryset of hotfix for build"""
        hotfix_list = HotFix.objects.filter(build=self.pk).order_by('-date_released')
        return hotfix_list

    @property
    def changelog(self):
        return '{base_url}project/{prj}/{bld}/changelog/'.format(prj=self.release.product.name,
                                                                 bld=self.full_name, base_url=settings.BASE_URL)

    def save(self, *args, **kwargs):

        if not self.jira:
            self.jira = check_jira_build(self.release.product.name, self.release.name, self.full_name)

        if self.released:
            # close jira task
            status = check_jira_task_status(self.jira)
            logger.debug("Jira task {jra} - status is {status}".format(jra=self.jira, status=status))

            if 'Closed' not in status:
                jira = JiraProject(project=self.release.product.jira)
                # jira.assign_task(self.jira, self.author.username)
                # jira.start_task(self.jira)
                jira.add_comment(self.jira, 'Build {}'.format(self.full_name))
                # jira.stop_task(self.jira)
                jira.close_task(self.jira)
            else:
                logger.debug("Task already have status Closed!")
            # create gitlab tag
            if self.name == '0':
                create_zero_tag(self.release.product.jira, self.release, self.git_name, self.author)

        super(Build, self).save(*args, **kwargs)


class HotFix(models.Model):
    name = models.CharField("HotFix number", max_length=20)
    build = models.ForeignKey(Build)
    jira = models.CharField(_("Jira task for hotfix"), max_length=20, null=True, blank=True)
    author = models.ForeignKey(User)
    date_released = models.DateTimeField(_("HotFix date"), auto_now_add=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "HotFix"
        unique_together = ['build', 'name']

    def __str__(self):
        return "{build}.{hotfix}".format(build=self.build, hotfix=self.name)

    def get_absolute_url(self):
        return reverse('hotfix-detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return '{bld}.{hf}'.format(bld=self.build.full_name, hf=self.name)

    @property
    def git_name(self):
        return 'v' + self.full_name

    @property
    def get_jira_url(self):
        if self.jira:
            res = '<a href="{url}/browse/{task}" target"_blank">{task}</a>' \
                .format(url=settings.JIRA_URL, task=self.jira)
        else:
            res = ''
        return res


class ReleasePart(models.Model):
    """ Release part  - product modules configuration"""
    name = models.CharField(_("Module name"), max_length=200)
    product = models.ForeignKey(Product)
    release = models.ForeignKey(to=Release, null=True, blank=True,
                                help_text="Specific release number. Skip if all releases have one configurations")
    gitlab_id = models.IntegerField(_("Gitlab project"), null=True, blank=True, choices=gitlab_project_list())
    history = HistoricalRecords()

    class Meta:
        unique_together = ('name', 'product',)

    def __str__(self):
        return '{product}::{name}'.format(product=self.product.name, name=self.name)

    @property
    def gitlab_project_url(self):
        return gitlab_project(self.gitlab_id).web_url

    @property
    def gitlab_project_name(self):
        return gitlab_project(self.gitlab_id).name_with_namespace

    @property
    def gitlab_repo_ssh(self):
        return gitlab_project(self.gitlab_id).ssh_url_to_repo

    @property
    def gitlab_repo_html(self):
        return gitlab_project(self.gitlab_id).http_url_to_repo

    @property
    def gitlab_project_desc(self):
        return gitlab_project(self.gitlab_id).description


class BuildRevision(models.Model):
    build = models.ForeignKey(Build)
    release_part = models.ForeignKey(ReleasePart)
    revision = models.CharField(_("Git revision"), max_length=40, null=True, blank=True)

    def __str__(self):
        return '{build}={release_part}'.format(build=self.build, release_part=self.release_part)


class HotFixRevision(models.Model):
    hotfix = models.ForeignKey(HotFix)
    release_part = models.ForeignKey(ReleasePart)
    revision = models.CharField(_("Git revision"), max_length=40, null=True, blank=True)

    def __str__(self):
        return '{hotfix}={release_part}'.format(hotfix=self.hotfix, release_part=self.release_part)
