import re
# region colors
G, W, R, B, C, P = "\033[32;1m", "\033[37;1;0m", "\033[31;1m", "\033[34;1m", "\033[36;1m", "\033[35;1m"
er, ok = "\033[31;1;4m"+"ERROR::"+W, "\033[34;1;4m"+"OK::"+W
# endregion

# region re
define = re.compile(r'(?P<type>int|float|double|string)\s+'
                    r'(?P<var>[^=\s*]+)\s*'
                    r'(\s*|((?P<op>=)(\s*(?P<num>[0-9.]+)|\s*(?P<string>[\"][\S\s]*[\"]))))\s*;')
equal = re.compile(r'(?P<left>[^=\s*])\s+(?P<op>=)\s*'
                   r'(?P<right>\.?\d+\.?\d*|[\"][\S\d\s]*[\"]|\S*)'
                   r'\s*;$', re.I)
condition = re.compile(r'if\s*\(\s*(?P<left>([\S^=])*\s*(?=\=)|\.?\d+\.?\d*)'
                       r'\s*(?P<op>==|!=|>=|<=|>|<)\s*'
                       r'(?P<right>\.?\d+\.?\d*|[a-z]+[0-9_]*[a-z]*)\s*\)\s*((:?)|{)$', re.M)
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


def variable(entry):
    if re.match(r'[\-_!@#$%^&*+()=\'".0-9]', entry):
        print(f"{er} {P}:: {entry}{W} don't start variables with {G}'_ 0..9 or symbols'{W}")
        return True
    elif re.search(r'[\-!@#$%^&*+=()"\']', entry):
        print(f"{er} {P}:: {entry}{W} don't use illegal chars in variables {G}'\"!@#$%^&*()+-={W}")
        return True
    else:
        return False


def declare(entry):
    if entry.startswith(('int', 'float', 'double', 'string')):
        if entry.endswith(';'):
            create = re.search(define, entry) if re.search(define, entry) else None
            if create:
                # variables ERROR
                print(create.group('var'))
                if variable(str(create.group('var'))):
                    pass
                elif not create.group('op'):
                    db[create.group('var')] = [create.group('type'), '']
                    print(f'{ok} {G}{create.group("type")} {B}{create.group("var")}{W}')
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
        # value = tmp.group('right')
        if variable(eq.group('left')):
            pass
        elif not db.get(eq.group('left')):
            print(f"{er} {P}:: {eq.group('left')}{W} not exist in database for info type: {C}REPORT{W}")
        elif db.get(assign):
            if db[eq.group('left')][0] == db[assign][0]:
                print(f"{ok} {P}{eq.group('left')}{W} = {B}{eq.group('right')}{W}")
            else:
                print(f"{er} {P}:: {code}{W} {eq.group('left')} and {assign} aren't same object,"
                      f" {R}{db[eq.group('left')][0]} != {db[assign][0]}{W}")
        elif re.fullmatch(r'([\d.]|\d)+', assign) and re.fullmatch(r'(int|float|double)', db[eq.group('left')][0]):
            # NUMERIC
            if re.fullmatch(r'int', db[eq.group('left')][0]) and re.fullmatch(r'(\d+)', assign):
                db[eq.group('left')][1] = eq.group('right')
                print(f"{ok} {B}{eq.group('left')}{W} = {eq.group('right')}")
            elif re.match(r'(float|double)', db[eq.group('left')][0]) and re.search(r'(\.(?=\d+)|(?<=\d)\.)', assign):
                if eq.group('right').startswith('.'):
                    val = '0' + assign
                elif eq.group('right').endswith('.'):
                    val = assign + '0'
                else:
                    val = assign
                db[eq.group('left')][1] = val
                print(f"{ok} {P}{eq.group('left')}{W} = {B}{eq.group('right')}{W}")
            else:
                print(f"{er} {P}:: {assign}{W} doesn't match with the variable {G}{eq.group('left')}{W}'s type")
        # STRING
        elif re.fullmatch(r'([\"][\s\S]*[\"])', assign) and re.fullmatch(r'string', db[eq.group('left')][0]):
            if not (assign[0] == '"' and assign[-1] == '"'):
                print(f"{er} {P}:: {assign} {W}string quote's ain't match together")
            elif re.search(r'\"', assign[1:-1]):
                print(f'{er} string {P}:: {assign[1:-1]}{W} contain extra quote')
            else:
                db[eq.group('left')][1] = assign[1:-1]
                print(f"{ok} {P}{eq.group('left')}{W} = {B}{assign[1:-1]}{W}")
        else:
            print(f"{er} {P}:: {assign}{W} doesn't match with the variable {G}{eq.group('left')}{W}'s type")
        return True


def xform(entry):
    if len(str(entry)) % 2 == 0:
        ppp = int((21 - len(str(entry)))/2) + 1
    else:
        ppp = int((21 - len(str(entry)))/2)
    lll = '_' * ppp
    return lll+str(entry)+lll if len(str(entry)) % 2 == 0 else lll+str(entry)+lll+'_'


# event = ('int x12 = 10;', 'float y2 = 20;', 'string z = "RHN";', 'double temp = 13;', 'string operator = "SE M1I";',
#          'string aaa;', 'aa = "RHN";', 'aaa = "si_-na12";', 'y2 = 1.2;', 'y2 = 10;', 'z = operator;', 'x12 = y2;',
#          'report')
i = 0
print(f'\nif you ever wanted see database type: {C}REPORT{W}')
while True:
    # code = input(':\n').strip()
    # code = event[i].strip()
    code = input(':\t').strip()
    # print(i, ':', end='\n')
    # define
    if declare(code):
        pass
    # equal
    elif equivalent(code):
        pass
    # if condition
    elif code.startswith('if'):
        if code.endswith((':', '{')):
            tmp = re.search(condition, code) if re.search(condition, code) else 'ERROR'
            if str(type(tmp)) == "<class 'str'>":
                if re.search(r'if\s*\(\s*(?=[_0-9]+)', code) or re.search(r'(=|<|>(?=[_0-9]+))', code):
                    print(f"{er}ERROR::{W} don't start variables with {R}_{W} or {R}numbers{W}")
                elif re.search(r'=(?= <|>|!|\s*)', code):
                    se = re.search(r'=(?= <|>|!|\s*)', code).span()[0]
                    x = 'white-space or number' if not se == '<' or '>' '!' else code[se:se+1]
                    print(f"{er}ERROR::{W} {R}( {code[se:se+2]} ){W} can't use {P}{x}{W} after {P}={W} or use it alone,"
                          f"use these:{P}>=, <=, !=, ==, >, <{W}")
                elif re.search(r'[<>!\s](?=[<>!\s])', code):
                    pos = re.search(r'[<>!]\s*(?=[<>!])', code).span()
                    print('{0}ERROR::{1} {2}{3}{1}'.format(er, W, R, ''.join(code[pos[0]:pos[1]+1].split())))
            elif re.match(r'\.?\d+\.?\d*', tmp.group(1)) and re.match(r'\.?\d+\.?\d*', tmp.group(3)):
                left, right = float(tmp.group(1)), float(tmp.group(3))
                op = {'==': 'True' if left == right else 'False', '!=': 'True' if not left == right else 'False',
                      '>=': 'True' if left >= right else 'False', '<=': 'True' if left <= right else 'False',
                      '>': 'True' if left > right else 'False', '<': 'True' if left < right else 'False'}
                print(f'{G}{left} {C}{tmp.group(2)} {G}{right}\n{B}{str(op.get(tmp.group(2)))}{W}')
            elif re.search(r'[a-z]+[0-9_]*[a-z]*', code):
                print(f'{G}{tmp.group(1)} {C}{tmp.group(2)} {G}{tmp.group(3)}')

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

    elif re.fullmatch(r'report', code, re.I):
        print(f'\n{P} . . . VARIABLE . . . {W}||{G} . . . . TYPE . . . . {W}||{B}  . . . VALUE . . .  {W}')
        for k, v in db.items():
            print(f'{P}{xform(k)}{G}  {xform(v[0])}{B}  {xform(v[1])}{W}')
    else:
        print(f'{er} unknown token {P}{code}{W}please start with a valid token')
    i += 1
