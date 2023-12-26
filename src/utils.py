import os
import getpass
from loguru import logger
import platform
import psutil

def get_shell_type():
    shell = os.environ.get('SHELL')
    
    if shell:
        if 'fish' in shell:
            return 'Fish'
        elif 'zsh' in shell:
            return 'Zsh'
        elif 'bash' in shell:
            return 'Bash'
    
    return 'Unknown'

def get_curr_username():
    return getpass.getuser()

def append_file(contents, target_file):
    # 打开源文件和目标文件
    with open(target_file, 'a') as target:
        target.write(contents)
    target.close()

def check_string_in_file(file_path, target_string):
    # 打开文件并读取内容
    with open(file_path, 'r') as file:
        content = file.read()
        # 搜索目标字符串
        if target_string not in content:
            return False
        else:
            return True
    file.close()

def is_yml_valid(yml_obj: dict):
    if yml_obj['proxies'] is not None and yml_obj['proxy-groups'] is not None and yml_obj['rules'] is not None:
        return True
    else: 
        return False
    
def add_yml_custom_options(_dict: dict, _yml_data: dict):
    for key in _dict.keys():
        if _yml_data[key] is not _dict[key]:
            _yml_data[key] = _dict[key]
            logger.info("Key " + key + " is updated to " + _dict[key] + " ...")
    logger.info("yml custom options has been added")

def get_cpu_arch() -> str:
    name = platform.machine()
    if name == 'AMD64':
        return 'windows-amd64'
    elif name == 'x86_64':
        return 'linux-amd64'
    elif name == 'aarch64':
        return name
    else:
        logger.error("Can't determine current cpu architechure, exiting...")
        exit(1)

def detect_instance(process_loc) -> list:
    _target_pids = []
    for pid in psutil.process_iter():
        if pid.name().find(process_loc) != -1 or pid.pid == process_loc:
            _target_pids.append(pid.pid)
    return _target_pids