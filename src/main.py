import utils
import function
import argparse
from loguru import logger
import os
import sys

# TODO: using starting time as log file name 

# parser settings
parser = argparse.ArgumentParser()
parser.add_argument(
    '-u', '--url',
    type=str,
    help="attach your subscription url here to update your config.yaml"
)
parser.add_argument('command',
                    choices=['setup', 'start', 'stop', 'update', 'log', 'autostart', 'install'])
# TODO implement "uninstall"
parser.add_argument('option', nargs='?')
# parser.add_argument('value', nargs='?', help='The value to set')

# global vars
_conf_dir: str = os.path.join(os.path.expandvars('$HOME'), '.config', 'PythonClash')

if __name__ == "__main__":
    if not os.path.exists(_conf_dir):
        # recursively creating new folders until reach "PythonClash"
        logger.warning("Default user home dir not exist, creating...")
        os.makedirs(_conf_dir, exist_ok=True)
    # confirming conf_path after conf_dir is confirmed
    _conf_path = os.path.join(_conf_dir, "conf.json")

    if not os.path.exists(_conf_path):
        logger.debug("creating & initializing conf.json...")
        with open(_conf_path, 'w') as f:
            # init conf.json
            f.write("{}")
        f.close()

    # at now conf.json should be always accessible
    utils.init_perf(_conf_path)
    utils.perf['config_dir'] = _conf_dir
    if utils.perf.get("log_level") is None:
        utils.perf["log_level"] = "INFO"

    # loguru configuration
    logger.remove(handler_id=None)
    logger.add(
        sink=sys.stderr,
        level=utils.perf.get("log_level")
    )
    logger.debug("logger level has been set to " + utils.perf.get("log_level"))

    args = parser.parse_args()
    utils.perf['sub_url'] = args.url

    # cmd settings
    cmd = args.command
    if cmd == 'update':
        function.update()
    elif cmd == 'setup':
        function.setup()
    elif cmd == 'start':
        function.start()

    if cmd == 'autostart':
        if args.option in ["true", "false"]:
            utils.autostart(args.option)
        else:
            logger.error("Command 'autostart' only support true/false choices")
            exit(1)
    elif cmd == 'install':
        utils.install()

    if args.url is not None:
        # TODO: url connectivity check
        logger.info("new subscribe url has been wrote to file")
