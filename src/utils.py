import os
import getpass
from loguru import logger
import platform
import psutil

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

def is_yml_valid(yml_obj: dict) -> bool:
    if yml_obj['proxies'] is not None and yml_obj['proxy-groups'] is not None and yml_obj['rules'] is not None:
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

def detect_instance(process_loc) -> list:
    _target_pids = []
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