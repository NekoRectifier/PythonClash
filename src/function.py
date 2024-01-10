import utils
from loguru import logger
import os
import urllib.request
import urllib.error
import yaml
import subprocess


def setup():
    # TODO: check if there's a sudo permission
    _mmdb_path: str = str(utils.perf["config_dir"] + "/conf/Country.mmdb")
    _script_path: str = utils.perf["config_dir"] + "/scripts"
    shell_type: str = utils.get_shell_type()

    _mihomo_path = subprocess.getoutput("which mihomo")

    ## detect mihomo binary path
    #TODO: multiple binary mihomo detected
    if _mihomo_path.startswith("which:"):
        logger.error("No usable mihomo binary found!\nTry to download one and put it in the system path.")
        exit(1)
    else:
        logger.info("Mihomo binary detected")
        utils.perf["mihomo_path"] = _mihomo_path
        #utils.save_config(utils.perf["config_dir"], utils.perf)

    # Release Script Files
    if shell_type == "Fish":
        _path: str = os.path.expandvars('$HOME') + "/.config/fish/config.fish"
        _config_valid: bool = os.path.exists(_path)

        if _config_valid and not utils.check_string_in_file(_path, "PythonClash.fish"):
            utils.append_file("source " + os.path.join(_script_path, "/PythonClash.fish"), _path)
            logger.info("Finished adding function to shell config file...")
        elif _config_valid and utils.check_string_in_file(_path, "PythonClash.fish"):
            logger.info("Functions had been added to the shell config, skipping...")
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
            # TODO replace with something else
            urllib.request.urlretrieve(
                "https://mirror.ghproxy.com/https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb",
                _mmdb_path,
            )
        logger.info("Finished database downloading")
    else:
        logger.info("GeoIP Database exists, skipping...")
    logger.info("PythonClash Setup finished")
    utils.save_perf()


def update():
    _yml_content = {}
    _config_path: str = utils.perf['config_dir'] + "/conf/config.yaml"

    try:
        if utils.perf.get("sub_url") is not None:
            logger.info("updating config now...")
            urllib.request.urlretrieve(str(utils.perf.get("sub_url")), _config_path)
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

        if utils.perf.get("secret") is None:
            # defult secret is 'admin'
            _secret = "admin"
        else:
            _secret: str = str(utils.perf.get("secret"))

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
    utils.save_perf()


def start():
    _dir:str = str(utils.perf['config_dir'])
    _mihomo_path = str(utils.perf.get("mihomo_path"))

    if _mihomo_path == "":
        logger.error("No mihomo binary path set, please run setup first")
        exit(1)

    if not utils.is_yml_valid(os.path.join(_dir, "conf","config.yaml")):
        logger.warning("No proper configuration in the config.yaml, probable no proxy functionality")

    if not os.path.exists(str(utils.perf["config_dir"] + "/conf/Country.mmdb")):
        logger.warning("No mmdb file, probable no proxy functionality")

    if os.path.exists(_mihomo_path):
        ins_indks: list[int] = utils.detect_instance(_mihomo_path.rpartition("/")[2])
        if len(ins_indks) == 0:
            logger.info("Starting clash core...")
            subprocess.run(
                "nohup "
                + _mihomo_path
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
        logger.critical("Clash binary at " + _mihomo_path + " is not exist, exiting!")
        exit(1)
    utils.save_perf()


def stop(_target='mihomo'):
    ins_indks: list[int] = utils.detect_instance(_target)

    if len(ins_indks) == 0:
        logger.error("No Running clash instance, exiting...")
    else:
        for pid in ins_indks:
            subprocess.run("kill -9 " + str(pid), shell=True, check=True)
        logger.info("All running clash instance has been closed")
    utils.save_perf()

