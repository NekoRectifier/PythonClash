import function
import argparse
from loguru import logger
import json
import os
import getpass

parser = argparse.ArgumentParser(usage="\n\tpython3 main.py {setup, update, start, stop}\n")

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
    '-d', '--dir',
    type=str,
    help="input a path where you want to place the conf.json"
)

args = parser.parse_args()

# rewrite
_marker = False
def_conf_path: str =  os.path.join(os.path.expandvars('HOME'),'PythonClash')
conf_path = ""
conf_dict = {}

if args.dir is not None:
    logger.info("Using custom config dir, writing now...")
    _abs_custom_dir = str(os.path.abspath(args.dir))
    if os.path.exists(_abs_custom_dir):
        conf_dict['config_dir'] = _abs_custom_dir
        # with open(args.dir, 'w') as f_conf:
        #     f_conf.write(json.dumps(conf_dict))
        conf_path: str = _abs_custom_dir
        #     # handmade json
    else:
        logger.critical("Designated dir is not reachable, do not use any short like '~' ")
        exit(1)

elif args.dir is None and os.path.exists(def_conf_path):
    # using default conf.json directory: ~/.config/PythonClash/conf.json
    logger.info("Using default config dir...")
    _marker = True
elif args.dir is None and not os.path.exists(def_conf_path):
    # recursively creating new folders until reach "PythonClash"
    logger.warning("Default user home dir not exist, creating...")
    _marker = True
    
if _marker:
    os.makedirs(def_conf_path, exist_ok=True)
    # with open(def_conf_path, ) as f_conf:
    #     f_conf.write("{}")
    # f_conf.close()
    conf_path = def_conf_path


if __name__ == "__main__":

    # only valid with true log files
    logger.add(
        format="{time}|{level}|{message}",
        level='INFO',
        sink=conf_path + "/log/service.log"
    )
    # TODO: using starting time as log file name 

    input_func = args.function

    if args.url is not None:
        logger.info("new subscribe url has been wrote to file")
        conf_dict['sub_url'] = args.url

    if input_func == 'update':
        function.update(conf_dict)
    elif input_func == 'setup':
        function.setup(conf_dict)
    elif input_func == 'start':
        function.start(conf_dict)
    else:
        print('usage') 

with open(conf_path, 'w') as f_conf:
    f_conf.write(json.dumps(conf_dict))
f_conf.close()
# lastly save the configuration to the json file