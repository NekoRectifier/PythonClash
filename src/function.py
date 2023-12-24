import utils
import os

def setup():
    shell_type = utils.get_shell_type()
    if shell_type == 'Fish':
        _path = "/home/" + utils.get_curr_username() + "/.config/fish/config.fish"
        if os.path.exists(_path):
            utils.append_file("./../script/function.fish", _path)
    else:
        print("not supported to set shell functions.")
    
    print(shell_type)