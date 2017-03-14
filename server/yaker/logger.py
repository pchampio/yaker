import logging, logging.config, sys, os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.append(os.path.join(os.path.dirname(__file__)))

if not os.path.exists(BASE_DIR + "/log/"):
    os.makedirs(BASE_DIR + "/log/")

# the basic logger other apps can import
logger = logging.getLogger(__name__)

# Note, doing this manually in every module results in nicer output:
#
#     import logging
#     logger = logging.getLogger(__name__)

# logging dictConfig configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False, # keep Django's default loggers
    'formatters': {
        # see full list of attributes here:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s [%(name)-15.15s] %(message)s'
        },
        'timestampthread': {
            'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s",
        },
    },
    'handlers': {
        'logfile': {
           'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + "/log/logfile",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'timestampthread'
        },
        'console': {
            'level': 'INFO', # INFO or higher goes to the console
            #  'class': 'logging.StreamHandler',
            "class": "colorstreamhandler.ColorStreamHandler",
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': { # configure all of Django's loggers
            'handlers': ['logfile', 'console'],
            'level': 'INFO', # set to debug to see e.g. database queries
            'propagate': False, # don't propagate further, to avoid duplication
        },
        # root configuration – for all of our own apps
        # (feel free to do separate treatment for e.g. brokenapp vs. sth else)
        '': {
            'handlers': ['logfile', 'console'],
            'level': 'DEBUG',
        },
    },
}
