import logging
import re
import ast

logger = logging.getLogger('jekkin')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - JEKKIN_MONITOR\t%(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)

pattern = "JEKKIN_MONITOR\t([\w_]+)\t([\w.]+)"
matcher = re.compile(pattern=pattern)

def capture_value(line):
    results = matcher.search(line)
    if results:
        return results.group(1), ast.literal_eval(results.group(2))


def log_value(name, value):
    logger.info(msg="{}\t{}".format(name, value))
