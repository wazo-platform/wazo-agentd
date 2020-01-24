# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests


# this function is not executed from the main thread
def self_check(config):
    port = config["port"]
    scheme = "http"
    if config["certificate"] and config["private_key"]:
        scheme = "https"

    url = "{}://{}:{}/1.0/agents".format(scheme, "localhost", port)
    try:
        return (
            requests.get(
                url, headers={'accept': 'application/json'}, verify=False
            ).status_code
            == 401
        )
    except Exception:
        return False
