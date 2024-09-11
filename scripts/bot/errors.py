import logging, sys, os, inspect


def setup_logging(debug_info_log, warning_error_log):
    sys.stderr = open(os.devnull, 'w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    info_handler = logging.FileHandler(debug_info_log)
    info_handler.setLevel(logging.INFO)

    warning_error_handler = logging.FileHandler(warning_error_log)
    warning_error_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    warning_error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warning_error_handler)

    info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    
def conserr(e, pass_=False):
    logging.error(f"MSG: [{e}], WHERE:[{__name__}.{inspect.stack()[1].function}]", exc_info=True)
    if not pass_:
        exit(0)