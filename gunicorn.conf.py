import multiprocessing

# bind = "127.0.0.1:8888"

bind = "unix:///var/run/rndgui/rndgui.sock"
# worker numbers 2xCPUs + 1
workers = multiprocessing.cpu_count() * 2 + 1
user = "uwsgi"
group = "uwsgi"
errorlog = "/srv/rndgui/logs/error-gunicorn.log"
loglevel = "info"
proc_name = "rndgui"
accesslog = "/srv/rndgui/logs/access-gunicorn.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
