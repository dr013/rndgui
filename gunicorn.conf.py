# bind = "127.0.0.1:8888"

bind = "unix:/home/proft/projects/blog/run/blog.socket"
workers = 5
user = "uwsgi"
group = "uwsgi"
logfile = "/srv/rndgui/logs/gunicorn.log"
loglevel = "info"
proc_name = "rndgui"
#pidfile = "/home/proft/projects/blog/gunicorn.pid"
