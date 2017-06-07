#!/usr/bin/env python
# coding=utf-8
#  Created by 'Evgeny Krukov<krukov@bpcbt.com>' at 07.11.13 19:53<br />

import datetime
from fabric.api import env, run, cd, sudo, require, prefix
from fabric.colors import green, red
from fabric.contrib import django
from contextlib import contextmanager as _contextmanager

now = datetime.datetime.now()
django.project('rndgui')
django.settings_module('rndgui.settings')


def production1():
    # здесь данные об удаленном сервере с сайтом
    env.environment = "production"
    env.hosts = ["sv2-web.bt.bpc.in:22"]
    env.user = 'uwsgi'
    env.path = '/srv/rndgui'
    env.db_host = 'rnd-pg.bt.bpc.in'
    env.activate = 'source /srv/rndgui/venv/bin/activate'


def production2():
    # здесь данные об удаленном сервере с сайтом
    env.environment = "production"
    env.hosts = ["sv2-web2.bt.bpc.in:22"]
    env.user = 'uwsgi'
    env.path = '/srv/rndgui'
    env.db_host = 'rnd-pg.bt.bpc.in'
    env.activate = 'source /srv/rndgui/venv/bin/activate'


def dev():
    # здесь данные об удаленном сервере с сайтом
    env.environment = "develop"
    env.hosts = ["sv2.bpc.in:22"]
    env.user = 'www-data'
    env.path = '/srv/rndgui'
    env.db_host = 'rnd-pg.bt.bpc.in'
    env.activate = 'source /srv/rndgui/venv/bin/activate'


@_contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield


def deploy():
    """
    In the current version fabfile no initial database creation and configure the virtual server host.
    """
    require('environment', provided_by=[production1, production2, dev])
    print(red("Beginning Deploy:"))
    update_from_git()
    install_requirements()
    if 'develop' in env.environment:
        set_dev_config()
    migrate()
    if env.environment == 'production':
        # stop_webserver()
        collect_static()
        # start_webserver()
        # touch_reload()
    elif 'develop' in env.environment:
        run_dev_server()


def install_requirements():
    require('environment', provided_by=[production1, production2, dev])  # дописать по желанию dev и stage
    print(green(" * install the necessary applications..."))
    if 'develop' in env.environment:
        req = 'dev.txt'
    else:
        req = 'prod.txt'
    with virtualenv():
        requirements_file = 'requirements/{req}'.format(req=req)

        args = ['install',
                '-r', requirements_file, '--upgrade'
                ]
        run('pip %s' % ' '.join(args))


def update_from_git():
    require('environment', provided_by=[production1, production2, dev])
    print(green('* update from git'))
    with cd(env.path):
        print(green('run checkout master'))
        run('git checkout -- .')
        run('git clean -fd')

        if 'develop' in env.environment:
            run('git checkout develop')
        else:
            run('git checkout master')

        run('git fetch --prune origin')
        run('git pull')


def touch_reload():
    require('environment', provided_by=[production1, production2, dev])  # дописать по желанию dev и stage
    print(green('touch reload uwsgi'))
    with cd(env.path):
        run("git show > uwsgi")


def migrate():
    require('environment', provided_by=[production1, production2, dev])  # дописать по желанию dev и stage
    print(green('Migrate database'))
    with virtualenv():
        run("python manage.py migrate")


def collect_static():
    require('environment', provided_by=[production1, production2, dev])  # дописать по желанию dev и stage
    print(green('Collect static'))
    with virtualenv():
        run("python manage.py collectstatic -l --noinput")


def stop_webserver():
    require('environment', provided_by=[production1, production2, dev])  # дописать по желанию dev и stage
    print(green('Stop uwsgi'))
    sudo("/etc/init.d/uwsgi stop")


def set_dev_config():
    print (red('Copy settings/dev'))
    with cd(env.path):
        run('cp rndgui/settings/demo.py rndgui/settings/dev.py')


def run_dev_server():
    print (green('Run dev server'))
    with virtualenv():
        run('python manage.py runserver sv2.bpc.in:8000 &')
