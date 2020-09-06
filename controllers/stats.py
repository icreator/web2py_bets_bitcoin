# -*- coding: utf-8 -*-

if not request.is_local: raise HTTP(200, 'error')

def recalc():
    wagers_count = bets_count = 0
    for cash in db(db.cash.used==True).select():
        cash_id = cash.id
        wagers_cash = bets_cash = 0
        total = Decimal(0)
        sts = db(db.stats_cash.cash_id == cash_id).select().first()
        if not sts:
            sts = db.stats_cash[ db.stats_cash.insert( cash_id = cash_id )]
        for wager in db(db.wagers.cash_id == cash_id ).select():
            total += wager.total
            wagers_cash += 1
        sts.update_record( total = total, wagers = wagers_cash )
        wagers_count += wagers_cash

    stats = db(db.stats).select().first()
    stats.update_record( men = db(db.men).count(), wagers = wagers_count, bets = bets_count)

def index():
    h = CAT()
    for cash in db(db.cash.used==True).select():
        cash_id = cash.id
        sts = db(db.stats_cash.cash_id == cash_id).select().first()
        if not sts: continue
        h += SPAN(' ', round(float(sts.total),6),
            IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''))
    return dict(h=h)
