# import multiprocessing

workers = 1 # multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:8080'
reload = True

#logging
accesslog = '-'
errorlog = '-'
