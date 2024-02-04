import utils
import function
import argparse
from loguru import logger
import os
import sys

# loguru configuration
logger.remove(handler_id=None)

logger.add(
    sink=sys.stderr,
    # format="<green>{time:HH:mm:ss}</> | <blue>{level}</> | {message}",
    # colorize=True,
    level='DEBUG',
)
# TODO: using starting time as log file name 

parser = argparse.ArgumentParser()

parser.add_argument(
    'function',
    type=str,
    choices=["update", "setup", "start", "stop"]
)
parser.add_argument(
    '-u', '--url',
    type=str,
    help="attach your subscription url here to update your config.yaml"
)

parser.add_argument(
    '--config_dir',
    type=str,
    help="path of configuration files like conf.json"
)

args = parser.parse_args()

def_conf_dir: str = os.path.join(os.path.expandvars('$HOME'), '.config', 'PythonClash')
conf_dir = ""

if args.dir is not None:
    logger.info("Using custom config dir, writing now...")
    _abs_custom_dir = str(os.path.abspath(args.dir))
    if os.path.exists(_abs_custom_dir):
        conf_dir: str = _abs_custom_dir
    else:
        logger.critical("Designated dir is not reachable, do not use any short like '~' ")
        exit(1)

elif args.dir is None:
    conf_dir = def_conf_dir
    if os.path.exists(def_conf_dir):
        # using default conf.json directory: ~/.config/PythonClash/conf.json
        logger.info("Using default config dir...")
    else:
        # recursively creating new folders until reach "PythonClash"
        logger.warning("Default user home dir not exist, creating...")
        os.makedirs(def_conf_dir, exist_ok=True)

logger.debug("current config dir: " + conf_dir)
# confirming conf_path after conf_dir is confirmed
_conf_path = os.path.join(conf_dir, "conf.json")

if not os.path.exists(_conf_path):
    logger.debug("creating & initializing conf.json...")
    with open(_conf_path, 'w') as f:
        # init conf.json
        f.write("{}")
    f.close()

# at now conf.json should be always accessible
utils.init_perf(_conf_path)
utils.perf['config_dir'] = conf_dir

if __name__ == "__main__":
    input_func = args.function

    if args.url is not None:
        logger.info("new subscribe url has been wrote to file")
        utils.perf['sub_url'] = args.url

    if input_func == 'update':
        function.update()
    elif input_func == 'setup':
        function.setup()
    elif input_func == 'start':
        function.start()
