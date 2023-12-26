import utils
from loguru import logger
import os
import urllib.request
import urllib.error
import yaml
import subprocess

def setup(_dir):
    _mmdb_path = _dir + "/conf/Country.mmdb"
    shell_type = utils.get_shell_type()


    if shell_type == 'Fish':
        _path = "/home/" + utils.get_curr_username() + "/.config/fish/config.fish"
        _config_valid = os.path.exists(_path) 

        if _config_valid and not utils.check_string_in_file(_path, "PythonClash"):
            utils.append_file("source " + _dir + "/scripts/PythonClash.fish", _path)
            logger.info("Adding function to shell config file...")
        elif _config_valid and utils.check_string_in_file(_path, "PythonClash"):
            logger.warning("Functions had been added to the shell config file, ignoring!")
        else:
            logger.error("fish config file is not in default pos")
    else:
        logger.error("not supported to set shell functions.")
    
    if not os.path.exists(_mmdb_path):
        # TODO mmdb validity check
        logger.warning("No GeoIP Database detected in conf folder")
        logger.info("Downloading database now...")
        subprocess.run("wget https://mirror.ghproxy.com/https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb -O " + _mmdb_path , shell=True)
        logger.info("Finished database downloading")

def update(_conf: dict, _dir):
    _yml_content = {}
    _config_path = _dir + "/conf/config.yaml"

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
            _secret: str = _conf["secret"]

        # custom settings
        options = {
            'mode': 'Rule',
            'external-controller': '0.0.0.0:9090',
            'external-ui': _dir + "/dashboard/public",
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
    
def start(_dir):
    clash_bin_path = _dir + "/bin/clash-" + utils.get_cpu_arch()
    if os.path.exists(clash_bin_path):
        ins_indks = utils.detect_instance(clash_bin_path.rpartition('/'))
        if len(ins_indks) == 0:
            logger.info("Starting clash core...")
            subprocess.run("nohup " + clash_bin_path + " -d " + _dir + "/conf > " + _dir + "/log/clash.log 2>&1 &", shell=True)
        else:
            logger.warning("Another clash instance is already running, killing...")
            for pid in ins_indks:
                subprocess.run("kill -9 " + str(pid), shell=True, check=True)
    else:
        logger.critical("Clash binary:" + clash_bin_path + " is not exist, exiting!")
        exit(1)

def stop():
    ins_indks = utils.detect_instance("clash-" + utils.get_cpu_arch())
    if len(ins_indks) == 0:
        logger.error("No Running clash instance, exiting...")
    else:
        for pid in ins_indks:
                subprocess.run("kill -9 " + str(pid), shell=True, check=True)
        logger.info("All running clash instance has been closed")
