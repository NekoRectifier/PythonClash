import io
import os
import getpass
from loguru import logger
import platform
import psutil
import yaml
import pygeoip
import json
import urllib3
from tqdm import tqdm
import stat
import shutil

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
        return 'arm64'
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


def save_perf():
    _conf_path = str(perf.get('config_dir'))
    with open(os.path.join(_conf_path, "conf.json"), 'w') as f_conf:
        logger.debug("saving config to " + _conf_path)
        f_conf.write(json.dumps(perf))
    f_conf.close()


def init_perf(conf):
    # used when conf.json is already exist
    global perf

    # using r+ to read & write while pointer is at head
    with open(conf, 'r+') as f_conf:
        try:
            con = f_conf.read()
        except io.UnsupportedOperation as e:
            logger.error(e.args)
            exit(1)
        try:
            perf = json.loads(con)
            logger.info("Perf loaded")
        except json.decoder.JSONDecodeError:
            logger.warning("json config parse failed, erasing...")
            # TODO: may have a problem here
            f_conf.write("{}")
    f_conf.close()


urllib3.disable_warnings()
http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)


def vis_download(_url, _save_path):
    response = http.request('GET', _url, preload_content=False)
    total_size = int(response.headers.get('content-length', 0))
    try:
        with open(_save_path, 'wb') as file, tqdm(
                desc=_save_path,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as progress_bar:
            # 逐块写入文件并更新进度条
            for data in response.stream(1024):
                size = file.write(data)
                progress_bar.update(size)
    except OSError as e:
        logger.error(e)
        exit(1)


def extract_tar_gz(tar_gz_file, output_path):
    import tarfile
    with tarfile.open(tar_gz_file, 'r:gz') as tar:
        tar.extractall(output_path)


def decompress_gzip_file(gzip_file, output_file):
    import gzip
    with gzip.open(gzip_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            f_out.write(f_in.read())


def check_mmdb(_mmdb_path):
    try:
        pygeoip.GeoIP(_mmdb_path)
    except pygeoip.GeoIPError as e:
        logger.error(str(e.args) + "\nmmdb file is broken, please retry download")
        os.remove(_mmdb_path)
        logger.info("Broken mmdb has been removed")
        exit(1)


def modify_shell_conf(_path: str, shell_name: str):
    # currently supporting bash & fish
    _config_valid: bool = os.path.exists(_path)

    if _config_valid and not check_string_in_file(_path, "PythonClash." + shell_name):
        append_file("source " + os.path.join(perf['script_path'], "PythonClash." + shell_name), _path)
        logger.info("Finished adding function to shell config file...")
    elif _config_valid and check_string_in_file(_path, "PythonClash." + shell_name):
        logger.info("Functions had been added to the shell config, skipping...")
    else:
        logger.error("Shell " + shell_name + " has no available config file, skipping...")


def has_executable_permission(file_path):
    # 获取文件的权限模式
    file_mode = os.stat(file_path).st_mode
    # 检查文件的用户执行权限
    is_executable = bool(file_mode & stat.S_IXUSR)
    return is_executable


def is_running_python_file():
    current_file_path = os.path.abspath(__file__)
    if current_file_path.endswith(".py"):
        return True
    else:
        return False


def autostart(choice: bool):
    file_path = os.path.join(os.path.expandvars('$HOME'), '.config', 'autostart', 'pythonclash.desktop')

    if is_running_python_file():
        logger.error("Currently running with python file, autostart requires single executable file")
        exit(1)
    if os.getuid() != 0:
        with open(file_path, 'w', encoding='UTF-8') as file:
            if choice:
                file.write("[Desktop Entry]\n")
                file.write("Type=Application\n")
                file.write("Exec=\n")
                file.write("Hidden=false\n")
                file.write("NoDisplay=false\n")
                file.write("X-GNOME-Autostart-enabled=true\n")
                file.write("PythonClash\n")
            else:
                file.write("\n")
    else:
        logger.error("Autostart do not need root privillage, exiting...")
        exit(1)


def install():
    install_path = "/usr/local/bin/pclash"
    if os.getuid() == 0:
        if not is_running_python_file():
            shutil.copyfile(__file__, install_path)
            logger.info(f"Exec binary has been installed to {install_path}")
        else:
            logger.error("Currently running with python file, autostart requires single executable file")
            exit(1)
    else:
        logger.error("Install requires root privillage")
        exit(1)
