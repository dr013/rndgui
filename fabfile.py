#!/usr/bin/env python
# coding=utf-8
#  Created by 'Evgeny Krukov<krukov@bpcbt.com>' at 07.11.13 19:53<br />

import datetime
from fabric.api import env, run, cd, sudo, require, prefix
from fabric.colors import green, red
from contextlib import contextmanager as _contextmanager

now = datetime.datetime.now()


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


@_contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield


def deploy():
    """
    In the current version fabfile no initial database creation and configure the virtual server host.
    """
    require('environment', provided_by=[production1, production2])
    print(red("Beginning Deploy:"))

    if env.environment == 'production':
        # stop_webserver()
        update_from_git()
        install_requirements()
        migrate()
        collect_static()
        # start_webserver()
        touch_reload()


def install_requirements():
    require('environment', provided_by=[production1, production2])  # дописать по желанию dev и stage
    print(green(" * install the necessary applications..."))
    with virtualenv():
        requirements_file = env.path + '/requirements/prod.txt'

        args = ['install',
                '-r', requirements_file, '--upgrade'
                ]
        run('pip %s' % ' '.join(args))


def update_from_git():
    require('environment', provided_by=[production1, production2])
    print(green('* update from git'))
    with cd(env.path):
        print(green('run checkout master'))
        run('git checkout -- .')
        run('git clean -fd')
        run('git fetch --prune origin')
        run('git pull')


def touch_reload():
    require('environment', provided_by=[production1, production2])  # дописать по желанию dev и stage
    print(green('touch reload uwsgi'))
    with cd(env.path):
        run("git show > uwsgi")


def migrate():
    require('environment', provided_by=[production1, production2])  # дописать по желанию dev и stage
    print(green('Migrate database'))
    with virtualenv():
        run("python manage.py migrate")


def collect_static():
    require('environment', provided_by=[production1, production2])  # дописать по желанию dev и stage
    print(green('Collect static'))
    with virtualenv():
        run("python manage.py collectstatic")


def stop_webserver():
    require('environment', provided_by=[production1, production2])  # дописать по желанию dev и stage
    print(green('Stop uwsgi'))
    sudo("/etc/init.d/uwsgi stop")
