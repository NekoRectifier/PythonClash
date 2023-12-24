import function
import argparse
from loguru import logger
import json
import os

parser = argparse.ArgumentParser(usage="\n\tpython3 main.py {setup, update, start, stop, restart}\n")

parser.add_argument('function')
parser.add_argument('-u', '--url')
args = parser.parse_args()

exec_dir = os.path.dirname(__file__).rpartition("/")[0]
_conf_path = exec_dir + "/conf/conf.json"

conf = {}

if not os.path.exists(_conf_path):
    with open(_conf_path, 'w') as f:
        f.write("{}")
    f.close()
else:
    with open(_conf_path, 'w+') as f:
        _raw = f.read()
        if _raw != "":
            conf = json.loads(_raw)
        else:
            logger.debug('conf.json is empty')
            f.write("{}")
    f.close()


if __name__ == "__main__":
    input_func = args.function

    if args.url is not None:
        logger.info("subscribe url updated...")
        conf['sub_url'] = args.url

    if input_func == 'update':
        print("starting update now...")
        function.update()
    elif input_func == 'setup':
        function.setup(exec_dir)
    elif input_func == 'start':
        print("start clash core")
    else:
        print('usage')

    # saving conf
    with open(_conf_path, 'w') as cf:
        json.dump(conf, cf)
        

# catch when program exits, to save conf to file