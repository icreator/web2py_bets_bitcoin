# -*- coding: utf-8 -*-

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires

def get_serv(s):
    if s.g_id and s.g_host_p:
        b_serv = db((db.b_servs.game_id == s.g_id)
                    & (db.b_servs.host_p == s.g_host_p)
                    & (db.b_servs.s_port == s.g_s_port or 0)
                    & (db.b_servs.zone_id == s.g_zone_id or 0 )).select().first()
        if b_serv:
            ids = b_serv.id
        else:
            ids = db.b_servs.insert( game_id = s.g_id,  host_p = s.g_host_p,
                    s_port = s.g_s_port or 0,
                    zone_id = s.g_zone_id or 0 )
        s.b_serv_id = ids
        return ids

def get_new_acc(s):
    import random
    import string
    token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(31))
    return token

def serv_resp(s):
    import gluon.contrib.simplejson as sj
    #r = sj.loads('{"name":"pl1","score":234,"deaths":13,"team":1}')
    return [{'name':'Team1', 'wins': 123,
          'players': [
            ['player1',6,34],
            ['player2',4,14],
            ['icreator',1,4],
            ],
         },
        {'name':'Team noobs', 'wins':7,
          'players': [
            ['pla_on',1,3],
            ['play_ss',3,4],
            ['icreator2',11,24],
            ],
         }]


def get_pay_acc():
    b_cond_id = request.args(0)
    if not b_cond_id: return T('b_cond_id is empty!')
    b_cond = db.b_conds(b_cond_id)
    if not b_cond: return T('b_cond with id %s not found!') % b_cond_id

    pay_sys_id = request.args(1)
    if not pay_sys_id: return T('pay_sys_id is empty!')
    pay_sys = db.pay_systems(pay_sys_id)
    if not pay_sys: return T('pay_sys with id %s not found!') % b_pay_sys_id

    pay_acc = db((db.b_cond_accs.b_cond_id == b_cond_id)
            & (db.b_cond_accs.pay_sys_id == pay_sys_id)).select().first()
    if pay_acc:
        acc = pay_acc.acc
        total = pay_acc.total
    else:
        acc = get_new_acc(1)
        ids = db.b_cond_accs.insert(b_cond_id = b_cond_id,
                 pay_sys_id = pay_sys_id,
                 acc = acc)
        total = 0.0
    # #SCRIPT("$('#host_form').animate({ height: 'show'  }, 'slow');"),
    return DIV(T('Send money to account [%s] (total payed: %s)') % (acc, total), _class='row btn_a pay_btn' )

# show
def show_b_game():
    b_game_id = request.args(0)
    if not b_game_id: return T('B_Game id is empty!')
    b_game = db.games(b_game_id)
    if not b_game: return T('B_Game with id %s not found!') % b_game_id
    
    h = CAT()
    
    if b_game.status == 'OPEN':
        # make bets
        h += DIV(T('You may make bets'), _class='row')
    for cond in db(db.b_conds.b_game_id == b_game_id).select():
        '''
    Field('name','string', length=30, comment='название величины (имя, номер команды или голы'),
    Field('srav','string', length=3, requires=IS_IN_SET(['==', '>', '<'])),
    Field('val','integer', default=0),
    Field('acc','string', length=60, comment='wallet addres for payments'),
    Field('res','boolean', default=False), # WIN?
        '''
        ps = CAT()
        for pay_sys in db(db.pay_systems.used == True).select():
            id_pay_acc = 'pay_acc_%s_%s' % (cond.id, pay_sys.id)
            ps += SPAN(pay_sys.name,
                    _onclick='ajax("%s", [], "%s")' % (URL('quick','get_pay_acc',args=[cond.id, pay_sys.id]), id_pay_acc),
                     _class='btn_a')
        h += DIV(
                DIV(
                        DIV(cond.name,' ',cond.srav,' ',cond.val,' ',cond.res, _class='col-sm-4'),
                        DIV(ps, _class='col-sm-8'),
                    _class='row'),
                    DIV(_id=id_pay_acc, _class='row'),
                #_onclick='ajax("%s", [], "%s")' % (URL('quick','b_conds',args=[cond.id]), '_'),
                _class='row b_cond_stats')
    return h

def make_b_game():
    tag = "$('#bg_list').html('%s');" ## обязательно кавычки одинарные - иначе они путаются там
    b_serv_id = get_serv(session)
    if not b_serv_id:
        return tag % T('b_serv_id is empty!')
    '''
    b_serv = db.b_servs(b_serv_id)
    if not b_serv: return tag % T('server with id %s not found!') % b_serv_id
    '''
    serv_resp = session.b_serv_resp
    if not serv_resp: return tag % T('serv_resp is empty!')
    #print serv_resp
    
    b_game_id = db.games.insert(
                b_serv_id = b_serv_id,
                map_id = session.g_map_id or 0,
                total = 12,
                status = 'OPEN'
                )
    for team in serv_resp:
        acc = get_new_acc(1)
        ids = db.b_conds.insert(b_game_id = b_game_id,
                 name = team['name'], srav = '>', val = -1,
                 )
    #print tag % bg_list()
    return tag % bg_list(b_serv_id)
    
def bg_list_1(g, cls='ins'):
    id_game = 'game%s' % g.id
    return DIV(
                DIV(H3(g.id, ':', g.status, ' ', g.total, _class = 'btn_a b ' + cls),
                    _onclick='ajax("%s", [], "%s")' % (URL('quick','show_b_game',args=[g.id]),id_game),
                    _class='col-sm-4'),
                DIV(T('Stats'), _id=id_game, _class='col-sm-8'),
                _class='row b_game_stats')

# список пари для этой игры
def bg_list(b_serv_id=None):
    b_serv_id = b_serv_id or session.b_serv_id
    '''
    if not b_serv_id: return T('b_serv_id is empty!')
    b_serv = db.b_servs(b_serv_id)
    if not b_serv: return T('b_serv with id %s not found!') % b_serv_id
    '''
    
    hh = DIV(T('Make BETs Game'),
        _onclick='ajax("%s", [], ":eval")' % URL('quick','make_b_game'),
        _class='row btn_a inv b')

    h = CAT()
    show_make_btn = True
    b_games = b_serv_id and db(db.games.b_serv_id==b_serv_id).select(orderby=~db.games.id)
    if b_games:
        h += DIV(T('List of bet-games:'), _class='row')
        hh1 = CAT()
        hh2 = CAT()
        hh3 = CAT()
        for g in b_games:
            # отсортируем по статусу
            if g.status == 'OPEN':
                # не показывать создание нового ппари
                show_make_btn = False
                hh1 += bg_list_1(g,'inv')
            elif g.status == 'RUN':
                show_make_btn = False
                hh2 += bg_list_1(g)
            else:
                hh3 += bg_list_1(g)
            
        h += DIV(hh1,hh2,hh3, _class='row')


    return (show_make_btn and hh or DIV()) + h

def test_serv():
    session.g_id = request.vars.get('g_id')
    session.g_host_p = request.vars.get('g_host_p')
    session.g_s_port = request.vars.get('g_s_port')
    if not session.g_host_p:
        return T('HOST:IP is empty...')
    session.g_zone_id = request.vars.get('g_zone_id')
    session.g_map_id = request.vars.get('g_map_id')
    #print session

    h = CAT(T('Coming soon'),'... ', T('Subscribe to receive news'))
    f = SQLFORM(db.subscr, fields=['email'])
    h += f
    if f.accepted:
        response.flash = T('accepted')
    
    return DIV(h, _class='row game_stats')
    
    r = serv_resp(session)
    session.b_serv_resp = r
    #h = CAT(T('For making a bet: 1.STEP: Select the Team - it make a payment address, 2.STEP: Click on that Team again'))
    h = CAT()
    i = 0
    for t in r:
        i +=1
        pls = CAT()
        for pl in t['players']:
            pls += DIV(pl[0],' +',pl[1],' x', pl[2], _class='row')
            
        h += DIV(
                DIV(H3(i,'.',t['name']),T('WINS'),': ',t['wins'], _class='col-sm-4'),
                DIV(pls,
                    _class='col-sm-4'),
                _class='row g_team_stats')

    return CAT(DIV(h, _class='row game_stats'), DIV(bg_list(), _id='bg_list', _class='row'), SCRIPT('$("html,body").animate({"scrollTop":500},"slow");'))

def index():
    response.title = None
    h = CAT(T('Coming soon'),'... ', T('Subscribe to receive news'))
    f = SQLFORM(db.subscr, fields=['email'])
    f.vars.val='e-sport want'
    h += f
    if f.process().accepted:
        response.flash = T('accepted')
    elif f.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(h=h)
    
    r = CAT()
    
    r += FORM(LABEL(T('Find GAME by least 2 chars'), _class='b'), INPUT(_name='n', _value=session.sel_game, _placeholder=T('insert 2 or more first shars')),
              INPUT(_type='submit', _value=T('Find')))
    n = request.vars.get('n') or session.sel_game
    session.sel_game = n
    
    if n:
        if len(n)<1:
            r += T('Input more chars!')
            return dict(r=r)
    else:
        r += T('Input find chars')
        return dict(r=r)

    recs = db(db.games.name.startswith(n)).select(orderby=db.games.name)
    if not recs: return dict(r=r + T('Not founded...'))
    
    r += LABEL(T('Founded games:'), _class='b')
    rr = CAT()
    for rec in recs:
    #for rec in db(db.games.name.like(n)).select(orderby=db.games.name):
        rr += SPAN(rec.name,
                       _onclick=
                           """$('#host_form').animate({ height: 'show'  }, 'slow');
                           $('#g_id').val("%s");
                           $('#g_name').val("%s");
                           $('#host_p').focus();
                           """ % (rec.id, rec.name),
                       _class='btn_a')
    r += DIV(rr, _class='row games_seek')
    r += DIV(
        P(),
        INPUT(_name='g_id', _id='g_id', _type='hidden', _value = session.g_id),
        DIV(
            DIV(
                INPUT(_name='g_name', _id='g_name', _readonly='readonly', _value = session.g_name),
                IMG(_src='', _heigh=100),
                _class='col-sm-4'),
            DIV(
                LABEL('IP:PORT', _class='b'), INPUT(_name='g_host_p', _value = session.g_host_p, _placeholder='23.95.60.173.1:36963', _id='host_p'),
                LABEL('Software PORT', _class='b'), INPUT(_name='g_s_port', _value = session.g_s_port or '0', _placeholder='0'),
                LABEL('ZONE', _class='b'), INPUT(_name='g_zone_id', _value = session.g_zone_id or '', _placeholder='0...9'),
                LABEL('MAP', _class='b'), INPUT(_name='g_map_id', _value = session.g_map_id or '', _placeholder='0...9'),
                _class='col-sm-4'),
            DIV(DIV(T('Test server'), _onclick = 'ajax("%s", ["g_id", "g_host_p", "g_s_port", "g_zone_id", "g_map_id"], "conn_res");\
               ' % URL('quick','test_serv', args=request.args, vars=request.vars),
               _class='col-sm-12 btn_a'),
               _class='col-sm-3'),
        _class='row'),
        DIV(_id='conn_res'),
        _id = 'host_form',
        _style='display:none',
        _class='row')
    #r += 
        
    return dict(r=DIV(r, _class='inv'))

def error():
    return dict()
