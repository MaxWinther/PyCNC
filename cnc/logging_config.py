import logging

logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s [%(levelname)s] %(message)s')


def debug_enable():
    logging.getLogger().setLevel(logging.DEBUG)


def debug_disable():
    logging.getLogger().setLevel(logging.CRITICAL)
