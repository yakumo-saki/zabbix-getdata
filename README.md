# deprecated

Use https://github.com/yakumo-saki/zabbix-getter instead

# zabbix-getdata

Get latest data from zabbix
zabbixからデータを取得して、jsonファイルに出力します。

## つかいかた

1. config_sample.yaml をコピーして config.yaml を作成します。
2. pip install -r requirements.txt  <= 初回のみ必要
3. python zabbix-getdata.py <config.yamlのconfig名> (例： `python zabbix-getdata.py denki`

※ 環境により、 pipはpip3、pythonはpython3 の場合があります。

## config

config_sample.yaml を参照してください。

## config解説

```
zabbix:
  host: 'http://10.1.0.10/zabbix'   <= zabbix URL
  user: Admin                       <= zabbix username
  password: zabbix                  <= zabbix password
configs:
  denki:                            <= config名。yamlの仕様の範囲で任意の名前が使用可能。パラメタに指定する名前
    output: json                    <= 出力タイプ。 json のみ。
    output_path: "/tmp/denki.json"  <= jsonを出力するパス。 "" で囲んでおいてください。
    values:                         <= jsonに出力する値
      - key: "delta"                <= jsonのキー（ key:の前に - があるので、これはリストです。複数指定可能）
        zabbix_host: 'ENVIRONMENT'  <= zabbixのホスト名（ホスト一覧に表示されるホスト名（表示名ではありません）
        zabbix_key: 'denki.delta'   <= zabbixアイテムのキー名
      - key: "now_total_amp"        <= jsonに出力する2個目の要素
        zabbix_host: 'ENVIRONMENT'
        zabbix_key: 'denki.now_total_amp'
```

上記configでの出力例
`{"delta": "22807.9000", "now_total_amp": "20"}`
