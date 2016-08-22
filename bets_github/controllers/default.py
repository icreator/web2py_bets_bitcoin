# -*- coding: utf-8 -*-

'''
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
'''

response.title = ''
def u(h, url, cls='col-sm-4'):
    return DIV(DIV(P(h, _class='btn_mc2'), _class='btn_mc1', _onclick="location.href='%s'" % url), _class='btn_mc ' + cls)

def sel_loc_view(req, res):
    #print T.accepted_language, T.accepted_language in LANGS
    lang = T.accepted_language
    if lang in LANGS:
        view = req.controller +'\\' + req.function + '-' + lang + '.' + req.extension
        f = req.folder + 'views\\' + view
        import os
        #print f, os.path.exists(f)
        if os.path.exists(f):
            #print 'response.view=view', view
            res.view=view


def help():
    sel_loc_view(request, response)
    return dict()

def contacts():
    h = CAT()
    h += DIV(
        #SCRIPT(URL('static','js/share.js',vars=dict(static=URL('static','images')))),
        A(IMG(_src=URL('static','images/questions-o.png')),
            #_style="position:relative;bottom:0;left:0;z-index:1000",
            _href="https://groups.google.com/forum/#!forum/lite-cash", _target="_blank"),
        T('or'),BR(),BR(),
        T('administration'),': ', 'adm@lite.cash',BR(),
        T('support'), ': ', 'support@cryptopay.in',BR(),
        T('or'), ' ', A(T('discuss on BitcoinTalk forum'), _href='https://bitcointalk.org/index.php?topic=1054672.0',
              _target='_blank'),
        BR(),
        _class='row')

    return dict(h = h)

def index():
    sel_loc_view(request, response)
    
    h = CAT()
    h += DIV(
        u(T('Make new WAGER'),URL('hand', 'make')),
        u(T('Quick Make Simple WAGER'),URL('hand', 'make', vars={'quick':1})),
        u(T('See WAGERs List'), URL('hand', 'list')),
        _class='row')
    h += DIV(
        u(T('Shooters online auto bets'),URL('quick', 'index')),
        _class = 'row')
    h += HR()
    h += DIV(
        H2(T('Partners'), _class='header'),
        _class = 'row')
    h += DIV(
        A(IMG(_src=URL('static','images/logo-litecash.png'), _style='height:80px;padding-right:20px'),
            _title=T('Bitcoin Payment Gateway'), _href="http://LITE.cash", _class='header', _target='_blank'),' ',
        A(IMG(_src=URL('static','images/logo-7P-301.png'), _style='height:80px;padding-right:20px'),
            _title=T('Bitcoin payments for Tanks, Dota2, HoN, Allods, Prime World, etc.'), _href="https://7pay.in/more/index/2", _class='header', _target='_blank'),' ',
        A(IMG(_src='http://coinspot.io/wp-content/themes/bitcoin/images/logo-site.png', _style='height:40px;padding-right:20px'),
            _title=T('Bitcoin News'), _href="http://coinspot.io", _class='header', _target='_blank'),' ',
        A(IMG(_src='https://bitnovosti.files.wordpress.com/2015/03/bn_logo_256px.jpg?w=150', _style='height:80px;padding-right:20px'),
            _title=T('Bitcoin News'), _href="http://bitnovosti.com", _class='header', _target='_blank'),' ',
        BR(),BR(),
        DIV(H4(T('Online Games'), _class='header'), _class = 'row'),
        A(IMG(_src='http://static-ptl-us.gcdn.co/static/3.28.0.4/common/css/scss/header/img/wot-logo.png', _style='height:160px;padding-right:20px', _alt=''), _href="http://worldoftanks.com/", _class='header', _target='_blank'),' ',
        A(IMG(_src='https://allods.cdn.gmru.net/static/img/60/logo.png', _style='height:180px;padding-right:20px', _alt=''), _href="http://allods.mail.ru", _class='header', _target='_blank'),' ',
        A(IMG(_src='http://ru.playpw.com/welcome/lp1/ui/img/logo-pw.png', _style='height:60px;padding-right:20px', _alt=''), _href="http://ru.playpw.com", _class='header', _target='_blank'),' ',
        A(IMG(_src=URL('static','images/logos/HoN.png'), _style='height:100px;padding-right:20px', _alt=''), _href="http://www.heroesofnewerth.com/", _class='header', _target='_blank'),' ',
        BR(),BR(),
        DIV(H4(T('Others'), _class='header'), _class = 'row'),
        #A("Bet on tanks", _href='http://betontanks.com/', _target='_blank'), # - ставки на бои танков"!
        A(IMG(_src=URL('static','images/logos/logoNew.png'), _style='height:100px;padding-right:20px', _alt=''), _href="http://betontanks.com/", _class='header', _target='_blank'),' ',

        
        _class = 'row')
    
    return dict(h = DIV(h))
