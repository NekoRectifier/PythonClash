import utils
import os

def setup():
    shell_type = utils.get_shell_type()
    if shell_type == 'Fish':
        _path = "/home/" + utils.get_curr_username() + "/.config/fish/config.fish"
        _config_valid = os.path.exists(_path)

        if _config_valid and not utils.check_string_in_file(_path, "PythonClash"):
            utils.append_file("source " + os.path.dirname(__file__) + "/../scripts/function.fish")
        elif _config_valid and utils.check_string_in_file(_path, "PythonClash"):
            print("functions had been added to the shell config file!")
        else:
            print("config file is not in default pos")
    else:
        print("not supported to set shell functions.")
