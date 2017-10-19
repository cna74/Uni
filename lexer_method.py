import re

# region colors
G, W, R, B, C, P = "\033[32;1m", "\033[37;1;0m", "\033[31;1m", "\033[34;1m", "\033[36;1m", "\033[35;1m"
er, ok = "\033[31;1;4m" + "ERROR::" + W, "\033[34;1;4m" + "OK::" + W
# endregion

# region re
define = re.compile(r'(?P<type>int|float|double|string|char)\s+'
                    r'(?P<var>[^=\s]+)\s*'
                    r'(\s*|((?P<op>=)(\s*(?P<num>[0-9.]+)|'
                    r'\s*(?P<strmath>(?P<one>[\"][\S\s]*[\"])\s*((?P<mul>[*])\s*(?P<to>[\d]+)|(?P<add>[+])\s*(?P<by>[\"][\S\s]*[\"])))|'
                    r'\s*(?P<string>[\"][\S\s]*[\"])|'
                    r'\s*(?P<char>[\'][\S\s]*[\'])|'
                    r'\s*(?P<math>[\d.]+\s*[+*\-/%]\s*[\d.]+))))\s*;')
equal = re.compile(r'(?P<var>[^=\s*]+)\s*=\s*'
                   r'(?P<right>\.?\d+\.?\d*|'
                   r'[\"\'][\S\s]*[\"\']|'
                   r'\s*(?P<math>[\d.]+\s*[+*\-/%]\s*[\d.]+)|'
                   r'\S*(?P<strmath>(?P<one>[\"][\S\s]*[\"])\s*((?P<mul>[*])\s*(?P<to>[\d]+)|(?P<add>[+])\s*(?P<by>[\"][\S\s]*[\"]))))'
                   r'\s*;$', re.I)
condition = re.compile(r'if\s*\(\s*(?P<left>[^=\s]+|\.?\d+\.?\d*)'
                       r'\s*(?P<op>[=<>!]+)\s*(?P<right>\.?\d+\.?\d*|[^=\s]+)\s*\)\s*((:?)|{)$', re.I)
loop_for = re.compile(r'for\s*\(\s*int\s+([a-z]+[0-9_]*[a-z]*)\s*=(\d*)\s*;\s*([a-z]+[0-9_]*[a-z]*)'
                      r'\s*(=|<=|>=|!=|<|>)\s*(\d*)\s*;\s*([a-z]+[0-9_]*[a-z]*)\s*'
                      r'(((?P<one>[+\-*/%])\s*(?P=one))|(?P<two>[+\-*/%]=\s*[0-9]+))\s*\):$', re.I)
loop_while = re.compile(r'while\s*\(?(True|False|[a-z]+[0-9_]*[a-z]*)\s*'
                        r'(?P<op>==|!=|>=|<=|>|<)\s*'
                        r'[0-9.]+\s*\)?:$', re.I)
# endregion

# region database
db = {}


# endregion


# region methods
def variable(entry):
    if re.match(r'[\-_!@#$%^&*+()=\'".0-9]', entry):
        print(f"{er} {P}:: {entry}{W} don't start variables with {G}'_ 0..9 or symbols'{W}")
        return True
    elif re.search(r'[\-!@#$%^&*+=()"\']', entry):
        print(f"{er} {P}:: {entry}{W} don't use illegal chars in variables {G}'\"!@#$%^&*()+-={W}")
        return True
    else:
        return False


def mth(entry, tip=True):
    if entry.group('math'):
        db[entry.group('var')] = [entry.group('type'), eval(entry.group('math'))]
        print(f"{ok} {entry.group('var')} = {eval(entry.group('math'))}")
    elif entry.group('strmath'):
        if entry.group('mul') and int(entry.group('to')) > 0 and tip:
            db[entry.group('var')] = [entry.group('type'), str(entry.group('one'))[1:-1] * int(entry.group('to'))]
            print(str(entry.group('one'))[1:-1] * int(entry.group('to')))
        elif entry.group('mul') and int(entry.group('to')) > 0 and not tip:
            db[entry.group('var')][1] = str(entry.group('one'))[1:-1] * int(entry.group('to'))
            print(str(entry.group('one'))[1:-1] * int(entry.group('to')))
        elif entry.group('add') and entry.group('by') and tip:
            db[entry.group('var')] = [entry.group('type'), str(entry.group('one'))[1:-1] + entry.group('by')[1:-1]]
            print(str(entry.group('one'))[1:-1] + entry.group('by')[1:-1])
        elif entry.group('add') and entry.group('by') and not tip:
            db[entry.group('var')][1] = str(entry.group('one'))[1:-1] + entry.group('by')[1:-1]
            print(str(entry.group('one'))[1:-1] + entry.group('by')[1:-1])
        return True
    else:
        return False


def if_cond(entry):
    if entry.startswith('if'):
        if entry.endswith((':', '{')):
            if_c = re.search(condition, entry) if re.search(condition, entry) else None
            if if_c:
                if not db.get(if_c.group('left')):
                    print(f"{er} {P}:: {if_c.group('left')}{W} undefined variable")
                elif not if_c.group('op') in ('==', '>=', '<=', '!=', '<', '>'):
                    print(f"{er} {P}:: {if_c.group('op')}{W} is wrong, use one of these {G}==, >=, <=, !=, >, <{W}")
                if not db.get(if_c.group('right')):
                    print(f"{er} {P}:: {if_c.group('right')}{W} undefined variable")
                elif re.fullmatch(r'(\d*\.\d+|\d+\.\d*|\d+)', if_c.group('left')) or \
                        re.fullmatch(r'(\d*\.\d+|\d+\.\d*|\d+)', if_c.group('right')):
                    left, right = float(if_c.group('left')), float(if_c.group('right'))
                    op = {'==': 'True' if left == right else 'False', '!=': 'True' if not left == right else 'False',
                          '>=': 'True' if left >= right else 'False', '<=': 'True' if left <= right else 'False',
                          '>': 'True' if left > right else 'False', '<': 'True' if left < right else 'False'}
                    print(f'{G}{left} {C}{if_c.group(2)} {G}{right}\n{B}{str(op.get(if_c.group(2)))}{W}')
                elif variable(if_c.group('left')) or variable(if_c.group('right')):
                    pass
                return True


def declare(entry):
    if entry.startswith(('int', 'float', 'double', 'string', 'char')):
        if entry.endswith(';'):
            create = re.search(define, entry) if re.search(define, entry) else None
            if create:
                # variables ERROR
                if variable(str(create.group('var'))):
                    pass
                elif not create.group('op'):
                    db[create.group('var')] = [create.group('type'), '']
                    print(f'{ok} {G}{create.group("type")} {B}{create.group("var")}{W}')
                elif mth(create, tip=True):
                    pass
                # string
                elif str(create.group('type')) == 'string':
                    c_str = create.group('string')
                    if not c_str:
                        print(f"{er} {P}{entry}{W} check the {P}variable-type{W} with the {P}value{W}")
                    elif not (c_str[0] == '"' and c_str[-1] == '"'):
                        print(f"{er} {P}:: {c_str} {W}string quote's ain't match together")
                    elif re.search(r'\"', c_str[1:-1]):
                        print(f'{er} string {P}:: {c_str[1:-1]}{W} contain extra quote')
                    else:
                        db[create.group('var')] = [create.group('type'), c_str[1:-1]]
                        print(f"{ok} {G}{create.group('type')} {P}{create.group('var')}{W} = {B}{c_str[1:-1]}{W}")
                # char
                elif str(create.group('type')) == 'char':
                    c_chr = create.group('char')
                    if not c_chr:
                        print(f"{er} {P}:: {entry}{W} check the {P}variable-type{W} with the {P}value{W}")
                    elif not (c_chr[0] == '\'' and c_chr[-1] == '\''):
                        print(f"{er} {P}:: {c_chr}{W} char quote's ain't match together")
                    elif len(c_chr[1:-1]) > 1 and not c_chr[1:-1] == "\\'":
                        print(f"{er} {P}:: {c_chr}{W} chars only take one value")
                    elif c_chr[1:-1] == "'":
                        print(f"{er} {P}:: {c_chr}{W} can't assign => ' <= to char")
                    elif c_chr[1:-1] == "\\'":
                        db[create.group('var')] = [create.group('type'), c_chr[2:-1]]
                        print(f"{ok} {G}{create.group('type')} {P}{create.group('var')}{W} = {B}{c_chr[2:-1]}{W}")
                    else:
                        db[create.group('var')] = [create.group('type'), c_chr[1:-1]]
                        print(f"{ok} {G}{create.group('type')} {P}{create.group('var')}{W} = {B}{c_chr[1:-1]}{W}")
                # numeric
                elif str(create.group('type')) == 'int' or 'float' or 'double':
                    c_int = create.group('num')
                    if not c_int:
                        print(f"{er} {P}:: {entry}{W} check the {P}variable-type{W} with the {P}value{W}")
                    elif re.search(r'([.]+\d*[.]+)', c_int):
                        print(f'{er} too mani dot {P}:: {c_int}{W}')
                    elif re.search(r'(\d+\.?)', c_int) and re.match(r'(float|double)', create.group('type')):
                        if not re.search(r'(\.(?=\d+)|(?<=\d)\.)', c_int):
                            c_int = str(c_int) + '.0'
                            db[create.group('var')] = [create.group('type'), c_int]
                            print(f'{ok} {G}{create.group("type")} {P}{create.group("var")}{W} = {B}{c_int}{W}')
                        else:
                            if str(create.group('num')).startswith('.'):
                                val = '0' + c_int
                            elif str(create.group('num')).endswith('.'):
                                val = str(c_int) + '0'
                            else:
                                val = c_int
                            db[create.group('var')] = [create.group('type'), val]
                            print(f'{ok} {G}{create.group("type")} {P}{create.group("var")}{W} = {B}{val}{W}')
                    elif re.fullmatch(r'\d+', str(create.group('num'))) and re.fullmatch(r'int', create.group('type')):
                        if re.search(r'\.', create.group('num')):
                            print(f"{er} {P}:: {entry}{W} can't define a int with float number")
                        else:
                            db[create.group('var')] = [create.group('type'), c_int]
                            print(f'{ok} {G}{create.group("type")} {P}{create.group("var")}{W} = {B}{c_int}{W}')
                    else:
                        print(f"{er} {P}:: {code}{W} {create.group('type')} doesn't match with {c_int}")
            else:
                print(f'{er} {P}:: {entry}{W} invalid syntax')
        else:
            print(f'{er} {P}:: {entry}{W} semicolon missing')
        return True
    else:
        return False


def equivalent(entry):
    eq = re.fullmatch(equal, entry) if re.fullmatch(equal, entry) else None
    if eq:
        assign = eq.group('right')
        if variable(eq.group('var')):
            pass
        elif mth(eq, tip=False):
            pass
        elif db.get(assign):
            if db[eq.group('var')][0] == db[assign][0]:
                db[eq.group('var')][1] = db[assign][1]
                print(f"{ok} {eq.group('var')} = {assign}")
            else:
                print(f"{er} {P}:: {entry}{W} variables ain't match together")

        elif not db.get(eq.group('var')):
            print(f"{er} {P}:: {eq.group('var')}{W} not exist in database for info type: {C}REPORT{W}")
        elif db.get(assign):
            if db[eq.group('var')][0] == db[assign][0]:
                print(f"{ok} {P}{eq.group('var')}{W} = {B}{eq.group('right')}{W}")
            else:
                print(f"{er} {P}:: {code}{W} {eq.group('var')} and {assign} aren't same object,"
                      f" {R}{db[eq.group('var')][0]} != {db[assign][0]}{W}")
        # NUMERIC
        elif re.fullmatch(r'([\d.]|\d)+', assign) and re.fullmatch(r'(int|float|double)', db[eq.group('var')][0]):
            if re.fullmatch(r'int', db[eq.group('var')][0]) and re.fullmatch(r'(\d+)', assign):
                db[eq.group('var')][1] = eq.group('right')
                print(f"{ok} {B}{eq.group('var')}{W} = {eq.group('right')}")
            elif re.match(r'(float|double)', db[eq.group('var')][0]) and re.search(r'(\.(?=\d+)|(?<=\d)\.)', assign):
                if eq.group('right').startswith('.'):
                    val = '0' + assign
                elif eq.group('right').endswith('.'):
                    val = assign + '0'
                else:
                    val = assign
                db[eq.group('var')][1] = val
                print(f"{ok} {P}{eq.group('var')}{W} = {B}{eq.group('right')}{W}")
            else:
                print(f"{er} {P}:: {assign}{W} doesn't match with the variable {G}{eq.group('var')}{W}'s type => {R}"
                      f"{db[eq.group('var')][0]}{W}")
        # STRING
        elif re.fullmatch(r'([\"][\s\S]*[\"])', assign) and re.fullmatch(r'string', db[eq.group('var')][0]):
            if not (assign[0] == '"' and assign[-1] == '"'):
                print(f"{er} {P}:: {assign} {W}string's quotes ain't match together")
            elif re.search(r'\"', assign[1:-1]):
                print(f'{er} string {P}:: {assign[1:-1]}{W} contain extra quote')
            else:
                db[eq.group('var')][1] = assign[1:-1]
                print(f"{ok} {P}{eq.group('var')}{W} = {B}{assign[1:-1]}{W}")
        # char
        elif re.fullmatch(r'([\'][\s\S]*[\'])', assign) and re.fullmatch(r'char', db[eq.group('var')][0]):
            if len(assign[1:-1]) > 1 and not assign[1:-1] == "\\'":
                print(f"{er} {P}:: {assign}{W} chars only take one value")
            elif assign[1:-1] == "'":
                print(f"{er} {P}:: {assign}{W} can't assign => ' <= to char try \"\\'\"")
            elif assign[1:-1] == "\\'":
                db[eq.group('left')][1] = assign[2:-1]
                print(f"{ok} {G}{eq.group('var')} = {B}{assign[2:-1]}{W}")
            else:
                db[eq.group('left')][1] = assign[1:-1]
                print(f"{ok} {P}{eq.group('var')}{W} = {B}{assign[1:-1]}{W}")
        else:
            print(f"{er} {P}:: {assign}{W} doesn't match with the variable {G}{eq.group('var')}{W}'s type => {R}"
                  f"{db[eq.group('var')][0]}{W}")
        return True


def xform(entry):
    if len(str(entry)) % 2 == 0:
        ppp = int((21 - len(str(entry))) / 2) + 1
    else:
        ppp = int((21 - len(str(entry))) / 2)
    lll = '_' * ppp
    return lll + str(entry) + lll if len(str(entry)) % 2 == 0 else lll + str(entry) + lll + '_'


# endregion


# event = ('int x12 = 10;', 'float y2 = 20;', 'string z = "RHN";', 'double temp = 13;', 'string operator = "SE M1I";',
#          'string aaa;', 'aa = "RHN";', 'aaa = "si_-na12";', 'y2 = 1.2;', 'y2 = 10;', 'z = operator;', 'x12 = y2;',
#          '',
#          'report')
# region start
i = 0
print(f'\nif you ever wanted see database type: {C}REPORT{W} or {C}RT{W}')
while True:
    # code = event[i].strip()
    code = input(':\t').strip()
    # print(i, code, end='\n')
    # define
    if declare(code):
        pass
    # equal
    elif equivalent(code):
        pass
    # if condition
    elif if_cond(code):
        pass
    # for loop
    elif code.startswith('for'):
        if code.endswith(':'):
            if re.search(loop_for, code):
                tmp = re.match(loop_for, code)
                until = {'=': 'equal to', '<': 'smaller than', '>': 'greater than', '<=': 'equal or smaller than',
                         '>=': 'equal or greater than', '!=': 'not equal with'}
                step = tmp.group('two')[0:1] + tmp.group('two')[2:] if tmp.group('two') else tmp.group(8)
                print('{0}OK::{1} int {2}{3}{4} from {2}{5}{4} until {6}{7} {2}{8}{4} step:: {9}{10}{4}'.format(
                    ok, C, B, tmp.group(1), W, tmp.group(2), R, until.get(tmp.group(4)), tmp.group(5), G, step))
            else:
                if not re.search(r'[;]{2}', code[:-1]):
                    print('{}ERROR::{} not enough semicolon {}{}{} '.format(
                        er, W, P, ' '.join(code.split()).strip()[3:], W))
                if not re.search(loop_for, code):
                    print('{}ERROR::{} check your loop again {}{}{} something is wrong'.format(
                        er, W, P, ' '.join(code.split()), W))

    elif re.fullmatch(r'(report|rt)', code, re.I):
        print(f'\n{P} . . . VARIABLE . . . {W}||{G} . . . . TYPE . . . . {W}||{B}  . . . VALUE . . .  {W}')
        for k, v in db.items():
            print(f'{P}{xform(k)}{G}  {xform(v[0])}{B}  {xform(v[1])}{W}')
    else:
        print(f'{er} unknown token {P}{code}{W}please start with a valid token')
    i += 1
# endregion
