#!/usr/bin/env python
# -*- coding: utf-8 -*-

def calc_trust_pay(UP_LVL, trust_level):
    if trust_level < 0: return UP_LVL[0]
    to_pay = UP_LVL[0]*UP_LVL[1]**int(trust_level)
    if to_pay > 999: to_pay = int(to_pay*0.01) * 100 - 45
    elif to_pay > 99: to_pay = int(to_pay*0.1) * 10 - 5
    return to_pay
