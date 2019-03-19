import datetime
import time
from pyzabbix import ZabbixAPI
from pprint import pprint

config = None

def init_zabbix_api():
    # ZabbixサーバーのFQDN。パス(/zabbix/api_jsonrpc.php)は不要
    zapi = ZabbixAPI(config["zabbix"]["host"])
    zapi.login(config["zabbix"]["user"], config["zabbix"]["password"])

    print("Connected to Zabbix API Version %s" % zapi.api_version())
    return zapi

def main(name):

    myconfig = config["configs"][name]

    zapi = init_zabbix_api()

    output = {}
    for cfg in config["configs"][name]["values"]:
        pprint(cfg)

        hostid = get_hostid(zapi, cfg["zabbix_host"])
        print(hostid)
        if (hostid == None): raise RuntimeError('host not found =>' + str(cfg))

        print(cfg["zabbix_key"])
        itemid = get_itemid(zapi, hostid, cfg["zabbix_key"])

        if (itemid == None): raise RuntimeError('item not found on host =>' + str(cfg))

        lastval = get_latest_value(zapi, itemid)
        if (lastval == None): raise RuntimeError('item has no value =>' + str(cfg))

        output[cfg["key"]] = lastval["value"]

    write_output(output, myconfig["output_path"], myconfig["output_type"])


def write_output(output, path, type):
    import json
    with open(path, 'w') as json_file:
        json_file.write(json.dumps(output))


def get_hostid(zapi, hostname):
    for h in zapi.host.get(output=["hostid", "host", "unit"]):
        #pprint(h)
        if h["host"] == "ENVIRONMENT":
            return h["hostid"]

    return None


def get_itemid(zapi, hostid, itemkey):
    for itm in zapi.item.get(hostids=hostid,output=["itemid", "name", "key_", "units"],
                             search={"key_":itemkey}):
        #
        if itm["units"][0] == "!":
            itm["units"] = itm["units"][1:]
        print(itm)

        return itm["itemid"]

    return None


def get_latest_value(zapi, itemid):
    for lastval in zapi.history.get(
        itemids=itemid,
        sortfield="clock",
        sortorder="DESC",
        limit=1
        ):
        print(lastval)
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

    print(args.configname)

    config = get_config('config_sample.yaml')
    pprint(config["configs"][args.configname])
    main(args.configname)
