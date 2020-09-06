# -*- coding: utf-8 -*-

import time, datetime
from ws import lite_wager_go

intv = 600

# take zone
# дата тут НЕ меняется в запросе к ГЛУОН !
from gluon import current
now1 = current.request.now
now2 = datetime.datetime.now() # - со смещением делает - не верно
time_diff = now2 - now1
print 'time_zone:', time_diff

while True:
    # смещение зоны добавим
    now = datetime.datetime.now() - time_diff
    print now
    for rec in db(db.wager_to_run).select():
        #print 'test:', rec.run_dt
        if now < rec.run_dt:
            #print 'so yang'
            continue

        #print 'process...'
        wager = db.wagers[ rec.ref_id ]
        
        # в любом случае удалим из стека и закроем спор
        st = wager.status
        if st == 'NEW' or not wager.total:
            # удаляем спор вообще
            del db.wagers[ wager.id ]
            # тут стек сам удалится и все удалится связанное поэтому ПРОДОЛЖИТЬ
            db.commit()
            continue
        elif st == 'PAY':
            error = lite_wager_go( wager, LITEcash )
            if error:
                print error
                continue
            wager.update_record(status = 'RUN')
        else:
            # любой другой статус удаляем в стека просто записm
            ## error = lite_wager_go( wager, LITEcash )
            ## if error:
            ##    print error
            pass
        
        del db.wager_to_run[ rec.id ]
        db.commit()
    print 'seep', intv
    time.sleep(intv) # check every minute
