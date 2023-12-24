import utils
from loguru import logger
import os

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

