#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
from pyzabbix import ZabbixAPI
from pprint import pprint

from logging import getLogger, basicConfig, StreamHandler, Formatter, DEBUG, INFO, WARN
basicConfig(level=INFO)

logger = getLogger(__name__)
logger.setLevel(DEBUG)

config = None

def init_zabbix_api():
    zapi = ZabbixAPI(config["zabbix"]["host"])
    zapi.login(config["zabbix"]["user"], config["zabbix"]["password"])

    logger.info("Connected zabbix successfully. API version %s" % zapi.api_version())
    return zapi

def main(name):

    myconfig = config["configs"][name]

    zapi = init_zabbix_api()

    output = {}
    for cfg in config["configs"][name]["values"]:
        # logger.debug(cfg)

        hostid = get_hostid(zapi, cfg["zabbix_host"])
        logger.debug("host " + cfg["zabbix_host"] + " is hostid " + str(hostid))
        if (hostid == None): raise RuntimeError('host not found =>' + str(cfg))

        item = get_item(zapi, hostid, cfg["zabbix_key"])
        if (item == None):
            raise RuntimeError('item not found on host =>' + str(cfg))
        else:
            logger.debug("item " + item["name"] + "(" + item["key_"] + ") is id " + str(item["itemid"]))

            if (item["lastvalue"] == None):
                raise RuntimeError('lastvalue not exist =>' + str(cfg))

        output[cfg["key"]] = item["lastvalue"]

        # lastval = get_latest_value(zapi, itemid)
        # if (lastval == None): raise RuntimeError('item has no value =>' + str(cfg))
        #output[cfg["key"]] = lastval["value"]

    write_output(output, myconfig["output_path"], myconfig["output"])
    logger.info("output done => " + myconfig["output_path"])


def write_output(output, path, type):
    if type.upper() == "JSON":
        import json
        with open(path, 'w') as json_file:
            logger.debug(json.dumps(output))
            json_file.write(json.dumps(output))
    elif type.upper() == "LTSV":
        raise NotImplementedError()
    else:
        raise NotImplementedError("unknown output type " + type)

def get_hostid(zapi, hostname):
    for h in zapi.host.get(output=["hostid", "host", "unit"], filter={"name": hostname}):
        #plogger.debug(h)
        if h["host"] == hostname:
            return h["hostid"]

    return None


def get_item(zapi, hostid, itemkey):
    logger.debug("get_item key => host " + str(hostid) + " itemkey " + itemkey )
    for itm in zapi.item.get(hostids=hostid,output=["itemid", "name", "key_", "units", "lastvalue"],
                             search={"key_":itemkey}):
        # keyが似たものが取得できてしまう？
        if itm["key_"] != itemkey:
            logger.debug("not wanted " + itm["key_"])
            continue
        # K M G に丸めるのを防止する為の ! が単位の先頭にある場合削除
        if itm["units"][0] == "!":
            itm["units"] = itm["units"][1:]

        return itm

    return None


# item.get APIで lastvalueが取れるのを知らなかったので書いた。
# もう使わない
def get_latest_value(zapi, itemid):
    for lastval in zapi.history.get(
        itemids=itemid,
        sortfield="clock",
        sortorder="DESC",
        limit=10
        ):
        logger.debug(lastval)
        return lastval

    return None

def get_config(filename):
    import yaml

    with open(filename, 'r') as yaml_file:
        conf = yaml.safe_load(yaml_file)
        return conf

if __name__ == "__main__":
    import argparse
    config_name = None

    parser = argparse.ArgumentParser(
                    description='get last value from zabbix and output to file.',
                    add_help = True
                    )
    parser.add_argument('configname', metavar='config_name', type=str,
                        help='section name to use (config.yaml)')
    args = parser.parse_args()

    config = get_config('config.yaml')
    main(args.configname)
