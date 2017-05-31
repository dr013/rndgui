#R&D GUI for release management.
Django web site for manage Products, Releases, QA testing and others. 


Author: Evgeny Kryukov <ekryukov@icloud.com>
##Start new project

* Setup Python 2.7
* Setup virtualenv
* Create virtualenv

```bash
cd rndgui
virtualenv venv
source venv/bin/acitvate
```
* install requirements
```bash
pip install --upgrade pip
pip install -r requirements/dev.txt
```

* set developer settings
```bash
cd rndgui/settings/
cp dev.py.txt dev.py
cd ../../
```
* migrate database
```bash
python manage.py migrate
```

* create superuser (Use BPC AD credentials)
```bash
python manage.py createsuperuser  
```

* run local web-server
```bash
python manage.py runserver
```


# Workflow

We are use GitFlow. Please, install plugin and read this tutorial: 
* [Gitflow cheatsheet + install] (https://danielkummer.github.io/git-flow-cheatsheet/index.ru_RU.html)
* [Habrahabr article] (https://habrahabr.ru/post/106912/)

```bash
git flow init
```
### New features
```bash
# see last version number in file VERSION

# start new git flow branch
# update repo
git fetch --prune && git co develop && git pull
# start new feature
git flow feature start {VERSION+1}
.....
# Don't remember increase version number in file VERSION
.....
git commit -m "My new feature #Gitlab or Jira issue number"
git flow feature finish {VERSION+1}
git pull origin && git push origin
```

