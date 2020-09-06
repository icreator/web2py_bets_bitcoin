# coding: utf8
# попробовать что-либо вида

if not request.is_local: raise HTTP(20, 'error is')

def index():
    h = CAT()
    h += DIV(
        DIV(
            DIV(P(T('Make mew full WAGER'), _href=URL(),
              _class='btn_mc2'),
            _class='btn_mc1'),
        _class='col-sm-4 btn_mc'),
        DIV(
            DIV(P(T('Quck Make simple WAGER'), _href=URL(),
              _class='btn_mc2'),
            _class='btn_mc1'),
        _class='col-sm-4 btn_mc'),
        DIV(
            DIV(SPAN(T('See WAGER'),
              _class='btn_mc2'),
             _onclick="location.href='%s'" % URL('hand', 'index'),
            _class='btn_mc1'),
        _class='col-sm-4 btn_mc'),
        _class='row')
    return dict(h = h)

# locz/en/1
def locz():
    import locz
    rec = db.wagers[request.args(1) or 1]
    rec_locz = locz.get(db.wagers, rec, request.args(0))
    return rec_locz.name
