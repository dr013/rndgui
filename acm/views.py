# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import urllib
# noinspection PyCompatibility
import urllib2
import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from prd.models import Product


def start(request):
    # get timesheet
    if request.user.is_authenticated():
        username = request.user.username
        prd_list = Product.objects.all()
        jira_url = settings.JIRA_BROWSE_URL

    return render(request, 'start.html', locals())


def logout_view(request):
    logout(request)
    return redirect('start')


def login_view(request):

    username = request.POST["username"]
    password = request.POST["password"]
    user_arr = check_ldap(username, password)
    if not user_arr:
        # fail LDAP
        messages.add_message(request, messages.ERROR, 'Wrong username/password!')
        return redirect('start')
    else:
        request.session["secret"] = password

    user = authenticate(request, username=username, password=password)

    if user is not None:
        update_user(user, user_arr)
        login(request, user)
    else:
        # create user from LDAP
        user = User.objects.create_user(username=user_arr['username'], email=user_arr['email'],
                                        password=user_arr["password"])
        user.first_name = user_arr["first_name"]
        user.last_name = user_arr["last_name"]
        user.save()

        messages.add_message(request, messages.SUCCESS, _('New user {} was created.'.format(user.username)))
        login(request, user)
    return render(request, 'start.html')


def create_user(username, password, email, first_name, last_name):
    user = User.objects.create_user(username=username, email=email, password=password)
    user.last_name = last_name
    user.first_name = first_name
    user.save()


def check_ldap(username, password):
    if settings.AUTH_URL:
        data = urllib.urlencode({'username': username,
                                 'password': password})
        content = urllib2.urlopen(url=settings.AUTH_URL, data=data)
        user = json.load(content)
        return user


def update_user(user, user_arr):
    u = user
    changed = False

    if not u.first_name:
        u.first_name = user_arr["first_name"]
        changed = True

    if not u.last_name:
        u.last_name = user_arr["last_name"]
        changed = True

    if changed:
        u.save()


def tofirstdayinisoweek(year, week):
    max_week = datetime.date(year, 12, 31).isocalendar()[1]
    if week > max_week:
        week = 1
        year += 1
    if week < 1:
        year -= 1
        week = datetime.date(year, 12, 31).isocalendar()[1]

    ret = datetime.datetime.strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
    if datetime.date(year, 1, 4).isoweekday() > 4:
        ret -= datetime.timedelta(days=7)
    return ret, week


# def timesheet_week(username, start_date=datetime.date.today()):
#     return get_user_week_timesheet(username, start_date)


# def timesheet_month(username, start_date=datetime.date.today()):
#     """
#     Return timesheet report
#     :param username:
#     :param start_date:
#     :return:
#     """
#     start_month = datetime.datetime(start_date.year, start_date.month, 1)
#     duration = calendar.monthrange(start_date.year, start_date.month)[1]
#     return get_user_week_timesheet(username, start_month, duration)


# def timesheet_group(inst_id, start_date, end_date):
#     empls = User.objects.all().filter(groups__in=inst_id)
#     duration = end_date - start_date
#     duration = duration.split()[0]
#
#     timesheet = []
#     for rec in empls:
#         timesheet.extend(get_user_week_timesheet(rec.user.username, start_date, duration))


# def get_user_timesheet(username, start_date=datetime.date.today(), duration=6):
#     """
#     Table of  timesheet
#     :param username: username
#     :param start_date: Start day
#     :param duration: report date delta
#     :return: :raise:
#     """
#     import cx_Oracle
#     timesheet = {}
#     result = {}
#     db_str = {'login': 'jira_worklog', 'passw': 'p12345', 'host': 'odb02.rbs.bpc.in', 'name': 'pdbbpcjira'}
#     dsn = cx_Oracle.makedsn(host=db_str['host'], port=1521, service_name=db_str['name'])
#     db = cx_Oracle.connect(db_str['login'], db_str['passw'], dsn)
#     cursor = db.cursor()
#     # noinspection PyCallByClass
#     end_date = start_date + datetime.timedelta(days=duration)
#     named_params = {'username': username, 'start_date': start_date, 'end_date': end_date}
#     date_list = "'%s'" % "','".join(
#         [(start_date + datetime.timedelta(days=x)).strftime('%d.%m.%y') for x in xrange(duration+1)])
#     date_list += ", '*TOTAL'"
#
#     sql = """
#         select *
#         from
#             (select
#                 case grouping (startdate)
#                     when 0
#                     then startdate
#                     else '*TOTAL'
#                 end         as re
#               , round(sum(hours), 2) as hours
#               , task
#               , summary
#             from
#                 (select
#                     to_char (a.startdate ,'dd.mm.yy') as startdate
#                   , a .hours                          as hours
#                   , a . summary
#                   , a .task
#                 from
#                     bpcjira.jira_worklog_vw a
#                 where
#                     lower (a .user_name) = :username
#                 and a .startdate between trunc(:start_date) and trunc(:end_date)
#                 union all
#                 select
#                     to_char (startdate1 ,'dd.mm.yy') as startdate
#                   , (select
#                         nvl (sum (hours) ,0)
#                     from
#                         bpcjira.jira_worklog_vw a
#                     where
#                         lower (a .user_name)      = :username
#                     and trunc (a.startdate) = startdate1
#                     )
#                   , ' '
#                   , '*TOTAL'
#                 from
#                     (select
#                         trunc (sysdate ,'YEAR') + rn as startdate1
#                     from
#                         (select rownum as rn from all_objects
#                         )
#                     where
#                         rn < 400
#                     )
#                 where
#                     startdate1 between trunc(:start_date) and trunc(:end_date)
#                 )
#             group by
#                 task
#               ,summary
#               ,rollup (startdate)
#             ) pivot (sum (hours) for re in (%s))
#         order by
#             task desc
#         """ % date_list
#
#     try:
#         cursor.execute(sql, named_params)
#     except cx_Oracle.DatabaseError, e:
#         error, = e.args
#         print >> sys.stderr, u'Oracle error: %s' % (error.message,)
#         print >> sys.stderr, error.context
#         print >> sys.stderr, sql
#         logger.error('Oracle error: %s. ' % (error.message,))
#         logger.error('SQL: %s' % sql)
#         cursor.close()
#
#     desc = [x[0].lower() for x in cursor.description]
#     timesheet[username] = [x for x in cursor.fetchall()]
#     cursor.close()
#     result['desc'] = desc
#     result['timesheet'] = timesheet
#     result['jira_url'] = settings.JIRA_BROWSE_URL
#     result['start_date'] = start_date
#     result['end_date'] = end_date
#     result['num_of_week'] = start_date.isocalendar()[1]
#
#     return result
