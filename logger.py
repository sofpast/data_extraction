import os
# import yaml
import logging
from logging.handlers import TimedRotatingFileHandler

from config import config

if not os.path.exists(config.save_log):
    os.mkdir(config.save_log)

SUCCESS = 21
logging.SUCCESS = SUCCESS
logging.addLevelName(SUCCESS, 'SUCCESS')

def success(self, message, *args, **kws):
    """Success logger
    """
    self.log(SUCCESS, message, *args, **kws)

logging.Logger.success = success

if config.log_level.lower() == 'debug':
    log_level = logging.DEBUG
elif config.log_level.lower() == 'info':
    log_level = logging.INFO
elif config.log_level.lower() == 'success':
    log_level = logging.INFO
elif config.log_level.lower() == 'warning':
    log_level = logging.WARNING
elif config.log_level.lower() == 'exception':
    log_level = logging.EXCEPTION
elif config.log_level.lower() == 'critical':
    log_level = logging.CRITICAL
else:
    print('Wrong kind of log level! Exitting ...')
    exit()

log_format = '%(asctime)s: %(levelname)s: %(message)s'


def create_logger(name):
    """Create logger
    """
    formatter = logging.Formatter(log_format)
    logger = logging.getLogger(name)
    logger.setLevel(level=log_level)
    log_dir = os.path.join(config.save_log, name)

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
        
    if config.log_to_file:
        logpath = os.path.join(config.save_log, name, name + '.log')
        fh = TimedRotatingFileHandler(logpath, when="midnight")
        fh.suffix = "%Y%m%d"
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

loggers = {}

def get_logger(name):
    """Get name for logger
    """
    if not loggers.get(name, None):
        loggers[name] = create_logger(name)
    return loggers[name]

