from celery import task
from cat.models import TestEnvironment, UsageLog, ReleaseCarousel
import logging
from django.shortcuts import get_object_or_404
import datetime
from django.utils import timezone

# Get an instance of a logger
logger = logging.getLogger(__name__)


@task()
def get_stand(release=None):
    #   get all exists stands from the db
    all_stands = TestEnvironment.objects.all()
    for stand in all_stands:
        logger.info("Check stand [{st}]:".format(st=stand.name))
        #   if the stand is not active
        if stand.is_active:
            #  try acquire stand
            res = stand.acquire(release=release)
            if res:
                return res.name
        else:
            logger.info("Stand [{st}] - is disabled".format(st=stand.name))


@task()
def release_stand(hash_code, status, force=False):
    #   try get 'busy' stand by hash
    try:
        busy_stand = UsageLog.objects.get(hash=hash_code)
        return busy_stand.release_stand(force=force, status=status)
    except UsageLog.DoesNotExist:
        logger.error("Log record with hash [{h}] was not found!".format(h=hash_code))


@task()
def auto_release_stand():
    #   get all 'busy' stands
    busy_stands_arr = UsageLog.objects.all().filter(status='busy')
    for usage_stand in busy_stands_arr:
        #   get the stand startTime's
        start_time = datetime.datetime.strftime(usage_stand.started_at, "%H:%M:%S %d/%m")
        logger.info("Run check used stand [{st}], started at {tm}:".format(st=usage_stand.stand, tm=start_time))
        #   get stand from Model by stand from UsageLog
        stand = get_object_or_404(TestEnvironment, name=usage_stand.stand)
        #   get expireTime for stand
        expire_data = usage_stand.started_at + datetime.timedelta(minutes=int(stand.expire))
        #   human's expireTime
        print_expire_date = datetime.datetime.strftime(expire_data, "%d/%m %H:%M:%S")
        #   if DateTime.now() more than expireTime, unlock stand
        if expire_data < timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()):
            logger.info("End time [{ex}] for stand [{st}] is over. "
                        "The work will be abort.".format(st=stand.name,
                                                         ex=print_expire_date))
            usage_stand.release_stand(force=True, status='timeout')
        else:
            logger.info("End time [{ex}] for stand [{st}] is not out. Continue work.".format(st=stand.name,
                                                                                             ex=print_expire_date))


def up_release(pk):
    #   getting the Release to raise
    release = get_object_or_404(ReleaseCarousel, pk=pk)
    logger.info("Request UP release [{r}] for testing".format(r=release))
    #   the current positions of this "sort" for the release
    cur_release_pos = int(release.count)
    #   try found other releases with same "sort"
    cnt_other_releases = ReleaseCarousel.objects.all().filter(count=cur_release_pos-1).count()
    logger.info("[{c}] - releases already in the same priority of the sort".format(c=cnt_other_releases))
    if cnt_other_releases > 0:
        logger.info("Getting all releases in the needed priority [{p}] and sort them".format(p=release.count-1))
        other_releases = ReleaseCarousel.objects.all().filter(count=cur_release_pos-1).order_by('last_used_at')
        logger.info("The release [{r}] is the first at the needed priority [{p}]".format(r=other_releases[0],
                                                                                         p=cur_release_pos-1))
        #   get the first element from other releases and take his lastUsedTime
        last_used_time = other_releases[0].last_used_at
        used_time = last_used_time - datetime.timedelta(hours=1)
        logger.info("Change priority for the release [{r}] to [{p}] and set last_used_datetime to [{t}] "
                    "before the last_used_datetime release [{br}]".format(r=release,
                                                                          p=release.count-1,
                                                                          t=used_time,
                                                                          br=other_releases[0]
                                                                          ))
        release.count -= 1
        release.last_used_at = used_time
        release.save()
        return release.release
    else:
        logger.info("Change priority for the release [{r}] to [{p}]".format(r=release, p=release.count-1))
        release.count -= 1
        release.save()
        return release.release


def down_release(pk):
    #   getting the Release to lowering
    release = get_object_or_404(ReleaseCarousel, pk=pk)
    logger.info("Request DOWN release [{r}] for testing".format(r=release))
    #   the current positions of this "sort" for the release
    cur_release_pos = int(release.count)
    #   try found other releases with same "sort"
    cnt_other_releases = ReleaseCarousel.objects.all().filter(count=cur_release_pos+1).count()
    logger.info("[{c}] - releases already in the same priority of the sort".format(c=cnt_other_releases))
    if cnt_other_releases > 0:
        logger.info("Getting all releases in the needed priority [{p}] and sort them".format(p=release.count+1))
        other_releases = ReleaseCarousel.objects.all().filter(count=cur_release_pos+1).order_by('-last_used_at')
        logger.info("The release [{r}] is the first at the needed priority [{p}]".format(r=other_releases[0],
                                                                                         p=cur_release_pos+1))
        last_used_time = other_releases[0].last_used_at
        used_time = last_used_time + datetime.timedelta(minutes=5)
        logger.info("Change priority for the release [{r}] to [{p}] and set last_used_datetime to [{t}] "
                    "before the last_used_datetime release [{br}]".format(r=release,
                                                                          p=release.count+1,
                                                                          t=used_time,
                                                                          br=other_releases[0]
                                                                          ))
        release.count += 1
        release.last_used_at = used_time
        release.save()
        return release.release
    else:
        logger.info("Change priority for the release [{r}] to [{p}]".format(r=release, p=release.count+1))
        release.count += 1
        release.save()
        return release.release
