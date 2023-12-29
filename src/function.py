import utils
from loguru import logger
import os
import urllib.request
import urllib.error
import yaml
import subprocess


def setup(conf_dict: dict):
    # TODO: check if there's a sudo permission
    _mmdb_path: str = str(conf_dict["config_dir"] + "/conf/Country.mmdb")
    _script_path: str = conf_dict["config_dir"] + "/scripts"
    shell_type: str = utils.get_shell_type()

    if not os.path.exists(conf_dict["config_dir"] + "/scripts/PythonClash.fish"):
        # Release Script Files
        logger.info("Creating shell script...")
        os.makedirs(_script_path, exist_ok=True)
        utils.release_script(_script_path)

    if shell_type == "Fish":
        _path: str = os.path.expandvars('$HOME') + "/.config/fish/config.fish"
        _config_valid: bool = os.path.exists(_path)

        if _config_valid and not utils.check_string_in_file(_path, "PythonClash.fish"):
            utils.append_file("source " + os.path.join(_script_path, "/PythonClash.fish"), _path)
            logger.info("Finished adding function to shell config file...")
        elif _config_valid and utils.check_string_in_file(_path, "PythonClash.fish"):
            logger.info("Functions had been added to the shell config")
        else:
            logger.error("Fish config file is not as intended, script in fish shell will not be usable!")
    else:
        logger.error("Not supported to set shell functions.")

    if not os.path.exists(_mmdb_path):
        # TODO mmdb validity check
        logger.warning("No GeoIP Database detected in conf folder")
        try:
            logger.info("Downloading database now, please wait...")
            subprocess.run(
                "wget https://mirror.ghproxy.com/https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb -O "
                + _mmdb_path,
                shell=True,
                check=True,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            logger.warning(
                "'wget' is not usable, try to download with builit in urllib..."
            )
            urllib.request.urlretrieve(
                "https://mirror.ghproxy.com/https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb",
                _mmdb_path,
            )
        logger.info("Finished database downloading")
    else:
        logger.info("GeoIP Database exists")
    logger.info("PythonClash Setup finished")
    # TODO, download clash core 


def update(conf_dict: dict):
    _yml_content = {}
    _config_path: str = conf_dict['config_dir'] + "/conf/config.yaml"

    try:
        if conf_dict.get("sub_url") is not None:
            logger.info("updating config now...")
            urllib.request.urlretrieve(str(conf_dict.get("sub_url")), _config_path)
        else:
            logger.error("Subscription URL haven't been set. Exiting...")
            exit(1)
    except urllib.error.URLError:
        logger.error("URL cannot be connected")
        exit(1)

    with open(_config_path) as f:
        _secret = ""
        _content: str = f.read()  # may have a ram problem
        _yml_content: dict = yaml.load(_content, yaml.FullLoader)
    f.close()

    # config validity check
    # slow...
    if utils.is_yml_valid(_yml_content):
        logger.debug("downloaded config seems valid")

        if conf_dict.get("secret") is None:
            # defult secret is 'admin'
            _secret = "admin"
        else:
            _secret: str = str(conf_dict.get("secret"))

        # custom settings
        options: dict[str, str] = {
            "mode": "Rule",
            "external-controller": "0.0.0.0:9090",
            # "external-ui": _dir + "/dashboard/public",
            # currently do not support local external ui panel
            "secret": _secret,
        }
        utils.add_yml_custom_options(options, _yml_content)

        # saving yaml to file now
        with open(_config_path, "w") as f:
            yaml.dump(_yml_content, f)
            logger.info(
                "modifications on config yaml has been made to file, you may start the clash now"
            )

    else:
        # TODO: base64 config file support
        logger.critical("downloaded config is corrupted!")
        exit(1)


def start(conf_dict):
    _dir:str = str(conf_dict['config_dir'])
    clash_bin_path: str = "/usr/local/bin/mihomo"

    if not utils.is_yml_valid(os.path.join(_dir, "config.yaml")):
        logger.warning("No proper configuration in the config.yaml, probable no proxy functionality")

    if not os.path.exists(str(conf_dict["config_dir"] + "/conf/Country.mmdb")):
        logger.warning("No mmdb file, probable no proxy functionality")

    if os.path.exists(clash_bin_path):
        ins_indks: list[int] = utils.detect_instance(clash_bin_path.rpartition("/")[2])
        if len(ins_indks) == 0:
            logger.info("Starting clash core...")
            subprocess.run(
                "nohup "
                + clash_bin_path
                + " -d "
                + _dir
                + "/conf > "
                + _dir
                + "/log/clash.log 2>&1 &",
                shell=True,
            )
        else:
            logger.warning("Other clash instance is already running, killing...")
            stop()
    else:
        logger.critical("Clash binary at " + clash_bin_path + " is not exist, exiting!")
        exit(1)


def stop(_target='mihomo'):
    ins_indks: list[int] = utils.detect_instance(_target)

    if len(ins_indks) == 0:
        logger.error("No Running clash instance, exiting...")
    else:
        for pid in ins_indks:
            subprocess.run("kill -9 " + str(pid), shell=True, check=True)
        logger.info("All running clash instance has been closed")
