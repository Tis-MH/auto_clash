import os
from pprint import pprint
import shutil
import requests
import argparse
import json
import yaml
import subprocess


config = json.loads(open("./config.json", encoding="utf-8").read())


def download_clash():
    if os.path.exists(os.path.join(config["deploy_path"], 'clash')):
        print(f"clash already exists under {config["deploy_path"]}")
        return None
    if "http" in config["clash_path"]:
        print('try to download clash...')
        if not config.get('download_proxy'):
            print('download_proxy is None')
        response = requests.get(
            config["clash_path"],
            proxies={
                "http": config["download_proxy"],
                "https": config["download_proxy"],
            } if config.get('download_proxy') else None,
        )
        download_path = os.path.join(
            config["deploy_path"], os.path.basename(config["clash_path"])
        )
        with open(
            download_path,
            "wb",
        ) as f:
            f.write(response.content)
        if "gz" in config["clash_path"]:
            import gzip

            with gzip.open(download_path, "rb") as f_in:
                with open(os.path.join(config["deploy_path"], "clash"), "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
    else:
        print('copy clash...')
        shutil.copyfile(config["clash_path"], config["deploy_path"])


def download_config():
    with open("./config.yaml", "w", encoding="utf-8") as f:
        response = requests.get(config["config_url"])
        f.write(response.text)


def setting_tun():
    clash_config = open("./config.yaml", encoding="utf-8").read()
    clash_config = yaml.safe_load(clash_config)
    tun_config = {
        "enable": True,
        "stack": "gvisor",
        "auto-route": True,
        "auto-detect-interface": True,
        "dns-hijack": ["any:53"],
    }
    clash_config["tun"] = tun_config
    with open("./config.yaml", "w", encoding="utf-8") as f:
        f.write(yaml.safe_dump(clash_config, allow_unicode=True))
    # pprint(clash_config)


def run():
    subprocess.run(["sudo", "./clash", "-f", "./config.yaml"])


download_clash()
setting_tun()
run()
