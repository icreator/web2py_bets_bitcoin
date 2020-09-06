# -*- coding: utf-8 -*-

response.view = 'generic.json'

def up_man(order):
    if order.tab != 'men':
        return 'not tab == "men"'
    
    # это оплата повышения уровня
    man = db.men[ order.ref_id ]
    if not man:
        return 'not found man'
    
    if man.up_order != order.id:
        return 'up_order != order.id'
        
    from gluon.tools import fetch
    url = LITEcash.url + LITEcash.check % ('%s.%s' % (order.bill_id, order.skey))
    #print url
    resp = fetch(url)
    #print resp
    import gluon.contrib.simplejson as sj
    res = sj.loads(resp) # {'bill': bill_id }
    err = res.get('error')
    if err:
        return '%s' % err
    
    status = res['status']
    if status == 'CLOSED':
        from decimal import Decimal
        # обновление только 1 раз при наступлении статуса и сразу удалим заказ
        man.update_record( up_order = None, trust = man.trust + Decimal(1))
    elif status in ['EXPIRED', 'INVALID']:
        # забудем это заказ
        man.update_record( up_order = None)
    
    order.update_record( status = status )
    return status
    

## for LITE.cahs note_url = "check/index?"
## back_url to order = "hand/index?cond="
### 
def index():
    bill_id = request.vars.get('bill')
    if not bill_id: return
    order_id = request.vars.get('order')

    if order_id.startswith('up_'):
        # это оплата поднятия доверия
        order = db(db.orders.bill_id == bill_id).select().first()
        if order:
            # и если такой заказ найден то
            return up_man(order)
    
    cond = db(db.wager_conds.bill_id == bill_id).select().first()
    if not cond: return 'cond not found'
    
    from gluon.tools import fetch
    url = LITEcash.url + LITEcash.check % bill_id + '?status=SOFT'
    #print url
    resp = fetch(url)
    #print resp
    import gluon.contrib.simplejson as sj
    res = sj.loads(resp) # {'bill': bill_id }
    err = res.get('error')
    if err:
        return '%s' % err

    if cond.total != Decimal(res['payed']):
        cond.update_record( total = res['payed'] )
        wager_id = cond.wager_id
        wager = db.wagers[ wager_id ]
        sum1 = db.wager_conds.total.sum()
        sum2 = db(db.wager_conds.wager_id == wager_id ).select(sum1).first()[sum1]
        wager.update_record( total = sum2 )
        man = db.men[ wager.man_id ]
        man.update_record( activity = man.activity + 1 )
    
    return '%s' % res
