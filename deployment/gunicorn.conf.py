import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/sitanetmerchant_access.log"
errorlog = "/var/log/gunicorn/sitanetmerchant_error.log"
loglevel = "info"

# Process naming
proc_name = "sitanetmerchant"

# Server mechanics
daemon = False
pidfile = "/run/gunicorn/sitanetmerchant.pid"
