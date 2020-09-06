##

## TODO - change shopID
## 113 - shop ID in LITE.cash
shopID = 113
DB_LINK = "mysql://root:SECRET_WORD@localhost/bets"

from gluon.storage import Storage

LANGS = Storage({
    'en': ['English', 'gb.png'],
    'ru': ['Русский', 'ru.png'],
    #'de': ['Deutsche ', 'de.png'],
    #'tr': ['Türkçe', 'tr.png'],

})

# если в вызове смена языка назначенна
# то его запомним в сесси и вызов обратный без параметра по РЕДИРЕКТУ
lang = request.vars.lang
if lang:
    request.vars.pop('lang')
    if lang != session.lang and lang in LANGS:
        session.lang = lang
        #print '0.py - lang -> %s' % session.lang
        redirect(URL( args = request.args, vars = request.vars))

# перед тем как ключи в теги вставлять - сразу язык поменяем
if session.lang and T.accepted_language != session.lang:
    #print '0.py - forsed T.[%s]' % session.lang
    T.force(session.lang)

if False:
    response.alert=T.accepted_language == 'ru' and 'ВНИМАНИЕ!!! На сервисе идёт пересинхронизация кошелька Биткоин, операции с этой валютой приостановлены. Приносим извинения за задержку. Пожалуйста создавайте споры в другой криптовалюте (например лайткоин)'\
    or 'ATTENTION!!! The service is reloaded of Bitcoin wallet, operations with this currency suspended. We apologize for the delay. Please create wagers in another cryptocurrency (litecoin for example)'

    


UP_LVL = [5,3] # % UP_LVL[0]*UP_LVL[1]**(int(rec.trust)-1)

CLRS = Storage(
#btn = 'primary',
btn = 'danger', #'warning',
btn2 = 'warning',
)


settings = Storage(
## TODO set link to local DB
db_link = DB_LINK,
reload_bg_imgs = False, # reload back ground images
UPD_TIMEOUT =200000,

develop = True,
migrate = True,
serv_fee = 1.0, ## in %
title = T('Заработать и получить Биткоин бесплатно можно здесь. Пари за биткоины, Get Free Bitcoin.'),
meta_title = T('free, free bitcoin bets, free bitcoin wagers, free bitcoin totalizator'),
#subtitle = 'Games bets',
meta = Storage(
    keywords = T('bitcoin bets') + ', ' + T('bitcoin wagers') + ', ' + T('bitcoin totalizator') + ', '
        + T('make bets on any event') + ', ' + T('make own wagers on any event'),
    description = T('You may made self free bitcoin bets for esport, free bitcoin wager for politics, bitcoin bets for sport, free bitcoin totalizators.'),
    author = 'icreator',
    ),
author_email = 'icreator@mail.ru',
layout_theme = 'Default',
database_uri = 'sqlite://storage.sqlite',
security_key = 'b----8',
#####
email_server = 'smtp.sendgrid.net',
email_sender = 'support@cryptopay.in',
email_login =  '-SECRET_WORD-',
login_method = 'local',
login_config = '',
plugins = [],

)

LITEcash = Storage(
    url = 'http://LITE.cash/',
    make_wager = 'wager/make.json/' + '%s' % shopID +'/%s?', ## %(fee)s&%(m_fee)s&%(m_addr)s&%(run_dt)s',
    go_wager = 'wager/go.json/%s/%s',
    end_wager = 'wager/end.json/%s/%s/%s',
    make = 'wager/make_bet_bill.json/%s/%s?order=%s&vol=%s&mess=%s',
    make_bill = 'api_bill/make.json/' + '%s' % shopID + '?order=%s&price=%s&curr=USD&not_convert&mess=%s',
    show = 'bill/show/%s',
    check = 'api_bill/check.json/%s',
    info = 'api_bill/info/%s?get_payouts=1',
    )
if False and settings.develop:
    LITEcash.url='http://127.0.0.1:8000/bs3b/'
    LITEcash.make_wager = 'wager/make.json/1/%s?'
    LITEcash.make_bill = 'api_bill/make.json/1?order=%s&price=%s&curr=USD&not_convert&mess=%s'

is_mobile=request.user_agent().is_mobile
if not is_mobile:
    #response.logo = A(IMG(_src=URL('static','images/logo_bets.jpg')), _href=URL('default', 'index'), _class='pull-left', _id='logo')
    response.logo = A(IMG(_src=URL('static','images/logo_bets2m.png'), _width=270),
                  _href=URL('default', 'index'), _class='pull-left', _id='logo')
else:
    response.logo = A(IMG(_src=URL('static','images/logo_bets2mm.png'), _width1=70),
                  _href=URL('default', 'index'), _class='pull-left', _id='logo')
