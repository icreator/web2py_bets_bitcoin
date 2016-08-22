# -*- coding: utf-8 -*-
# try something like

def u(h, url, cls='col-sm-4'):
    return DIV(DIV(P(h, _class='btn_mc2'), _class='btn_mc1', _onclick="location.href='%s'" % url), _class='btn_mc ' + cls)

def set_session(sess, man):
    sess.man_id = man.id
    sess.man_name = man.name

# confirm - подтверждение по почте получено
def greet_conf():
    key = request.args(0)
    if not key: return dict(h = T('Empty key'))
    rec = db(db.man_keys.temp_key == key).select().first()
    if not rec: return dict(h = T('Key not found'))
    
    man = db.men[ rec.man_id ]
    del db.man_keys[ rec.id ]
    if not man: return dict(h = T('Man not found'))
    
    set_session(session, man)
    #return dict(h = CAT(T('Welcome'),', ', man.name))
    redirect(URL('default','index'))

def mail_greet(man, req):
    from gluon.tools import Mail
    import random
    import string
    key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(40))
    # запомним ключ посланный - только его принимаем
    db(db.man_keys.man_id == man.id ).delete()
    db.man_keys.insert( man_id = man.id, temp_key = key )
    
    
    url = URL('man', 'greet_conf', args=[key], scheme=True, host=True)
    #context = dict( key = key, man = man.name, url = url )
    #mess = response.render('man/email_greet.html', context)
    mess = CAT(
            H4(T('Hi'), ', ',man.name, '!'),
            BR(),
            T('You or someone request a re-greeting on %s') % req.env.http_host, BR(),
            #T('You or someone request a re-greeting on %s') % 'LITE.cash/bets', BR(),
            T('If that not you simple ignore that letter.'),B(),
            T('or'),BR(),
            T('For restore your greet on our site click'), ' ',
            A(H1(B(T('re-greeting url'))), _href=url),BR(),
            T('Or use this url manualy'), ': %s' % url,
        )
    #to_addrs = ['kentrt@yandex.ru','icreator@mail.ru']
    h = CAT(P(T('A letter sent to [%s]. Check your email and spam (junk) folder') % man.email))
    if req.is_local:
        h += DIV(mess)
    else:
        from gluon.tools import Mail
        mail = Mail()
        mail.settings.server = settings.email_server
        mail.settings.sender = settings.email_sender
        mail.settings.login = settings.email_login
        mail.send(
              to = man.email,
              subject = T('Restore access to BETS'),
              message = '<html>%s</html>' % mess )
    
    return h

def greet():
    res = ''
    if session.man_id:
        redirect(URL('man','meet'))
    
    form = FORM(LABEL(T('Input Your Email')),
             INPUT(_name='em', requires=IS_EMAIL()),
             INPUT(_type='submit', _class='btn btn-' + CLRS.btn))
    if form.accepts(request, session, keepvalues=True):
        man = db(db.men.email == form.vars.em).select().first()
        if man:
            response.flash = 'Email with access key send to Your. Check email and spam folder'
            res = mail_greet(man, request)
        else:
            form.errors.em = 'That email not metting'
            response.flash = T('That email not metting, please to Meet first')
    elif form.errors:
        response.flash = ''
    else:
        response.flash = 'please fill the form'
    
    h = DIV(T('For to restore Dating enter your email address and we will send you the key'), '. ',
            #T('If that email not known for as'), ' ',
            #A(T('to Meet'), _href=URL('man','meet')), ' ', T('first.'),
            form,
            res,
            _class='inv')
    
    return dict( h = h )

def forget():
    
    #return dict( h = (T('Sorry, email is busy')))
    session.man_id = session.man_name = session.man = None
    redirect(URL('man', 'meet'))
def form_accs_validate(f):
    if db((db.man_accs.man_id == f.vars.man_id)
          & (db.man_accs.cash_id == f.vars.cash_id)).select().first():
        f.errors.cash_id = T('Aready exist')
        response.flash = 'form has errors'

def make_mess(man):
    import urllib
    #return urllib.urlencode({'name':cond.name})
    return urllib.quote(man.name + ' ' + T('to up level to:') + ' ' + '%s' % (man.trust + 1))

def up_trust_pay():
    man_id = session.man_id
    if not man_id: return 'error man_id'
    man = db.men[ man_id ]
    if not man: return 'error man'
    up_order = man.up_order
    order = up_order and db.orders[ up_order ]
    if order:
        redirect(LITEcash.url + LITEcash.show % ('%s.%s' % (order.bill_id, order.skey)))

    # если счета нет то создадим
    from cm import calc_trust_pay
    to_pay = calc_trust_pay(UP_LVL, man.trust)
    
    url = LITEcash.url + LITEcash.make_bill % (
            'up_%s' % man.id,
            to_pay,
            make_mess(man)
            )
    print url
    from gluon.tools import fetch
    resp = fetch(url)
    print resp
    import gluon.contrib.simplejson as sj
    if not resp[:1].isdigit():
        # если тут не число - значит ошибка
        res = sj.loads(resp) # {'bill': bill_id }
        err = res.get('error')
        if err:
            return dict(err=err)

    bill_id, _, skey = resp.partition('.')
    order_id = db.orders.insert (price = to_pay,
                 tab = 'men', ref_id = man.id,
                 bill_id = bill_id, skey = skey,
                 )
    man.update_record(up_order = order_id)

    redirect(LITEcash.url + LITEcash.show % resp )

def deposit():
    return 'Only direct bitcoin bets used now'
def withdraw():
    return 'Only direct bitcoin bets used now'
def meet():
    man_id = session.man_id
    
    h = CAT()
    
    rec = man_id and db.men[ man_id ]
    form = SQLFORM(db.men, rec, readonly = rec, #, ignore_rw = rec,
        )
    #rec.trust = 5
    is_mobile = request.is_mobile
    if rec:
        from cm import calc_trust_pay
        to_pay = calc_trust_pay(UP_LVL, rec.trust)
        mm = ''
        for i in range(9):
            mm += '<div class="row %s">%s $ => %s level</div>' % (i == rec.trust and 'inv' or '', calc_trust_pay(UP_LVL, i), i+1)
        #tip = MENU([('%s $' % to_pay, False, None, mm)],
        #        _class='mobile-menu nav' if is_mobile else 'nav',mobile=is_mobile, li_class='dropdown', ul_class='dropdown-menu')
        tip = SPAN(to_pay, '$ ',TAG.i( _class='btn-awes fa fa-question-circle', _onclick="$('#up_lvls').toggle('slow');"), _class='inv')

        my_extra_element = TR(TD(
            T('For UP Trust Level You need to pay:'), ' ',
                tip,
                ' ', A(XML('<i class=" fa fa-shopping-cart" style="font-size:25px;"></i>'),
                      _title=T('Pay'),
                      _class='btn btn-' + CLRS.btn,
                      _style='width: 80px;margin-left:10px;',
                      _target = '_blank',
                      _href=URL('man', 'up_trust_pay')),
                DIV(XML(mm), _style='display:none', _id ='up_lvls'),
                _colspan=3,
                ),
            _id = 'up_trust',
            )
        form[0].insert(-3,my_extra_element)
    else:
        import random
        import string
        form.vars.ref_key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(10))
        if db(db.men.email == form.vars.email).select().first():
            form.errors.email=T('That email already exist!')

    #if form.accepts(request, session, keepvalues=True):
    if form.accepts(request, session, keepvalues=True):
        set_session(session, form.vars)
        ##response.flash = '%s welcome' % session.man_name
        redirect(URL('man', 'meet'))
    elif form.errors:
        response.flash = 'form has errors'
    
    if rec:
        
        form_accs = SQLFORM(db.man_accs, labels={'cash_id': T('Type of Cash'), 'acc':T('Account or address')})
        form_accs.vars.man_id = rec.id
        if form_accs.accepts(request, session, keepvalues=False, onvalidation=form_accs_validate):
            #redirect(URL('man', 'meet'))
            pass
        elif form_accs.errors:
            response.flash = 'form has errors'
        
        h += u(T('My Wagers'), URL('hand','list', vars={'man':rec.id})),

        
    
    h += form
    if rec:
        accs = db(db.man_accs.man_id == rec.id).select()
        if accs:
            hh = DIV(T('Accounts'),':')
            for r in accs:
                cash = db.cash[ r.cash_id]
                tag_id = 'mess%s' % r.id
                hh += DIV(
                    DIV(cash.name, ' ', r.acc, _class='col-sm-8'),
                    DIV(A(XML('<i class=" fa fa-plus" style="font-size:25px;"></i>'), _title=T('Deposit'), _class='btn btn-' + CLRS.btn, # bbig
                          _style='width: 60px;margin-right: 10px;',
                          _onclick="ajax('%s', ['name'], '%s')" % (URL('man', 'deposit'), tag_id)),' ',
                        A(XML('<i class=" fa fa-minus" style="font-size:25px;"></i>'), _title=T('Withdraw'), _class='btn btn-' + CLRS.btn,
                          _style='width: 60px;margin-right: 10px;',
                          _onclick="ajax('%s', ['name'], '%s')" % (URL('man', 'withdraw'), tag_id)),' ',
                            r.bal,
                        _class='col-sm-4', _id=tag_id),
                    _class='row', _style='margin-top: 7px;')
            h += DIV(hh, _class='game_stats')
        
        h += DIV(
                    DIV(_class='col-md-3'),
                    DIV(H3(T('Add payout account or wallet address')),form_accs, _class='col-sm-7'),
                _class='row')
    
        h += CAT(
             BR(), SPAN('To clear current session on this device, click: '),
             BUTTON(T('Good Bye'), _class='btn btn-' + CLRS.btn2,
                    _onClick = "parent.location='%s' " % URL('man','forget'))
            )
    
    return dict( h = DIV( h, _class='row') )

# class="fa fa-heart"
def fa_icons(fa_icon, val):
    h = CAT()
    for i in range(val):
        h += TAG.i(_class='fa ' + fa_icon)
    return h

def show_man(req, man):
    from cm import calc_trust_pay
    garant = 0
    # подсчитаем сколько оплачено гарантийного обеспечения
    for i in range(man.trust):
        garant += calc_trust_pay(UP_LVL, i)
    h = CAT()
    h += LABEL(T('Name'), ': ', man.name, _class='inv')
    h += LABEL(T('Trust'), ': ', B(man.trust, _class='inv'), ', ', T('guarantee deposit'), ': ', B(garant, _class='inv'),' $')
    h += LABEL(T('Activity'), ': ', B(man.activity, _class='inv'))
    h += LABEL(T('Distrust'), ': ', B(man.harm, _class='inv'))
    h += A(T('List of WAGERs'), _href=URL('hand','list',vars={'man':man.id}))
    
    return h

def index():
    man_id = request.args(0)
    man = man_id and db.men( man_id )
    if man: return dict(h = show_man(request, man))
    h = CAT()
    cl1 = 'col-sm-3'
    cl2 = 'col-sm-3'
    cl3 = 'col-sm-2'
    h += DIV(
        DIV(P(T('Name'), _class='header'), _class=cl1),
        DIV(P(T('Trust'), _class='header'), _class=cl2),
        DIV(P(T('Activity'), _class='header'), _class=cl2),
        DIV(P(T('Distrust'), _class='header'), _class=cl2),
         _class='row')
    odd = False
    for m in db(db.men).select(orderby = db.men.name):
        odd = not odd
        activity = m.activity
        actv = activity
        if actv > 3: actv = 3
        actv1 = int(activity * 0.1)
        if actv1 > 3: actv1 = 3
        actv += actv1
        actv1 = int(activity * 0.01)
        if actv1 > 3: actv1 = 3
        actv += actv1
        actv1 = int(activity * 0.001)
        if actv1 > 3: actv1 = 3
        actv += actv1
        h += DIV(
                DIV(A(m.name, _href=URL(args=[m.id])), _class=cl1),
                DIV(P(fa_icons('fa-heart', m.trust), _class='header'), _class=cl2 + ' green'),
                DIV(P(fa_icons('fa-trophy', actv), _class='header'), _class=cl2 + ' gold'),
                DIV(P(fa_icons('fa-thumbs-down', m.harm), _class='header'), _class=cl2 + ' black'),
                
             _class='inv row' + (odd and ' odd' or ''))
    
    return dict(h = h)
    #redirect(URL('man', 'meet'))
