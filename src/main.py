import function
import argparse
from loguru import logger
import json
import os

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
args = parser.parse_args()

exec_dir: str = os.path.dirname(__file__).rpartition("/")[0]
_conf_path: str = exec_dir + "/conf/conf.json"

conf:dict[str, str] = {}

if not os.path.exists(_conf_path):
    with open(_conf_path, 'w') as f:
        f.write("{}")
    f.close()
else:
    with open(_conf_path, 'w+') as f:
        _raw: str = f.read()
        if _raw != "":
            conf = json.loads(_raw)
        else:
            logger.debug('conf.json is empty')
            f.write("{}")
    f.close()


if __name__ == "__main__":

    # only valid with true log files
    logger.add(
        format="{time}|{level}|{message}",
        level='INFO',
        sink=exec_dir + "/log/service.log"
    )

    input_func = args.function

    if args.url is not None:
        logger.info("subscribe url updated...")
        conf['sub_url'] = args.url
        with open(_conf_path, 'w') as cf:
            json.dump(conf, cf)

    if input_func == 'update':
        function.update(conf, exec_dir)
    elif input_func == 'setup':
        function.setup(exec_dir)
    elif input_func == 'start':
        function.start(exec_dir)
    else:
        print('usage')

    # saving conf
    with open(_conf_path, 'w') as cf:
        json.dump(conf, cf)
        

# catch when program exits, to save conf to file