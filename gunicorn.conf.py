import multiprocessing

# bind = "127.0.0.1:8888"

bind = "unix:/srv/rndgui/rndgui.sock"
# worker numbers 2xCPUs + 1
workers = multiprocessing.cpu_count() * 2 + 1
user = "uwsgi"
group = "uwsgi"
logfile = "/srv/rndgui/logs/gunicorn.log"
loglevel = "info"
proc_name = "rndgui"
#pidfile = "/home/proft/projects/blog/gunicorn.pid"
