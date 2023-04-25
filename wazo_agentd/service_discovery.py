# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests


# this function is not executed from the main thread
def self_check(config):
    port = config["port"]
    scheme = "http"
    if config["certificate"] and config["private_key"]:
        scheme = "https"

    url = f"{scheme}://{'localhost'}:{port}/1.0/agents"
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers, verify=False)
        return response.status_code == 401
    except Exception:
        return False
