import utils
from loguru import logger
import os
import urllib.request
import urllib.error
import yaml

def setup(_dir):
    shell_type = utils.get_shell_type()
    if shell_type == 'Fish':
        _path = "/home/" + utils.get_curr_username() + "/.config/fish/config.fish"
        _config_valid = os.path.exists(_path) 

        if _config_valid and not utils.check_string_in_file(_path, "PythonClash"):
            utils.append_file("source " + _dir + "/scripts/PythonClash.fish", _path)
            logger.info("adding function to shell config file...")
        elif _config_valid and utils.check_string_in_file(_path, "PythonClash"):
            logger.warning("functions had been added to the shell config file!")
        else:
            logger.error("config file is not in default pos")
    else:
        logger.error("not supported to set shell functions.")

def update(_conf: dict, _main_dir):
    _yml_content = {}
    _config_path = _main_dir + "/conf/config.yaml"

    try:
        if _conf.get('sub_url') is not None:
            logger.info("updating config now...")
            urllib.request.urlretrieve(str(_conf.get('sub_url')), _config_path)
        else:
            logger.error("URL haven't been set. Exiting...")
            exit(1)
    except urllib.error.URLError:
        logger.error('URL cannot be connected')

    with open(_config_path) as f:
        _secret = ''
        _content = f.read() # may have a ram problem
        _yml_content = yaml.load(_content, yaml.FullLoader)
    f.close()

    # config validity check
    # slow...
    if utils.is_yml_valid(_yml_content):
        logger.debug("downloaded config seems valid")

        if _conf['secret'] is None:
            # defult secret is 'admin'
            _secret = 'admin'
        else:
            _secret = _conf["secret"]

        # custom settings
        options = {
            'mode': 'Rule',
            'external-controller': '0.0.0.0:9090',
            'external-ui': _main_dir + "/dashboard/public",
            'secret': _secret,
        }
        utils.add_yml_custom_options(options, _yml_content)

        # saving yaml to file now
        with open(_config_path, 'w') as f:
            yaml.dump(_yml_content, f)
            logger.info("modifications on config yaml has been made to file")

    else:
        # TODO: base64 config file support
        logger.critical("downloaded config is corrupted!")
        exit(1)
    

    

