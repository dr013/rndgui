
from .models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
                return res
        else:
            logger.info("Stand [{st}] - is disabled".format(st=stand.name))


def release_stand(hash_code, force=False):
    #   try get 'busy' stand by hash
    try:
        busy_stand = UsageLog.objects.get(hash=hash_code)
        return busy_stand.release_stand(force=force)
    except UsageLog.DoesNotExist:
        logger.error("Log record with hash [{h}] was not found!".format(h=hash_code))


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
            usage_stand.release_stand(force=True)
        else:
            logger.info("End time [{ex}] for stand [{st}] is not out. Continue work.".format(st=stand.name,
                                                                                             ex=print_expire_date))
