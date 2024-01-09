import os
import getpass
from loguru import logger
import platform
import psutil
import yaml
import pygeoip
import json

perf: dict[str, str] = {}

def get_shell_type() -> str:
    shell = os.environ.get('SHELL')
    
    if shell:
        if 'fish' in shell:
            return 'Fish'
        elif 'zsh' in shell:
            return 'Zsh'
        elif 'bash' in shell:
            return 'Bash'
    
    return 'Unknown'

def get_curr_username() -> str:
    return getpass.getuser()

def append_file(contents, target_file) -> None:
    # 打开源文件和目标文件
    with open(target_file, 'a') as target:
        target.write(contents)
    target.close()

def check_string_in_file(file_path, target_string) -> bool:
    # 打开文件并读取内容
    with open(file_path, 'r') as file:
        content = file.read()
        # 搜索目标字符串
        if target_string not in content:
            return False
        else:
            return True

def is_yml_valid(yml_obj) -> bool:
    _obj: dict[str, str] = {}
    # logger.debug(yml_obj)
    if type(yml_obj) is str:
        with open(yml_obj, 'r') as f_yml:
            _obj = yaml.load(f_yml.read(), yaml.FullLoader)
        f_yml.close()
    elif type(yml_obj) is dict:
        _obj = yml_obj
    else:
        logger.error("no valid input to 'is_yml_valid', exiting...")
        exit(1)
    
    if _obj['proxies'] is not None and _obj['proxy-groups'] is not None and _obj['rules'] is not None:
        return True
    else: 
        return False
    
    
def add_yml_custom_options(_dict: dict, _yml_data: dict) -> None:
    for key in _dict.keys():
        if _yml_data.get(key) is not _dict[key]:
            # using .get to avoid KeyError when specific key is not exist in the config dict
            _yml_data[key] = _dict[key]
            logger.info("Key '" + key + "' is updated to " + _dict[key] + " ...")
    logger.info("All custom options has been added to config file")

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

def detect_instance(process_loc) -> list[int]:
    _target_pids: list[int] = []
    for pid in psutil.process_iter():
        if pid.name().find(process_loc) != -1 or pid.pid == process_loc:
            _target_pids.append(pid.pid)
    return _target_pids

def release_script(_target_dir):
    with open(
            os.path.join(_target_dir, "PythonClash.fish"), "w"
        ) as f_fishscript:
            f_fishscript.write(
                """
function proxy_on
	export http_proxy=http://127.0.0.1:7890
	export https_proxy=http://127.0.0.1:7890
	export no_proxy=127.0.0.1,localhost
	echo -e "\033[32m[√] 已开启代理\033[0m"
end
function proxy_off
	set -e http_proxy
	set -e https_proxy
	set -e no_proxy
	set -e all_proxy
	set -e ALL_PROXY
	echo -e "\033[31m[×] 已关闭代理\033[0m"
end
                """
            )
            f_fishscript.close()

    with open(os.path.join(_target_dir, "PythonClash.bash"), "w") as f_bashscript:
        f_bashscript.write(
                """
function proxy_on() {
	export http_proxy=http://127.0.0.1:7890
	export https_proxy=http://127.0.0.1:7890
	export no_proxy=127.0.0.1,localhost
	echo -e "\033[32m[√] 已开启代理\033[0m"
}
function proxy_off(){
	unset http_proxy
	unset https_proxy
	unset no_proxy
	unset all_proxy
	unset ALL_PROXY
	echo -e "\033[31m[×] 已关闭代理\033[0m"
}
                """
            )
        f_bashscript.close()

def check_mmdb_file(path):
    if not os.path.isfile(path):
        print("文件路径无效")
        return False
    
    try:
        gi = pygeoip.GeoIP(path)
        return True
    except pygeoip.GeoIPError:
        print("无效的.mmdb文件")
        return False
    
def save_perf():
    _conf_path = str(perf.get('config_dir'))
    with open(os.path.join(_conf_path, "conf.json"), 'w') as f_conf:
        logger.debug("saving config to " + _conf_path)
        f_conf.write(json.dumps(perf))
    f_conf.close()

def init_perf(_conf_path):
    # save_perf()
    global perf
    with open(os.path.join(_conf_path, "conf.json"), 'r') as f_conf:
        con = f_conf.read()
        if con == "":
            logger.debug("conf.json is empty")
        else:
            logger.debug("reading perf, applying to perf...")
            perf = json.loads(con)
    f_conf.close()

