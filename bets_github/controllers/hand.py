# -*- coding: utf-8 -*-
import locz

class Jammer():
    def read(self,n): return 'x'*n
def jam(): return response.stream(Jammer(),40000)

def get_title_descr(wr_loc):
    return T('Bitcoin bets') + ' - ' + wr_loc.name, wr_loc.descr or T('Wager with bitcoin bets')

def fa_status(status, xml=None):
    fa = 'play'
    if status == 'NEW':
        fa = 'pause'
    elif status == 'PAY':
        fa = 'play'
    elif status == 'RUN':
        fa = 'forward'
    else:
        fa = 'eject'
    return xml and XML('<i class="fa fa-' + fa + '"></i> ') or 'fa fa-' + fa

def make_mess(wager, cond):
    import urllib
    #return urllib.urlencode({'name':cond.name})
    return urllib.quote(('WAGER #%s: ' % wager.id) + wager.name + ', condition: [' + cond.name + ']')

def lite_wager_end(wager, winned):
    from gluon.tools import fetch

    args = ''
    for w in winned:
        cond = db.wager_conds[ w ]
        if not cond: continue
        args += '%s/' % cond.bill_id
    url = LITEcash.url + LITEcash.end_wager % (wager.lite_wager_id, wager.lite_wager_key, args)
    #print url
    resp = fetch(url)
    import gluon.contrib.simplejson as sj
    res = sj.loads(resp)
    return res

import ws

def make_bill():

    cond_id = request.args(0) #, _target='_blank'
    if not cond_id:
        jam()
        return T('Cond_id empty')

    wager_cond = db.wager_conds[ cond_id ]
    if not wager_cond:
        jam()
        return T('wager_Cond not found')
    bill_id = wager_cond.bill_id

    if not bill_id:
        from gluon.tools import fetch
        if not wager_cond.wager_id:
            mess = 'wager_is is None for wager_cond[%]' % wager_cond
            return dict(err=mess + ' please contact with support')

        wager = db.wagers[ wager_cond.wager_id ]
        if not wager.lite_wager_id:
            mess = 'lite_wager_id is None for wager[%s]' % wager.id
            return dict(err=mess + ' please contact with support')

        url = LITEcash.url + LITEcash.make % (
            wager.lite_wager_id, wager.lite_wager_key, wager_cond.id,
            wager.def_bet or 0.1,
            make_mess(wager, wager_cond)
            )
        print url
        resp = fetch(url)
        print resp
        import gluon.contrib.simplejson as sj
        res = sj.loads(resp) # {'bill': bill_id }
        err = res.get('error')
        if err:
            return dict(err=err)

        bill_id = res['bill']
        #print 'bill_id :', bill_id
        wager_cond.update_record( bill_id = bill_id )

    redirect(LITEcash.url + LITEcash.show % bill_id )

def add_cond(wager_id):

    form = FORM( # заставит по Enter запускасть событие клика на BUTTON
        LABEL(T('For add a condition for Bets set name for it condition')),
        INPUT(_name='name', _placeholder=T('Type Name of Condition'),
           _id='ttt', _autofocus=1,
           _style_1='padding-left:50px;width:9em;'),
        BUTTON(T('Add a condition'), _name='cond_add_btn',
           _type='_submit',
           _class='btn btn-' + CLRS.btn, _id='cond_add_btn',
           ),
        #_action="javascript: void(0);" ## не перегружает страницу при нажатии на кнопку SUBMIT
        )

    if form.accepts(
            request, session, formname='add_cond',
            keepvalues=True, onvalidation=None,
            dbio=False, hideerror=False
            ):
        name = form.vars.name
        if len(name) == 0:
            mess = T('Name is emty')
            form.errors.name = mess
            response.flash = T('Input name please')
        else:
            cond = db((db.wager_conds.wager_id == wager_id)
                & (db.wager_conds.name == name)).select().first()
            if cond:
                mess = T('Condition [%s] already exist!') % name
                response.flash = SPAN(mess, _class='warn')
                form.errors.name = mess
            else:
                cond_id = db.wager_conds.insert( wager_id = wager_id, name = name )
                response.flash = SPAN(T('Condition [%s] added') % name, _class='succes')
                response.js = "jQuery('#show_conds').get(0).reload();"
                if session.wager_new:
                    # если было пустой спор еще - без условий
                    response.js += "jQuery('#show_wager').get(0).reload();"

    return form

def show_conds():

    wager_id = request.args(0)
    wager = wager_id and db.wagers[ wager_id ]
    if not wager: return ''

    h=CAT(
            SCRIPT("""
            if ( ! $('#show_conds').is(':visible')) {
                $('#show_conds').animate({ height: 'show' }, 1000);
            }
            """)
        )

    status = wager.status
    h += DIV(
        DIV(T('List of Conditions for'),' ',
            A(T('WAGER #%s') % wager_id,
                _href=URL('hand','make', args=[wager_id]), _class='btn btn-' + CLRS.btn),
            ' ',T('status'), ' [', fa_status(status, 1), status, ']',
            _class='col-sm-8'),
        DIV(P(A(T('Other Wagers'), _href=URL('hand','list'), _class='btn btn-' + CLRS.btn),
                _class='pull-right'),
            _class='col-sm-4'),
        _class='row')
    if status == 'PAY':
        h += DIV(P(T('ATTENTION!!! You must to pay only from your addresses and local wallets! Online wallets and accounts of exchanges are not supported.')),
            _class='row')

    h_reload = SPAN(A(TAG.i(_class='fa fa-refresh bbig'), # fa-spin
                      _onclick="""
                $(this).addClass('fa-spin');
                jQuery('#show_wager').get(0).reload();
                jQuery('#show_conds').get(0).reload();
                            """,
                      _class='btn circ btn-' + CLRS.btn2),
                    _class='pull-right')
    if status == 'NEW':
        hh = (DIV(P(B(T('Name')), _class='header'), _class='col-sm-4'))
    elif status == 'PAY':
        hh = (DIV(P(B(T('Click to make a BET')), _class='header'), _class='col-sm-7'),
              DIV(P(B(T('Total Bet')), _class='header'), _class='col-sm-3'),
              DIV(h_reload, T('Win Ratio'), _class='col-sm-2'))
    elif status == 'RUN':
        # загрузим стили для кнопок
        ## тут не пашет response.files.append(URL('static','css/chechbox.css'))
        hh = (DIV(P(B(T('Winned')), _class='header'), _class='col-sm-1'),
              DIV(P(B(T('Name')), _class='header'), _class='col-sm-6'),
              DIV(P(B(T('Total Bet')), _class='header'), _class='col-sm-3'),
              DIV(h_reload, T('Win Ratio'), _class='col-sm-2'))
    else:
        hh = (DIV(P(B(T('Name')), _class='header'), _class='col-sm-4'),
                 DIV(B(T('Stats')), _class='col-sm-4'),
                 DIV(B(T('Payed')), _class='col-sm-3'))
    hh = DIV( CAT(hh), _class='row')

    conds_payed = []
    for cond in db(db.wager_conds.wager_id == wager_id).select():
        wcond_loc = locz.get(db.wager_conds, cond, lang_curr)

        if status == 'NEW':
            hh += DIV(DIV(wcond_loc.name, _class='col-sm-5'),
                      DIV(wcond_loc.name, _class='col-sm-2'),
                      _class='row')
        elif status == 'PAY':
            bill_id = cond.bill_id
            ratio = (not cond.total or not wager.total) and 100 or float(wager.total / cond.total)
            if ratio > 100: ratio = int(ratio)
            elif ratio > 10: ratio = round(ratio,1)
            else: ratio = round(ratio,2)
            if bill_id:
                aa = A(wcond_loc.name, _href=LITEcash.url + LITEcash.show % bill_id,
                          _target='_blank', _class='col-sm-11 btn_a pay_btn inv')
                conds_payed.append( cond.total )
            else:
                aa = A(wcond_loc.name, _href=URL('hand','make_bill', args=[cond.id]),
                          _target='_blank', _class='col-sm-11 btn_a pay_btn inv')
            hh += DIV(DIV(aa, _class='col-sm-7'),
                      DIV(H3(cond.total), _class='col-sm-3'),
                      DIV(H3('x',ratio), _class='col-sm-2'),
                      _class='row')
        elif status == 'RUN':
            ratio = (not cond.total or not wager.total) and 100 or float(wager.total / cond.total)
            if ratio > 100: ratio = int(ratio)
            elif ratio > 10: ratio = round(ratio,1)
            else: ratio = round(ratio,2)
            hh += DIV(DIV(
                        DIV(INPUT(_type='checkbox', _id=cond.id, _name='winned', _value=cond.id, _form='form_go'),
                            LABEL( _for=cond.id),
                            _class='squaredOne pull-right'),
                        _class='col-sm-1'),
                      DIV(wcond_loc.name, _class='col-sm-6'),
                      DIV(cond.total,
                          cond.bill_id and A(TAG.i(_class='fa fa-info-circle bbig'),
                                _href=LITEcash.url + LITEcash.info % cond.bill_id, _target='_blank') or '',
                          _class='col-sm-3'),
                      DIV(H3('x',ratio), _class='col-sm-2'),
                      _class='row')
        else:
            hh += DIV(DIV(wcond_loc.name, _class='col-sm-6'),
                      DIV(cond.winned and B(T('Winner!')) or '', _class='win col-sm-2'),
                      DIV(cond.total,
                          cond.bill_id and A(TAG.i(_class='fa fa-info-circle bbig'),
                                _href=LITEcash.url + LITEcash.info % cond.bill_id, _target='_blank') or '',
                                #_href=URL('api_bill', 'info', host=LITEcash.url,
                                #    args=[cond.bill_id], vars={'get_payouts':1}), _target='_blank') or '',
                        _class='col-sm-4'),

                      _class='row')

    h += DIV(hh, _class = 'game_stats row')

    # только для хозяина разрешим это
    if status == 'NEW' and session.man_id == wager.man_id:
        h += add_cond(wager_id)
    ##elif status == 'NEW' and len(conds_payed)<2

    return h

def fa_icons(fa_icon, val):
    h = CAT()
    for i in range(val):
        h += TAG.i(_class='fa ' + fa_icon)
    return h

def show_wager():
    wager_id = request.args(0)
    wager = wager_id and db.wagers[ wager_id ]

    h = CAT(
        SCRIPT("""
            if ( ! $('#show_wager').is(':visible')) {
                $('#show_wager').animate({ height: 'show' }, 1000);
            }
            """)
        )

    if not wager:
        h +=  wager_id and T('Wager [%s] not found') % wager_id or ''
        return h


    status = wager.status
    if wager.run_dt and status in ['NEW', 'PAY']:
        h += DIV(T('Auto run on'),': ', SPAN(wager.run_dt, _class='inv'))
    #lang = session.lang or request.env.http_accept_language
    #print lang
    w_cat = locz.get(db.w_cats, db.w_cats[wager.w_cat_id], lang_curr)
    wr_loc = locz.get(db.wagers, wager, lang_curr)
    wl_name = wr_loc.name
    ## тут это не работает так как это по аяксу
    ## response.meta_title = wl_name
    h_name = DIV(H3(
                 wl_name,
                 _itemprop='name', # название события длля микроразметки поисковиков
                _class='ask'),
             _class='col-sm-9')
    h_descr = wr_loc.descr and DIV(XML(wr_loc.descr),
                                      _itemprop='description', # микроразметка для поисковиков и социалки
             _class='row') or ''
    s_url = URL('hand','make', args=[wager_id], scheme=True, host=True)
    title, descr = get_title_descr(wr_loc)
    twit = 'http://twitter.com/home?status='+title+'%20'+ s_url;
    facebook = 'http://www.facebook.com/sharer.php?u=' + s_url;
    gplus = 'https://plus.google.com/share?url=' + s_url;
    h_social = DIV(
            A(IMG(_src=URL('static','images/twitter.png'), _alt="Share on Twitter", _width="32", _height="32", _style='margin: 2px 5px;'),
              _target='_blabk', _href=twit, _id="twit", _title="Share on twitter"),
            A(IMG(_src=URL('static','images/facebook.png'), _alt="Share on facebook", _width="32", _height="32", _style='margin: 2px 5px;'),
              _target='_blabk', _href=facebook, _id="facebook", _title="Share on facebook"),
            A(IMG(_src=URL('static','images/gplus-32.png'), _alt="Share on Google Plus", _width="32", _height="32", _style='margin: 2px 5px;'),
              _target='_blabk', _href=gplus, _id="twit", _title="Share on Google Plus"),
            _class='pull-right'
        )


    if wager.man_id == session.man_id:
        h_man = DIV(P(T('Your is maker'), _class='header'), h_social, _class='col-sm-2 pull-right')
        h += DIV(h_name, h_man, _class='row')
        h += h_descr
    else:
        # это не хозяин спора - запретиа все редактирования
        man = db.men[ wager.man_id ]

        h_man =  DIV(P(A(man.name, _href=URL('man', 'index', args=[wager.man_id])), _class='header'),
                     P(fa_icons('fa-heart green', man.trust), _class='header'),
                     h_social,
                     _class='col-sm-3 pull-right')
        h += DIV(h_name, h_man, _class='row')
        h += h_descr
        return h

    conds = db(db.wager_conds.wager_id == wager_id).select()
    conds_cnt = len(conds)
    if conds_cnt < 2:
        # позволим открыть кнопку только когда добавлено 2-е условие
        session.wager_new = True
    else:

        # только когда 2 условия готовы
        go_btn = status == 'NEW' and 'Go to PAY' or status == 'PAY' and 'Go to RUN' or status == 'RUN' and 'Go to END'
        go_lbl = status == 'NEW' and 'If all conditions is setted click' or status == 'PAY' and 'If all Bets is made click' or status == 'RUN' and 'If the winners decided, select them and press'
        if status == 'PAY' and wager.total <= 0:
            go_btn = None
            h += DIV(T('Wager can not be runned - bet total is null!'))
        if go_btn:
            form_go = FORM(T(go_lbl), ': ', BUTTON(B(T(go_btn)), _type='submit', _class='btn-' + CLRS.btn),
                           formname='form_go', _id='form_go')
            h += BR()
            h += DIV(DIV(form_go, _class='col-sm-12'), _class='row')

            if wager.man_id != session.man_id: return h # дополнительная защита - если кто вручную форму создал
            if form_go.accepts(request, formname='form_go'):
                if status == 'NEW':
                    status = 'PAY'
                elif status == 'PAY':
                    ## запускаем на сервисе
                    ## выдаст ошибку или False при успехе
                    mess = ws.lite_wager_go(wager, LITEcash) or T('Wager was closed for payments and awaiting resolve now')
                    response.flash = '%s' % mess
                    status = 'RUN'
                elif status == 'RUN':
                    # тут должны быть заданы победители
                    winned = request.vars.winned ## в форме нету их - из реквайст только
                    if winned and winned.isdigit():
                        if type(winned) != type([]): winned = [winned]
                        res = lite_wager_end( wager, winned )
                        err = res.get('error')
                        if err:
                            response.flash = err
                            return h

                        for w in winned:
                            db.wager_conds[w].update_record( winned = True )
                        response.flash = res
                        status = 'END'
                    else:
                        response.flash = T('Winned conditions not selected!')
                        return h
                wager.update_record(status = status)
                response.js =  "$('#show_wager').hide();"
                response.js += "$('#show_conds').hide();"
                response.js += "jQuery('#show_wager').get(0).reload();"
                response.js += "jQuery('#show_conds').get(0).reload();"
                return # не нужно ничего возвращатьтак как перегрузка все равно начнктся

    return h

# создадим спор на службе LITE.cash
def make_lt_wager(wager, cash, man):

    if True:

        from gluon.tools import fetch
        ##print LITEcash.url, LITEcash.make_wager % cash.cash_name
        url = LITEcash.url + LITEcash.make_wager % cash.cash_name
        #%(fee)s
        #print url
        #return 'test'

        mam_acc = db((db.man_accs.man_id == man.id)
                & (db.man_accs.cash_id == cash.id)).select().first()
        if not mam_acc:
            return 'Wallet address not found for [%s], please set it in Your cabinet' % cash.name

        resp = fetch(url, { 'fee':settings.serv_fee, 'm_fee': man.fee, 'm_addr': mam_acc.acc})
        #print resp
        import gluon.contrib.simplejson as sj
        res = sj.loads(resp) # {'wager': wager_id, 'key': key }
        err = res.get('error')
        if err: return err
        wager_lt_id = res['wager']
        wager_lt_key = res['key']
    else:
        wager_lt_id = wager.id
        wager_lt_key = 'key'

    wager.update_record(
        lite_wager_id = wager_lt_id,
        lite_wager_key = wager_lt_key,
        )

def insert_wager(req, sess, quick_btn):

    name = sess.wager_name or '---'
    w_cat_id = int(quick_btn and 1 or req.vars.w_cat_id or 2) # или "другое"
    if w_cat_id < 0:
        # это перевод на язык
        w_cat_id = db.w_cat_loczs[ -w_cat_id ].ref_id

    if quick_btn:
        # сщздадим имена команд
        numbs = req.vars.numbs
        numbs = numbs and numbs.isdigit() and int(numbs)
        if numbs < 2: return
        elif numbs > 8: return
        sess.teams_numbs = numbs
        name = '%s x %s' % (quick_btn, numbs)
    tags = req.vars.tags


    run_dt = req.vars.run_dt

    wager_id = db.wagers.insert(
        cash_id = sess.cash_id,
        man_id = sess.man_id, man_name = sess.man_name,
        status = 'NEW',
        w_cat_id = w_cat_id,
        name = name,
        run_dt = run_dt,
        descr = req.vars.descr,
        tags = tags,
        def_bet = sess.def_bet,
        )
    if run_dt:
        # запомним в стеке чтобы проверять по циклу
        db.wager_to_run.insert( ref_id = wager_id, run_dt = run_dt )

    if tags:
        for tag in tags.split(','):
            tag = tag.strip().lower()
            if not tag: continue
            #print '[%s]' % tag
            rec = db(db.tags.name.lower() == tag).select().first()
            if rec:
                rec.update_record( uses = rec.uses + 1)
            else:
                db.tags.insert(name = tag)

    if quick_btn:
        # сщздадим имена команд
        if quick_btn == 'team':
            names = []
            for i in range(numbs):
                names.append('Team %s' % (i+1))
        elif quick_btn == 'color':
            names = ['Red', 'Green', 'Orange', 'Blue', 'Black', 'White'][:numbs]
        else:
            names = ['Good guys', 'Bad guys', 'Amazing guys', 'Poor guys', 'Crazy guys', 'Mage guys'][:numbs]

        for name in names:
            db.wager_conds.insert( wager_id = wager_id, name = name )

        db.wagers[ wager_id ].update_record( status = 'PAY' )

    return wager_id

def list_get_rec_html(wr, fa, odd):
        #w_cat = locz.get(db.w_cats, db.w_cats[wr.w_cat_id], lang)
        wr_loc = locz.get(db.wagers, wr, lang)

        cash = db.cash[ wr.cash_id ]
        cash_i = SPAN(IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''),
                      #' ', SPAN(cash.name, _class='small'),
                      )
        ## w_cat.name,': ',
        run_dt = wr.status == 'PAY' and wr.run_dt
        if run_dt:
            import datetime
            name = CAT(SPAN(run_dt.date(), _class='inv'), ' ', wr_loc.name)
        else:
            name = wr_loc.name

        h = DIV(DIV(A(XML('<i class="fa fa-%s"></i> ' % fa), name, _href=URL('hand','make',args=[wr.id])), _class='col-sm-8'),
                 #DIV(wr.status, _class ='col-sm-1'),
                 #DIV(cash_i, _class ='col-sm-3'),
                 #DIV(cash_i, _class ='col-sm-3'),
                 DIV(cash_i, round(float(wr.total),6), _class ='col-sm-2'),
                 DIV(A(wr.man_name, _href=URL('man','index',args=[wr.man_id]), _class='small'), _class='col-sm-2'),
                 _class='row' + (odd and ' odd' or ''))
        return h
def list_get_new(h, odd=None, pars={}, lang='en'):
    sel_man_id = pars.get('man')
    quick = tags = session.wlist_flt
    quick = quick == 1
    # поиск через contains(tags,  all=True, case_sensitive=False) - всех меток в одном споре
    tags = type(tags) == type('') and tags.split(',')
    for wr in db((db.wagers.status == 'NEW')
                 & (not sel_man_id or db.wagers.man_id == sel_man_id)
                 & (not quick or db.wagers.w_cat_id==1)
                 & (not tags or db.wagers.tags.contains(tags,  all=True, case_sensitive=False))
                 ).select(orderby=~db.wagers.id):
        odd = not odd

        '''
        w_cat = locz.get(db.w_cats, db.w_cats[wr.w_cat_id], lang)
        wr_loc = locz.get(db.wagers, wr, lang)

        cash = db.cash[ wr.cash_id]
        cash_i = SPAN(IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''),
                      #' ', SPAN(cash.name, _class='small'),
                      )
        ## w_cat.name,': ',
        h += DIV(DIV(A(XML('<i class="fa fa-pause"></i> '), wr_loc.name, _href=URL('hand','make',args=[wr.id])), _class='col-sm-5'),
                 DIV(A(wr.man_name, _href=URL('man','index',args=[wr.man_id])), _class='col-sm-2'),
                 #DIV(wr.status, _class ='col-sm-1'),
                 #DIV(cash_i, _class ='col-sm-3'),
                 #DIV(cash_i, _class ='col-sm-3'),
                 DIV(cash_i,wr.total, _class ='col-sm-2'),
                 _class='row' + (odd and ' odd' or ''))
        '''
        h += list_get_rec_html(wr, 'pause', odd)

    return h, odd

def list_get_pay(h, odd=None, pars={}, lang='en'):
    sel_man_id = pars.get('man')
    quick = tags = session.wlist_flt
    quick = quick == 1
    # поиск через contains(tags,  all=True, case_sensitive=False) - всех меток в одном споре
    tags = type(tags) == type('') and tags.split(',')
    total = 0
    for wr in db((db.wagers.status == 'PAY')
                 & (not sel_man_id or db.wagers.man_id == sel_man_id)
                 & (not quick or db.wagers.w_cat_id==1)
                 & (not tags or db.wagers.tags.contains(tags,  all=True, case_sensitive=False))
                 ).select(orderby=~db.wagers.id):
        odd = not odd

        '''
        w_cat = locz.get(db.w_cats, db.w_cats[wr.w_cat_id], lang)
        wr_loc = locz.get(db.wagers, wr, lang)

        cash = db.cash[ wr.cash_id]
        cash_i = SPAN(IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''),
                      #' ', SPAN(cash.name, _class='small')
                      )
        ## w_cat.name,': ',
        h += DIV(DIV(A(XML('<i class="fa fa-play"></i> '), wr_loc.name, _href=URL('hand','make',args=[wr.id])), _class='col-sm-7'),
                 #DIV(wr.status, _class ='col-sm-1'),
                 ## forward
                 #DIV(cash_i, _class ='col-sm-3'),
                 #DIV(cash_i, _class ='col-sm-3'),
                 DIV(cash_i,wr.total, _class ='col-sm-2'),
                 DIV(A(wr.man_name, _href=URL('man','index',args=[wr.man_id])), _class='col-sm-2'),
                 _class='row' + (odd and ' odd' or ''))
        '''
        h += list_get_rec_html(wr, 'play', odd)
        total += wr.total
    h += DIV(T('Total played bets'), ': ', round(float(total),4), _class='row')
    return h, odd

### RUN + CLOSED
def list_get_closed(h, odd=None, pars={}, lang='en'):
    sel_man_id = pars.get('man')
    quick = tags = session.wlist_flt
    quick = quick == 1
    # поиск через contains(tags,  all=True, case_sensitive=False) - всех меток в одном споре
    tags = type(tags) == type('') and tags.split(',')
    for wr in db((db.wagers.status != 'PAY')
                 & (db.wagers.status != 'NEW')
                 & (not sel_man_id or db.wagers.man_id == sel_man_id)
                 & (not quick or db.wagers.w_cat_id==1)
                 & (not tags or db.wagers.tags.contains(tags,  all=True, case_sensitive=False))
                 ).select(orderby=~db.wagers.id):
        odd = not odd

        ''''
        w_cat = locz.get(db.w_cats, db.w_cats[wr.w_cat_id], lang)
        wr_loc = locz.get(db.wagers, wr, lang)

        cash = db.cash[ wr.cash_id]
        cash_i = SPAN(IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''), ' ',
                      SPAN(cash.name, _class='small'))
        ## w_cat.name,': ',
        h += DIV(DIV(A(XML('<i class="fa fa-%s"></i> ' % (wr.status=='RUN' and 'forward' or 'eject')),
                           wr_loc.name, _href=URL('hand','make',args=[wr.id])), _class='col-sm-5'),
                 DIV(A(wr.man_name, _href=URL('man','index',args=[wr.man_id])), _class='col-sm-2'),
                 #DIV(wr.status, _class ='col-sm-1'),
                 DIV(cash_i, _class ='col-sm-3'),
                 #DIV(cash_i, _class ='col-sm-3'),
                 DIV(wr.total, _class ='col-sm-2'),
                 _class='row' + (odd and ' odd' or ''))
        '''
        h += list_get_rec_html(wr, wr.status=='RUN' and 'forward' or 'eject', odd)
    return h, odd

# тут переменна чтобы это как подпрограмма воспринималось
def show_id_btn(www):
    h = SPAN(
            INPUT(_id='show_by_id', _name='show_id', _class='numb'),
            BUTTON(TAG.i(_class="fa fa-eye bbig"),
                   _class='btn btn-' + CLRS.btn ,
                   _onclick='''
                        var u = $('#show_by_id').val();
                        if (u.length>0) location.href= '%s/' + u;
                    ''' % URL('hand','make')),
            _class='pull-right')
    return h

def filter_tags():
    session.wlist_flt = request.vars.tags
    response.js = "jQuery('#list_load').get(0).reload();"
    return
def filter_clear():
    session.wlist_flt=None
    response.js = "jQuery('#list_load').get(0).reload();"
    return
def filter_quicks():
    session.wlist_flt=1
    response.js = "jQuery('#list_load').get(0).reload();"
    return
def filter(sess, req):
    h = CAT()

    hide_list_load = '$("#list_load").slideUp(300);'
    h += A(XML('<i class="fa fa-search-minus"></i>'), _class='tag',
           _onclick=hide_list_load + "ajax('%s')" % URL('hand','filter_clear'), _style='background-color:#da4f49;')

    qvars = req.vars.copy()
    qvars.update({'quick':1})
    #h += A(XML('<i class="fa fa-flash"></i>'), _class='tag', _href=URL(args=req.args, vars=qvars), _style='background-color:#da4f49;')
    h += A(XML('<i class="fa fa-flash"></i>'), _class='tag',
           _onclick=hide_list_load + "ajax('%s')" % URL('hand','filter_quicks'), _style='background-color:#da4f49;')
    h += A(XML('<i class="fa fa-search"></i>'), _class='tag',
           _onclick=hide_list_load + "ajax('%s', ['tags']);" % URL('hand','filter_tags'), _style='background-color:#da4f49;' )
    wlist_flt = session.wlist_flt
    wlist_flt = type(wlist_flt) == type('') and wlist_flt or ''
    h += INPUT(_name='tags', _value=wlist_flt, _id='tags')
    h += SPAN(XML('<i class="fa fa-eraser"></i>'), _class='tag', _onclick='$("#tags").val("");')
    h += CAT(SCRIPT('function at(n) { $("#tags").val($("#tags").val() + n + ",");}'))
    tags = db(db.tags).select(orderby=~db.tags.uses, limitby=(0,20)).sort(lambda row: row.name.lower())
    for tag in tags:
        #uses = tag.uses**0.4
        uses = tag.uses
        size = uses> 300 and 24 or uses> 100 and 20 or uses> 10 and 16 or 14

        h += DIV(tag.name, _class='tag', _onclick='at("%s");' % tag.name,
                  _style='font-size:%spx;' % size)
    return DIV(h, _class='row')

def list_load():
    #print request.vars
    fltr = session.wlist_flt
    if fltr==1:
        fltr = T('Only quick wagers')
    elif type(fltr)==type(''):
        fltr = T('By tags') + ': ' + fltr

    h = CAT(fltr and DIV(fltr, _class='row') or '')
    #lang = session.lang or request.env.http_accept_language
    h, odd = list_get_new(h, False, request.vars, lang_curr)
    h, odd = list_get_pay(h, odd, request.vars, lang_curr)
    h, odd = list_get_closed(h, odd, request.vars, lang_curr)
    h += SCRIPT('$("#list_load").slideDown(600);')

    return h

def list():

    response.title = None # T('List of Wagers')

    h = CAT()

    hh = T('List of Wagers') #T('Wagers')
    sel_man_id = request.vars.man
    if sel_man_id:
        if sel_man_id.isdigit():
            sel_man = db.men( sel_man_id )
            if sel_man:
                hh = CAT(T('List of wagers for'), ' ', B(sel_man.name))
    h += DIV(hh, show_id_btn(1), _class='row')

    h += filter(session, request)

    '''
    #lang = session.lang or request.env.http_accept_language
    h, odd = list_get_new(h, False, request.vars, lang_curr)
    h, odd = list_get_pay(h, odd, request.vars, lang_curr)
    h, odd = list_get_closed(h, odd, request.vars, lang_curr)
    '''
    h += LOAD('hand', 'list_load', vars=request.vars, ajax=True, target='list_load', _style='display:none; height:0%;')

    return dict( h = DIV(h, _class='row inv'))

# вызов по Аяксу
def w_cat_sel():
    w_cat_name = request.vars.w_cat_name
    #lang = session.lang or request.env.http_accept_language or 'en'

    if not w_cat_name or len(w_cat_name) <1: return ''

    # начала добавим все "Другие"
    other = db.w_cats[1]
    sels = [[other.id, other.name]]
    if lang_curr == 'en':
        for r in db((db.w_cats.name.contains(w_cat_name, case_sensitive=False))
                & (db.w_cats.id != 1)).select():
            sels.append([r.id, r.name])
    else:
        for r in db(db.w_cat_loczs.ref_id == 1).select():
            sels.append([-r.id, r.name])
        for r in db(db.w_cat_loczs.name.contains(w_cat_name, case_sensitive=False)).select():
            sels.append([-r.id, r.name])

    return SPAN(*[SPAN(k[1],
                     _onclick="$('#w_cat_id').val('%s');$('#w_cat_name').val('%s');" % (k[0], k[1]),
                     #_onmouseover="this.style.backgroundColor='yellow'",
                     #_onmouseout="this.style.backgroundColor='white'"
                     _class = 'btn_a',
                     ) for k in sels], _class='btn_mc')

def w_cat_sel_all():
    other = db.w_cats[2]
    sels = [[other.id, other.name]]
    for r in db((db.w_cats.id != 1)
                & (db.w_cats.id != 2)).select():
        sels.append([r.id, r.name])
    for r in db((db.w_cat_loczs.ref_id != 1)
                & (db.w_cat_loczs.ref_id != 2)).select():
        sels.append([-r.id, r.name])

    return SPAN(*[SPAN(k[1],
                     _onclick="$('#w_cat_id').val('%s');$('#w_cat_name').val('%s');" % (k[0], k[1]),
                     #_onmouseover="this.style.backgroundColor='yellow'",
                     #_onmouseout="this.style.backgroundColor='white'"
                     _class = 'btn_a',
                     ) for k in sels], _class='btn_mc')

def form_full_make(resp, sess, cash_i):
    import datetime

    resp.title = CAT(T('Make a hand Wager'), ' ',
         TAG.i( _class='btn-awes fa fa-question-circle', _onclick="$('#help1').toggle('slow');")
         )
    resp.helptitle = SPAN(T('Yor may manage this wagers and earn on it!'), _id='help1', _style='display: none')
    h_tags = CAT(SCRIPT('function at(n) { $("#no_table_tags").val($("#no_table_tags").val() + n + ",");}'))
    h_tags += SPAN(XML('<i class="fa fa-eraser"></i>'), _class='tag', _onclick='$("#no_table_tags").val("");')
    tags = db(db.tags).select(orderby=~db.tags.uses, limitby=(0,30)).sort(lambda row: row.name.lower())
    for tag in tags:
        uses = tag.uses
        size = uses> 300 and 24 or uses> 100 and 20 or uses> 10 and 18 or 16
        h_tags += SPAN(tag.name, _class='tag', _onclick='at("%s");' % tag.name,
                        _style='font-size:%spx;' % size
                        )
        #h_tags += ', '
    if 1:
        run_dt = datetime.datetime.now() + datetime.timedelta(15)

        f = SQLFORM.factory(
            Field('wager_name', 'string',
                  # default = sess.wager_name or '',
                  label=T('Name')),
            Field('run_dt', 'datetime-',
                  default = run_dt,
                  label=XML(T('Auto RUN on Time') + '<br>' + T('Will set run status on this time')),
                  ),
            #LABEL(T('Auto run on setted Datetime') ),
            Field('descr', 'text', label=T('Description'),
                             widget=ckeditor.widget),
            Field('def_bet', 'float', default =  sess.def_bet or 0.33,
                  #comment=cash_i
                  ),
            Field('tags', 'string', default = sess.tags or '', label=T('Tags')),
            labels = {'def_bet': CAT(T('Default Bet in'),BR(), cash_i)}
            )
    else:
        ckeditor.load()
        f = FORM(
            DIV(DIV(
                LABEL(T('Select a Category')),
                INPUT(_name='w_cat_id', _id = 'w_cat_id', _value = sess.w_cat_id, _type='hidden'),
                DIV( w_cat_sel_all(), #_id="w_cat_list",
                    _class="row"),
                INPUT(_name='w_cat_name', _id='w_cat_name', _value = sess.w_cat, _placeholder=T('Or input new'),
                            #_onkeyup="ajax('%s', ['w_cat_name'], 'w_cat_list');" % URL('hand', 'w_cat_sel_all')
                            ),
                _class='row'),
                BR(),
                DIV(LABEL(T('Set WAGER Name')),
                    TEXTAREA(_rows=3, _name='wager_name',  _value = sess.wager_name, _placeholder=T('Type Name of Wager'), _style='width:350px;'),
                    TEXTAREA(_rows=5, _name='descr', _placeholder=T('Type Decsription of Wager'),
                             _class='text plugin_ckeditor',
                             _style='width:350px;'),
                    LABEL(T('Default Bet:')),
                    INPUT(_name='def_bet',  _value = sess.def_bet or 0.33, _class='numb'),
                    BUTTON(XML(T('MAKE for %s') % cash_i), _class='btn-' + CLRS.btn) ,
                    _class='col-sm-5'),
                _class='row')
                )
    #f[0].insert(-3,cash_i)
    if not is_mobile:
        # table.tr.td.elem
        f[0][0][1][0]['_style'] = 'width: 750px;'
        f[0][3][1][0]['_style'] = 'width: 650px;'
    f[0].insert(4, TR(TD(), TD(h_tags)))

    return f

def form_quick_make(resp, sess, cash_i):
    resp.title = CAT(T('Quick make a Wager'), ' ',
         TAG.i( _class='btn-awes fa fa-question-circle', _onclick="$('#help1').toggle('slow');")
         )
    resp.helptitle = SPAN(T('Quick make a wager by select of names type and number of commands'), _id='help1', _style='display: none')
    return FORM(
        DIV(
            DIV(
                T('Selected cash:'), ' ', cash_i,BR(),
                LABEL(T('Set number of commands or conditions')),
                INPUT(_name='numbs', _value = sess.teams_numbs or 2, _class='numb'),
                LABEL(T('And select a names type:')),

                #### _name='quick_btn' -  чтобы не путаться с параметром для быстрого создания ?quick=1
                BUTTON(T(' Team '), _class='btn-' + CLRS.btn, _name='quick_btn', _value='team'),' ',
                BUTTON(T(' Color '), _class='btn-' + CLRS.btn, _name='quick_btn', _value='color'),' ',
                BUTTON(T(' Good '), _class='btn-' + CLRS.btn, _name='quick_btn', _value='good'),
                _class='col-sm-6'),
            _class='row'),
        )

# добавим высказывание в чат
def show_chat_add_rec():
    man_id = session.man_id
    wager_id = request.args(0)
    name = request.vars.get('name')
    mess = request.vars.get('mess')
    if wager_id and (name or mess):
        db.wager_chat.insert( wager_id = wager_id, name = name,
                             man_id = man_id,
                             mess = mess )
        # обновим чат
        response.js = "jQuery('#show_chat').get(0).reload();"

def show_chat_add(wager_id):
    man_name = session.man_name
    h = CAT()

    btn_add = A(T('To Say as %s') % (man_name or '???'),
            _class="btn btn-danger", _id='show_chat_add_btn',
            _onclick='ajax("%s", ["name", "mess"]);$(this).parent().addClass("hidden");'
                % URL('hand', 'show_chat_add_rec', args=[wager_id]) )
    f = FORM(
        DIV(
             INPUT(_name='name', _class='form-control', _placeholder=T('Name of message')),
             ' ', btn_add,
             TEXTAREA(_name='mess', _class='form-control',
                      _style='height:100px;',
                      _placeholder=T('Input Text message')),
            _class='form-group'),
         '',
         )
    h += DIV(f,
         _style='padding-top:15px;',
        _class='row')
    return h

def show_chat():
    wager_id = request.args(0)
    if not wager_id: return ''

    wager = wager_id and db.wagers[ wager_id ]

    h = CAT(
        )

    if not wager:
        h +=  wager_id and T('Wager [%s] not found') % wager_id or ''
        return h

    chats = db(db.wager_chat.wager_id == wager_id).select(orderby=~db.wager_chat.created_on)
    for r in chats:
        user = r.man_id and db.men[ r.man_id ]
        user = user and user.name or '***'
        h += DIV(
            DIV(
                DIV(r.created_on, _class='col-sm-4'),
                DIV(user, _class='col-sm-4'),
                #DIV(BUTTON(T('answer')), _class='col-sm-4 poll-right'),
                _class='row'),
            DIV(DIV(r.name, _class='col-sm-6'),
                _class='row'),
            DIV(
                DIV(r.mess, _class='col-sm-12'),
                _class='row'),
            _style='padding-bottom:20px;',
            _class='row')
    return h

def make():
    response.title = None
    wager_id = request.args(0)
    if wager_id:
        if not wager_id.isdigit():
            #return response.stream('x' * 3333)
            return response.stream(Jammer(),40000)
    else:
        cond_id = request.vars.cond
        if cond_id and cond_id.isdigit():
            if cond_id.startswith('up_'):
                redirect(URL('man','meet'))
            if not cond_id.isdigit():
                #return response.stream('x' * 3333)
                return response.stream(Jammer(),40000)
            cond = db.wager_conds[ cond_id ]
            wager_id = cond and cond.wager_id

    session.wager_id = wager_id
    wager = wager_id and db.wagers[ wager_id ]

    if wager and (wager.status == 'PAY' or wager.status == 'RUN'):
        # загрузим стили для кнопок здесь - в LOAD не пашет это
        response.files.append(URL('static','css/chechbox.css'))

    h = CAT()

    if session.man_id:
        # можно менять валюту
        response.menu.append(cash_sel()) # in menu model

        cash_id = session.cash_id
        cash = db.cash[ cash_id ]
        cash_i = CAT(cash.system_name, ' ', IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''))

        if wager:
            # зазадим титл страницы для социальных сетей
            wr_loc = locz.get(db.wagers, wager, lang_curr)
            ###<!-- all META included in web2py_ajax.html -->
            title, descr = get_title_descr(wr_loc)
            response.meta_title = response.meta.title = title
            response.meta.description = descr
            itemprop_name = title
            # <script type="application/ld+json">
            response.ld_json = '''
                {
                "@context": "http://schema.org/Event",
                "@type": "Article",
                "name": "%s",
                "description"; "%s"
                }
                ''' % (title, descr or '')
        else:
            quick = request.vars.quick
            if quick:
                form = form_quick_make(response, session, cash_i)
                import datetime
                request.vars.run_dt =  datetime.datetime.now() + datetime.timedelta(1)
            else:
                form = form_full_make(response, session, cash_i)

            quick_btn = request.vars.quick_btn
            if form.accepts(request, session, keepvalues=True, formname='make_wager'):
                print 'form.vars', form.vars
                session.wager_name = '%s' % form.vars.wager_name
                print 'session.wager_name', session.wager_name
                #return
                session.def_bet = form.vars.def_bet
                session.w_cat_id = form.vars.w_cat_id
                session.w_cat = form.vars.w_cat
                # сначала созддадим у нас
                cash = db.cash[ session.cash_id ]
                if cash.used:
                    wager_id = insert_wager(request, session, quick_btn)
                    if wager_id:
                        # теперь внесем в ЛАЙТ
                        wager = db.wagers[ wager_id ]
                        mess = make_lt_wager(wager, cash, db.men[ session.man_id ])
                        if mess:
                            # ошибка - покажем
                            response.flash = mess
                        else:
                            redirect(URL('hand','make', args=[wager_id]))
                    else:
                         response.flash = T('Number wrong')
                else:
                     response.flash = T('That currency %s not used now. Select Bitcoin please') % cash.name

            h += form
            h += DIV(_id = 'make_wager')
    elif not wager:
        h += DIV(XML(T('You can not make a wagers, %s or %s first!')
                 % (A(T('to Meet'), _href=URL('man','meet')), A(T('to Greet'), _href=URL('man','greet')))), _class='row')

    if wager: times = 'infinity' # если огранисить то перезагрузка будет ограничена данное число раз по reload
    else: times = wager_id and 2 or 1 # если = 1 - то нначальной загрузки нету а только через 20сек загрузит


    h += LOAD('hand', 'show_wager',
            args= wager_id and [wager_id], # иначе передеает строковое значение "None'
            ajax=True, times = times, timeout=9999999, #settings.UPD_TIMEOUT,
            target='show_wager', # вместо _id
            _style='display:none; height:0%;',
            _class='', #  ### !!!! обязательно нужен - иначе анимация сбивается!
            )
    #h += BR()
    h += LOAD('hand', 'show_conds', args=wager_id and [wager_id],
            ajax=True, times = times, timeout=9999999, #settings.UPD_TIMEOUT,
            target='show_conds', # вместо _id
            _style='display:none; height:0%; margin-top:20px;',
            _class='', #  ### !!!! обязательно нужен - иначе анимация сбивается!
            )
    if wager and wager.status != 'NEW':
        h += show_chat_add(wager_id)
        h += LOAD('hand', 'show_chat', args=wager_id and [wager_id],
            ajax=True, times = 'infinity', timeout=111111, #settings.UPD_TIMEOUT,
            target='show_chat', # вместо _id
            #_style='display:none; height:0%; margin-top:20px;',
            _class='', #  ### !!!! обязательно нужен - иначе анимация сбивается!
            )

    return dict( h = DIV(h,
                 _itemscope='', _itemtype='http://schema.org/Evant',
                 _class='row'))


def u(h, url, cls='col-sm-4'):
    return DIV(DIV(P(h, _class='btn_mc2'), _class='btn_mc1', _onclick="location.href='%s'" % url), _class='btn_mc ' + cls)

def index():
    response.title = ''
    h = CAT()
    h += DIV(
        u(T('Make new WAGER'),URL('hand', 'make')),
        u(T('Quick Make Simple WAGER'),URL('hand', 'make', vars={'quick':1})),
        u(T('See WAGERs List'), URL('hand', 'list')),
        _class='row')

    h += BR()
    h += H3(T('You may to bet on Wagers now'),':', show_id_btn(1), _class='inv_lgrn')
    # сбросим фильтр поиска
    session.wlist_flt=None
    h, _ = list_get_pay(h, None, {}, lang_curr)

    h += H3(T('Last messages'))
    for r in db(db.wager_chat).select(orderby=~db.wager_chat.created_on, limitby=(0,20)):
        wager = db.wagers[ r.wager_id ]
        wr_loc = locz.get(db.wagers, wager, lang_curr)
        user = r.man_id and db.men[ r.man_id ]
        if r.name or r.mess:
            wr_name = wr_loc.name
            # тут по 2 байта на UTF
            #if len(wr_name)>60: wr_name = wr_name[:55] + '...'
            title = r.name or ''
            #if len(title)>20: title = title[:17] + '...'
            h += DIV(
                DIV(DIV(SPAN(r.created_on, _style='font-size:medium;'), ' ',
                        user and A(B(user.name), _href=URL('man', 'index', args=[user.id])) or T('anonim'),
                        ': ', B(title), ' ', r.mess or '', _class='col-sm-12'),
                    _class='row unv'),
                DIV(
                    DIV(A(TAG.i(_class='fa fa-eye', _style='font-size:x-large'), _href=URL('hand', 'make', args=[wager.id]),
                        _class='btn1'), ' ',
                        SPAN(wr_name, _class='una'), _class='col-sm-12'),
                    _class='row'),
                _style='padding-bottom:10px;',
                _class='row')

    return dict(h = DIV(h, _class='inv'))

def error():
    return dict()
