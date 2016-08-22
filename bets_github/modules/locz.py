#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from gluon import *

# вернуть все переводы для данного языка и данного сопра
## bets/test/locz/en/1
def get(table, rec, lang='en'):
    rec_loc = None
    db = table._db
    table_locz_name = table._tablename[:-1] + '_loczs'
    table_locz = db[table_locz_name]
    rec_loc = db((table_locz.ref_id == rec.id)
                & (table_locz.lang == lang)).select().first()
    return rec_loc or rec
