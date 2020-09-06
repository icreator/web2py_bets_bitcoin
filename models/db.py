# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
    
    
if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    #db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    if settings.develop:
        # мой комп для разработки
        db = DAL("sqlite://storage.sqlite", # on PC locals
            #folder='applications/shop/databases',
            pool_size=0,
            migrate=True,
            #fake_migrate=True,
            check_reserved=['all'],
            )
    else:
        migrate = False
        #migrate = True
        db = DAL(settings.db_link, # on AZURE
            #folder='applications/shop/databases',
            pool_size=2,
            auto_import=False,
            #migrate_enabled = migrate,
            #fake_migrate = True, # если таблицы уже созданы то включим это
            migrate=migrate,
            #fake_migrate=False,
            check_reserved=['all'],
            )

else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

session.connect(request, response, db=db)

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else ['html']

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Service, PluginManager

mail = None
if False:
    from gluon.tools import Auth
    auth = Auth(db)
    # create all tables needed by auth if not custom tables
    auth.define_tables(username=False, signature=False)

    ## configure email
    mail = auth.settings.mailer
    mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
    mail.settings.sender = 'you@gmail.com'
    mail.settings.login = 'username:password'

    ## configure auth policy
    auth.settings.registration_requires_verification = False
    auth.settings.registration_requires_approval = False
    auth.settings.reset_password_requires_verification = True

    ## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
    ## register with janrain.com, write your domain:api_key in private/janrain.key
    from gluon.contrib.login_methods.janrain_account import use_janrain
    use_janrain(auth, filename='private/janrain.key')

service = Service()
plugins = PluginManager()

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

##########################################
UNIQ = True
from decimal import Decimal
import random
import string

from plugin_ckeditor import CKEditor
ckeditor = CKEditor(db)
ckeditor.define_tables()

db.define_table('tags', # идентификаторр игры - на каком сервере, ИД + состояние
    Field('name', 'string', length=30, comment=''), # тут описание категирии и меток
    #Field('name2', 'calc', ), # тут описание категирии и меток
    Field('uses', 'integer', default=1),
    )

db.define_table('cash',
    Field('used','boolean', default=True), # ON - OFF
    Field('img_name','string', length=20, comment='for image static/images/cash'),
    Field('system_name','string', length=20, comment='PayPal, Yandex, ...'),
    Field('cash_name','string', length=20, comment='USD, BTC'),
    Field('name','string', length=30, unique=UNIQ, compute=lambda r: r['system_name']+':'+r['cash_name']),
    Field('def_bet', 'decimal(8,3)', default = Decimal('0.1'), comment='default bet'),
    Field('url','string', length=30),
    format = '%(name)s',
    )

db.define_table('men',
    Field('email','string', length=60, unique=UNIQ,
          requires=[IS_EMAIL(), IS_NOT_IN_DB(db, 'men.email')],
          #requires=IS_EMPTY_OR(IS_EMAIL(),
          ),
    Field('name','string', length=30, unique=UNIQ, comment='Nickname'),
    Field('ref_key','string', length=10, unique=UNIQ, readable=True, writable=False, comment='referal key'),
#    Field('session_key','string', length=40, writable=False, readable=False,
#          default = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(40)),
#          ),
    Field('trust','integer', default = 0, readable=True, writable=False, comment='level of Trust to You'),
    Field('activity','integer', default = 0, readable=True, writable=False, comment = 'level of Your Activity'),
    Field('harm','integer', default = 0, readable=True, writable=False, comment = 'level of Your Harm'),
    Field('fee', 'decimal(3,2)', default = Decimal('2'), comment='% fee for maker'),
    #  после создания счета на оплату сюда закатываем и сравниваем с этим номером тоже
    # без референсе -  тобы каскадного удаления не было
    Field('up_order','integer', readable=False, writable=False, comment='order id in db.orders for up trust level'),
    format = '%(email)s',
    )
# ключи доступа сюда запминаем - только надо их удалять периодически
db.define_table('man_keys',
    Field('man_id', db.men),
    Field('created_on', 'datetime', default=request.now ),
    Field('temp_key','string', length=100, unique = UNIQ),
    )
db.define_table('man_accs',
    Field('man_id', db.men, readable=False, writable=False),
    Field('cash_id',db.cash),
    Field('acc','string', length=60, requires=IS_NOT_EMPTY(), comment=T('wallet address')),
    Field('bal', 'decimal(16,8)', readable=False, writable=False, default = Decimal(0), comment='balance for this money'),
    Field('dep_bill', 'string', length=40, readable=False, writable=False, comment='bill_id in that money system for deposit'),
    format = '%(email)s',
    )
db.define_table('man_acc_txs',
    Field('man_acc_id', db.man_accs),
    Field('txid','string', length=60, requires=IS_NOT_EMPTY(), comment=T('transaction id')),
    Field('amo', 'decimal(16,8)', requires=IS_NOT_EMPTY(), comment=T('transaction amount')),
    )

# тут сделаем уникальный сложную проверку
db.man_accs.cash_id.requires=IS_IN_DB(db, 'cash.id', '%(name)s',
      _and = IS_NOT_IN_DB(db(db.man_accs.man_id==request.vars.man_id),'man_accs.cash_id'))
##db.exchg_taxs.curr2_id.requires=IS_IN_DB(db, 'currs.id', '%(name)s',
##    _and = IS_NOT_IN_DB(db(db.exchg_taxs.curr1_id==request.vars.curr1_id),'exchg_taxs.curr2_id'))


db.define_table('games',
    Field('cod','string', unique=True, length=20),
    Field('name','string', length=60),
    format = '%(name)s',
    )
db.define_table('b_servs', # идентификаторр сервера
    Field('game_id',db.games),
    Field('host_p','string', length=30, comment='123.32.123.2:3456'),
    Field('s_port','integer', comment='Software PORT'),
    Field('zone_id','integer', comment='zone id'),
    Field('status','boolean', default=False), # ON - OFF
    Field('total', 'decimal(16,8)', default = Decimal('0.0')),
    format = '%(id)s',
    )
db.define_table('w_cats', # каталог
    Field('name', 'string', length=100),
    format = '%(name)s',
    )
db.define_table('w_cat_loczs', # каталог
    Field('ref_id',db.w_cats),
    Field('lang', 'string', length=6, comment='en'),
    Field('name', 'string', length=100),
    )

db.define_table('wagers', # идентификаторр игры - на каком сервере, ИД + состояние
    Field('w_cat_id',db.w_cats, default=1),
    Field('tags', 'string', length=150, comment=''), # тут описание категирии и меток
    Field('cash_id',db.cash),
    Field('man_id', db.men),
    Field('name', 'string', length=150),
    Field('man_name', 'string', length=30),
    Field('run_dt', 'datetime', readable=False, writable=False, comment='Auto run om DatetIme' ),
    Field('descr', 'text', widget=ckeditor.widget),
    Field('b_serv_id', requires=IS_EMPTY_OR(IS_IN_DB(db, 'b_servs.id'))),
    Field('map_id', 'integer', comment='map or game id'),
    Field('lite_wager_id','integer', comment='LITE.cash/wager_id'),
    Field('lite_wager_key', 'string', length=10, comment='LITE.cash/wager_key'),
    Field('status','string', length=10,
          # 'NEW' - можно создавать условия спора, 'PAY' - можно делать ставки, 'RUN' - ожидаем, 'END' - выплачиваем
          requires=IS_IN_SET(['NEW', 'PAY', 'RUN', 'END'])),
    Field('def_bet', 'decimal(8,3)', default = Decimal('0.1'), comment='default bet'),
    Field('total', 'decimal(16,8)', default = Decimal('0.0')),
    format = '%(id)s %(name)s',
    )
# перевод имени и описания
db.define_table('wager_loczs', # идентификаторр игры - на каком сервере, ИД + состояние
    Field('ref_id', db.wagers),
    Field('lang', 'string', length=6, comment='en'),
    Field('name', 'string', length=150),
    Field('descr', 'text', widget=ckeditor.widget),
    )
db.define_table('wager_to_run', # у которых задано время запуска автоматом
    Field('ref_id', db.wagers),
    Field('run_dt', 'datetime'),
    )

db.define_table('wager_conds',
    Field('wager_id',db.wagers),
    Field('name','string', length=50, comment='название условия или величины (имя, номер команды или голы'),
    Field('descr','string', comment='описание'),
    Field('srav','string', length=3, requires=IS_EMPTY_OR(IS_IN_SET(['==', '>', '<']))),
    Field('val','integer', default=0),
    Field('res','boolean', default=False), # WIN?
    Field('bill_id','integer', comment='service bill_id'),
    Field('winned','boolean', default=False),
    Field('total', 'decimal(16,8)', default = Decimal('0.0')),
    format = '%(id)s',
    )

# перевод имени и описания
db.define_table('wager_cond_loczs', # идентификаторр игры - на каком сервере, ИД + состояние
    Field('ref_id',db.wager_conds),
    Field('lang', 'string', length=6, comment='en'),
    Field('name', 'string', length=50),
    Field('descr', 'string'),
    )

# обсуждения
db.define_table('wager_chat',
    Field('wager_id',db.wagers),
    Field('man_id', requires=IS_EMPTY_OR(IS_IN_DB(db,'men.id'))),
    Field('ref_id', 'integer'), # если есь ссылка - это ответ нна друге сообщение
    Field('name','string', length=100),
    Field('mess', 'text',
         #widget=ckeditor.widget
         ),
    Field('created_on', 'datetime', default=request.now ),
    )

db.define_table('orders', # счета для оплат чего угодно
    Field('cash_id',db.cash),
    Field('price', 'decimal(16,8)', default = Decimal('0.0')),
    Field('bill_id', 'string', length=40, comment='bill id in payment system'),
    Field('skey', 'string', length=40, comment='secret key'),
    Field('tab', 'string', length=20, comment='for table'),
    Field('ref_id', 'integer', comment='for rec id'),
    Field('status', 'string', length=20, comment='status'),
    Field('created_on', 'datetime', default=request.now ),
    )

db.define_table('subscr',
    Field('email','string', length=60, unique=UNIQ,
          requires=[IS_EMAIL(), IS_NOT_IN_DB(db, 'subscr.email')],
          ),
    Field('val','string', length=60),
    format = '%(email)s',
    )

# статистика сервиса
db.define_table('stats',
    Field('men','integer', default= 1),
    Field('wagers','integer', default= 0),
    Field('bets','integer', default= 0),
    )
if db(db.stats).isempty():
    db.stats.truncate()
    db.stats.insert()
db.define_table('stats_cash',
    Field('cash_id',db.cash),
    Field('wagers','integer', default= 0),
    Field('bets','integer', default = 0),
    Field('total','decimal(16,8)', default = Decimal('0.0')),
    )

# учет рекламы - откуда пришли на меня
db.define_table('adv',
    Field('site','string', length=60, unique=UNIQ ),
    Field('hit','integer', default= 0),
    format = '%(site)s',
    )

############################
############################
## TRUNCATE
if db(db.tags).isempty():
    db.tags.truncate()
if False and db(db.places).isempty():
    settings.develop and db.places.truncate()
if db(db.men).isempty():
    settings.develop and db.men.truncate()
if db(db.cash).isempty():
    settings.develop and db.cash.truncate()
if db(db.b_servs).isempty():
    settings.develop and db.b_servs.truncate()
if db(db.wagers).isempty():
    settings.develop and db.wagers.truncate()
if db(db.wager_conds).isempty():
    settings.develop and db.wager_conds.truncate()
if db(db.w_cats).isempty():
    settings.develop and db.w_cats.truncate()
if db(db.games).isempty():
    settings.develop and db.games.truncate()
#####################################################
## sets
if db(db.tags).isempty():
    for r in [
    'Europe', 'Asia', 'North America','South America','Australia', 'Germany',
         'England','China','Türkçe','Россия','e-sport','sport','Bitcoin','politics','finances','economics','shows'
    ]:
        db.tags.insert( name=r )

if False and db(db.places).isempty():
    db.places.insert( name='World', pic='wrld.png', cod='wrld')
    db.places.insert( name='Europe', pic='eur.png', cod='eu')
    db.places.insert( name='Asia', pic='eur.png', cod='eu')
    from os import listdir
    flags = listdir(request.folder + '/static/images/flags')
    for r in flags:
        db.places.insert( name=r[0], email=r[1], ref_key=r[0])

if db(db.men).isempty():
    for r in [
    ['icreator', 'icreator@mail.ru'],
    ]:
        db.men.insert( name=r[0], email=r[1], ref_key=r[0])

if db(db.cash).isempty():
    for r in [
            ['BTC', 'Bitcoin', 'btc.png', True],
            ['LTC', 'Litecoin', 'ltc.png', True],
            ['USD', 'PayPal', 'pp_usd.png', False],
            ]:
        db.cash.insert( cash_name = r[0], system_name = r[1], img_name = r[2], used=r[3])

if db(db.w_cats).isempty():
    db.w_cats.insert( name = 'quick') # с первым ИД сделаем
    db.w_cats.insert( name = 'other') # с 2 ИД сделаем
    for r in [ 'sport', 'eGames', 'finance', 'politics']:
        db.w_cats.insert( name = r)

if db(db.games).isempty():
    for k, v in {
    "aarmy"         : "Americas Army",
    "aarmy3"        : "Americas Army 3",
    "arcasimracing" : "Arca Sim Racing",
    "arma"          : "ArmA: Armed Assault",
    "arma2"         : "ArmA 2",
    "avp2"          : "Aliens VS. Predator 2",
    "avp2010"       : "Aliens VS. Predator ( 2010 By Rebellion )",
    "bfbc2"         : "Battlefield Bad Company 2",
    "bfvietnam"     : "Battlefield Vietnam",
    "bf1942"        : "Battlefield 1942",
    "bf2"           : "Battlefield 2",
    "bf2142"        : "Battlefield 2142",
    "callofduty"    : "Call Of Duty",
    "callofdutyuo"  : "Call Of Duty: United Offensive",
    "callofdutywaw" : "Call Of Duty: World at War",
    "callofduty2"   : "Call Of Duty 2",
    "callofduty4"   : "Call Of Duty 4",
    "cncrenegade"   : "Command and Conquer: Renegade",
    "crysis"        : "Crysis",
    "crysiswars"    : "Crysis Wars",
    "cs2d"          : "Counter-Strike 2D",
    "cube"          : "Cube Engine",
    "doomskulltag"  : "Doom - Skulltag",
    "doomzdaemon"   : "Doom - ZDaemon",
    "doom3"         : "Doom 3",
    "dh2005"        : "Deer Hunter 2005",
    "farcry"        : "Far Cry",
    "fear"          : "F.E.A.R.",
    "flashpoint"    : "Operation Flashpoint",
    "freelancer"    : "Freelancer",
    "frontlines"    : "Frontlines: Fuel Of War",
    "f1c9902"       : "F1 Challenge 99-02",
    "gamespy1"      : "Generic GameSpy 1",
    "gamespy2"      : "Generic GameSpy 2",
    "gamespy3"      : "Generic GameSpy 3",
    "ghostrecon"    : "Ghost Recon",
    "graw"          : "Ghost Recon: Advanced Warfighter",
    "graw2"         : "Ghost Recon: Advanced Warfighter 2",
    "gtr2"          : "GTR 2",
    "had2"          : "Hidden and Dangerous 2",
    "halflife"      : "Half-Life - Steam",
    "halflifewon"   : "Half-Life - WON",
    "halo"          : "Halo",
    "il2"           : "IL-2 Sturmovik",
    "jediknight2"   : "JediKnight 2: Jedi Outcast",
    "jediknightja"  : "JediKnight: Jedi Academy",
    "killingfloor"  : "Killing Floor",
    "kingpin"       : "Kingpin: Life of Crime",
    "mohaa"         : "Medal of Honor: Allied Assault",
    "mohaab"        : "Medal of Honor: Allied Assault Breakthrough",
    "mohaas"        : "Medal of Honor: Allied Assault Spearhead",
    "mohpa"         : "Medal of Honor: Pacific Assault",
    "mta"           : "Multi Theft Auto",
    "nascar2004"    : "Nascar Thunder 2004",
    "neverwinter"   : "NeverWinter Nights",
    "neverwinter2"  : "NeverWinter Nights 2",
    "nexuiz"        : "Nexuiz",
    "openttd"       : "Open Transport Tycoon Deluxe",
    "painkiller"    : "PainKiller",
    "plainsight"    : "Plain Sight",
    "prey"          : "Prey",
    "quakeworld"    : "Quake World",
    "quakewars"     : "Enemy Territory: Quake Wars",
    "quake2"        : "Quake 2",
    "quake3"        : "Quake 3",
    "quake4"        : "Quake 4",
    "ravenshield"   : "Raven Shield",
    "redorchestra"  : "Red Orchestra",
    "rfactor"       : "RFactor",
    "samp"          : "San Andreas Multiplayer",
    "savage"        : "Savage",
    "savage2"       : "Savage 2",
    "serioussam"    : "Serious Sam",
    "serioussam2"   : "Serious Sam 2",
    "shatteredh"    : "Shattered Horizon",
    "sof2"          : "Soldier of Fortune 2",
    "soldat"        : "Soldat",
    "source"        : "Source ( Half-Life 2 )",
    "stalker"       : "S.T.A.L.K.E.R.",
    "stalkercs"     : "S.T.A.L.K.E.R. Clear Sky",
    "startrekef"    : "StarTrek Elite-Force",
    "starwarsbf"    : "Star Wars: Battlefront",
    "starwarsbf2"   : "Star Wars: Battlefront 2",
    "starwarsrc"    : "Star Wars: Republic Commando",
    "swat4"         : "SWAT 4",
    "test"          : "Test ( For PHP Developers )",
    "teeworlds"     : "Teeworlds",
    "tribes"        : "Tribes ( Starsiege )",
    "tribes2"       : "Tribes 2",
    "tribesv"       : "Tribes Vengeance",
    "urbanterror"   : "UrbanTerror",
    "ut"            : "Unreal Tournament",
    "ut2003"        : "Unreal Tournament 2003",
    "ut2004"        : "Unreal Tournament 2004",
    "ut3"           : "Unreal Tournament 3",
    "vcmp"          : "Vice City Multiplayer",
    "vietcong"      : "Vietcong",
    "vietcong2"     : "Vietcong 2",
    "warsow"        : "Warsow",
    "warsowold"     : "Warsow ( 0.4.2 and older )",
    "wolfet"        : "Wolfenstein: Enemy Territory",
    "wolfrtcw"      : "Wolfenstein: Return To Castle Wolfenstein",
    "wolf2009"      : "Wolfenstein ( 2009 By Raven )",
    }.iteritems():
        db.games.insert( cod=k,name=v)

#############################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

if mail:
    mail.settings.server = settings.email_server
    mail.settings.sender = settings.email_sender
    mail.settings.login = settings.email_login
