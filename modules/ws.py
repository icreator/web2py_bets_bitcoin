#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon.tools import fetch
try:
    import json
except ImportError:
    from gluon.contrib import simplejson as json

def lite_wager_go(wager, LITEcash):
    url = LITEcash.url + LITEcash.go_wager % (wager.lite_wager_id, wager.lite_wager_key)
    print url
    try:
        resp = fetch(url)
        print resp
        r = json.loads(resp)
        error = r.get('error')
    except:
        error = 'fetch(%s) error!' % url

    return error
