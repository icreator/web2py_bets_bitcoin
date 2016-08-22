response.meta = settings.meta

def set_cash():
    new_cash_id = request.vars.get('sel_new_cash')
    if not new_cash_id: return
    
    if not new_cash_id.isdigit():
        import time
        time.sleep(22)
        return
    
    session.cash_id = new_cash_id
    new_cash = db.cash[new_cash_id]
    if not new_cash: return
    
    session.cash_name = new_cash.name

set_cash()

# менню выбора валют
def cash_sel():
    if session.cash_id:
        cash_id = session.cash_id
        curr_cash = db.cash[ cash_id ]
    else:
        # возьмем первый и запишем его в сесию
        curr_cash = db(db.cash.used==True).select().first()
        cash_id = curr_cash.id
        session.cash_id = cash_id
        session.cash_name = curr_cash.name
        
    cash_list = []
    for cash in db(db.cash.used==True).select():
        if cash.id == curr_cash.id: continue
        
        new_vars = {} #request.vars.copy()
        new_vars['sel_new_cash'] = cash.id
        cash_list.append(
            (SPAN(cash.system_name, ' ', IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt='')),
                 None, URL(args=request.args, vars=new_vars))
            )
    cash_list = (SPAN(curr_cash.system_name, ' ', IMG(_src=URL('static', 'images/cash/' + curr_cash.img_name), _width=30, _alt='')),
                None, None,
                cash_list)
    return cash_list

man_name = session.man_name

response.menu = [
#(XML('<i class="fa fa-home"></i>'), 0,URL('default','index'),[]),
(CAT(XML('<i class="fa fa-list-ul bbig"></i>'),T('Wagers')), 0,URL('hand','index'),[]),
(CAT(XML('<i class="fa fa-trophy bbig"></i>'),T('Makers')), 0,URL('man','index'),[]),
(XML('<i class="fa fa-question-circle bbig"></i>'), 0,URL('default','help'),[]),
(SPAN(XML(
    is_mobile and '<i class="fa fa-ellipsis-h" onclick="$(\'.mob_hide\').toggle();"></i>' or
    '<i class="fa fa-picture-o" onclick="$(\'#main_cont, #logo\').toggle();"></i>')),None,None),
]

lang_curr = session.lang or T.accepted_language
if not LANGS[lang_curr]: lang_curr = 'en'

def lang_sel():
    langs = []
    for (n,l) in LANGS.iteritems():
        if lang_curr == n: continue
        vars = request.vars.copy()
        vars['lang'] = n
        langs.append((
                CAT(IMG(_src=URL('static', 'images/flags/' + l[1]), _width=30, _alt=''),
                    ' ',l[0]), False, URL(args=request.args, vars=vars))
              )
    return langs


# если текущий язык не ннайден в нашем списке то покажем Англ как текущий
_lang = LANGS.get(lang_curr, LANGS.get('en', LANGS.get('ru'))) ## dict.keys()[0]
response.menu_man = [
    (CAT(IMG(_src=URL('static', 'images/flags/' + _lang[1]), _width=30, _alt=''), ' ', _lang[0]),
        False, None, lang_sel())
    ]

# request.controller=='man'
response.menu_man.append(
man_name and ( man_name, 0,URL('man','meet'),[
    ])
 or  (T('Enter'), request.controller=='man', None,[
    ( T('to Meet'), 0, URL('man','meet')),
    ( T('to Greet'), 0, URL('man','greet')),
    ])
)

partner = request.vars.partner
if partner:
    adv = db(db.adv.site==partner).select().first()
    if not adv:
        adv_id = db.adv.insert( site = partner )
        adv = db.adv[ adv_id ]
    adv.update_record ( hit = adv.hit + 1 )
        
    request.vars.pop('partner')
    redirect(URL( args = request.args, vars = request.vars))

def get_stats():
    h = CAT()
    for cash in db(db.cash.used==True).select():
        cash_id = cash.id
        sts = db(db.stats_cash.cash_id == cash_id).select().first()
        if not sts: continue
        h += SPAN(' ', round(float(sts.total),6),
            IMG(_src=URL('static', 'images/cash/' + cash.img_name), _width=30, _alt=''))
    return h
