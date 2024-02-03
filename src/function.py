import pygeoip
import utils
from loguru import logger
import os
import urllib.request
import urllib.error
import yaml
import subprocess


def setup():
    # path constants
    conf_dir = utils.perf["config_dir"]

    if conf_dir is None or conf_dir == '':
        logger.debug(conf_dir)
        logger.error("perf: conf_dir is not initiated")
        exit(1)

    if not os.path.exists(os.path.join(conf_dir, "conf")):
        logger.debug("making conf dir in root conf...")
        os.mkdir(os.path.join(conf_dir, "conf"))

    _mmdb_path: str = str(conf_dir + "/conf/Country.mmdb")
    _script_path: str = conf_dir + "/scripts"
    _log_path = os.path.join(conf_dir, "logs")

    # 1. check conf folders integrity
    if not os.path.exists(_script_path):
        os.makedirs(_script_path, exist_ok=True)
    if not os.path.exists(_log_path):
        os.makedirs(_log_path)

    # saving to perf file
    utils.perf["script_path"] = _script_path
    utils.perf["log_path"] = _log_path

    # 2. check exec bin
    env_paths = os.environ.get("PATH").replace(":", " ")
    try:
        res = subprocess.run("find " + env_paths + " -name mihomo", shell=True,
                             stdout=subprocess.PIPE,
                             text=True,
                             stderr=subprocess.DEVNULL)
        # saving mihomo bin path
        if res.stdout.strip() == "":
            raise subprocess.CalledProcessError(1, "")
        _mihomo_path: str = res.stdout.strip()
        logger.info("Mihomo binary detected at " + _mihomo_path)
        utils.perf["mihomo_path"] = _mihomo_path
    except subprocess.CalledProcessError as e:
        logger.warning("mihomo binary does not exist")
        # starting mihomo binary download now
        _arch = utils.get_cpu_arch()
        bin_url = "https://github.ink/MetaCubeX/mihomo/releases/download/v1.18.0/mihomo-" + _arch + "-v1.18.0.gz"
        utils.vis_download(bin_url, os.path.join(conf_dir, "mihomo.gz"))
    # TODO: unzip the compress

    shell_type: str = utils.get_shell_type()
    # TODO: check if there's a sudo permission
    if os.getuid() == 0:
        logger.info("root permission acquired, mihomo binary will be installed in /usr/bin/")
    else:
        logger.info("mihomo will be installed in ~/.local/share/bin")
        logger.info(os.path.join(conf_dir, "mihomo.gz"))
        utils.decompress_gzip_file(os.path.join(conf_dir, "mihomo.gz"), "a.j")

    # 3. Release Script Files
    # TODO: check if its already there
    utils.release_script(_script_path)

    # Modify User Shell Script
    if shell_type == "Fish":
        _path: str = os.path.expandvars('$HOME') + "/.config/fish/config.fish"
        _config_valid: bool = os.path.exists(_path)

        if _config_valid and not utils.check_string_in_file(_path, "PythonClash.fish"):
            utils.append_file("source " + os.path.join(_script_path, "PythonClash.fish"), _path)
            logger.info("Finished adding function to shell config file...")
        elif _config_valid and utils.check_string_in_file(_path, "PythonClash.fish"):
            logger.info("Functions had been added to the shell config, skipping...")
        else:
            logger.error("Fish config file is not as intended, script in fish shell will not be usable!")
    else:
        logger.error("Not supported to set shell functions.")

    # MMDB download
    if not os.path.exists(_mmdb_path):
        logger.warning("No GeoIP Database detected in conf folder, downloading now...")
        mmdb_url = "https://cdn.jsdelivr.net/gh/Hackl0us/GeoIP2-CN@release/Country.mmdb"
        utils.vis_download(mmdb_url, _mmdb_path)
        try:
            pygeoip.GeoIP(_mmdb_path)
        except pygeoip.GeoIPError as e:
            logger.error(str(e.args) + "\nmmdb file is broken, please retry download")
            exit(1)
            # may improve here
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
            # default secret is 'admin'
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
    _dir: str = str(utils.perf['config_dir'])
    _mihomo_path = str(utils.perf.get("mihomo_path"))

    if _mihomo_path == "":
        logger.error("No mihomo binary path set, please run setup first")
        exit(1)

    if not utils.is_yml_valid(os.path.join(_dir, "conf", "config.yaml")):
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
                + str(utils.perf["log_path"])
                + "/clash.log 2>&1 &",
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
