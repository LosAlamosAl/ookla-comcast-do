#!/usr/bin/env python3

import os
import json
import subprocess
from subprocess import PIPE

from influxdb import InfluxDBClient

DB_ADDRESS = '206.189.188.186'
DB_PORT = 8086
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = 'comcast'

influxdb_client = InfluxDBClient(
    DB_ADDRESS, DB_PORT, DB_USER, DB_PASSWORD, None)


def init_db():
    influxdb_client.switch_database(DB_DATABASE)


def format_for_influx(cliout):
    data = json.loads(cliout)
    # There is additional data in the speedtest-cli output but it is likely not necessary to store.
    influx_data = [
        {
            'measurement': 'download',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['download']['bandwidth'] / 125000,
            }
        },
        {
            'measurement': 'upload',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['upload']['bandwidth'] / 125000
            }
        }
    ]

    return influx_data


def main():
    init_db()
        
    speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"], stdout=PIPE, stderr=PIPE)

    if speedtest.returncode == 0:
        print(speedtest.stdout)
        data = format_for_influx(speedtest.stdout.decode('utf-8'))
        try:
            if influxdb_client.write_points(data) == True:
                print("Info: Data written to DB successfully")
        except:
                print("Error: Data write to DB failed")
    else:
        print("speedtest error")
        print(speedtest.stderr.decode('utf-8'))
        print(speedtest.stdout.decode('utf-8'))

if __name__ == '__main__':
    main()
