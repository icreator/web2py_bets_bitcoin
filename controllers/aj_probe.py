# -*- coding: utf-8 -*-

AJ_FROM_SERVER = True
UPD_TIMEOUT =200000

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires

def show_conds():
    wager_id = session.wager_id
    
    h=CAT(
            SCRIPT("""
            if ( ! $('#show_conds').is(':visible')) {
                $('#show_conds').animate({ height: 'show' }, 1000);
            }
            $('#is_spin').html('');
            """),
        H4('CONDS'),
        )
    
    h += DIV(request.now)
    
    if not wager_id: return h

    h += DIV('wager_id:', wager_id, _class = 'game_stats row')
    return h


def show_wager():
    wager_id = session.wager_id
    
    h = CAT(
        SCRIPT("""
            if ( ! $('#show_wager').is(':visible')) {
                $('#show_wager').animate({ height: 'show' }, 1000);
            }
            $('#is_spin').html('');
            """),
        H4('WAGER'),
        )

    h += DIV(request.now)
    
    if not wager_id: return h
    h += A(H3(T('This WAGGER')), _href=URL('hand','index', args=[wager_id]))

    h += DIV('SPIN', _id='is_spin')
    h += BUTTON(T('Go to RUN'),TAG.i(_class='fa fa-refresh'),
           _type='submit',
           _class='btn btn-primary', _id='cond_add_btn',
           # тут вызов обновления LOAD внутри - чтобы последовательно было
           _onclick= """
               $('#show_wager1').animate({ height: 'hide'  }, 'fast');
               ajax('aj_probe','show_wager', [], {}, 'show_wager');"""
           )

    
    hh = LOAD('aj_probe', 'show_conds', args=[wager_id], ajax=True,
                times = 'infinity', timeout=UPD_TIMEOUT,
                target='show_conds', # вместо _id
                _style='display:none; height:0%;',
                _class='container', #  ### !!!! обязательно нужен - иначе анимация сбивается!
            )
    
    return h

# создадим спор на службе LITE.cash
def make_wager():

    session.wager_id = (int(session.wager_id or 0)) + 1
    
    if AJ_FROM_SERVER:
        response.js =  "jQuery('#show_conds').get(0).reload();"
        response.js +=  "jQuery('#show_wager').get(0).reload();"
        return CAT(
            request.now,' ',
            session.wager_id,
            #INPUT(_name='inp1'),
            SCRIPT('$("html,body").animate({"scrollTop":100},"slow");')
            )
    else:
        return """jQuery('#make_wager').text('%s');
                jQuery('#show_conds').get(0).reload();
                jQuery('#show_wager').get(0).reload();""" % ('%s %s' % (request.now, session.wager_id))

def index():
    response.title = None
    
    wager_id = request.args(0)
    session.wager_id = wager_id
    h = CAT()
    
    h += DIV(T('Make WAGER Game'),
        _onclick = AJ_FROM_SERVER and 'ajax("%s", [], "make_wager")' % URL('aj_probe','make_wager') or 'ajax("%s", [], ":eval")' % URL('aj_probe','make_wager'),
        _class='row btn_a inv b')
    h += DIV(_id = 'make_wager')
    
    h += LOAD('aj_probe', 'show_wager', args=[], ajax=True,
            times = 'infinity', timeout=UPD_TIMEOUT,
            target='show_wager', # вместо _id
            _style='display:none; height:0%;',
            _class='container', #  ### !!!! обязательно нужен - иначе анимация сбивается!
            )
    h += BR()
    h += LOAD('aj_probe', 'show_conds', args=[], ajax=True,
            times = 'infinity', timeout=UPD_TIMEOUT,
            target='show_conds', # вместо _id
            _style='display:none; height:0%;',
            _class='container', #  ### !!!! обязательно нужен - иначе анимация сбивается!
            )
    return dict( h = DIV(h, _class='row inv'))
