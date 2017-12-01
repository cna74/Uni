import re

# region vars
G, W, R, B, C, P = "\033[32;1m", "\033[37;1;0m", "\033[31;1m", "\033[34;1m", "\033[36;1m", "\033[35;1m"
er, ok , warn= "\033[31;1;4m" + "ERROR::" + W, "\033[34;1;4m" + "OK::" + W, "\033[32;1;4m" + 'WARN::' + W
db = {}
# endregion

# region re
define = re.compile(r'(?P<type>int|float|double|string|char)\s+'
                    r'(?P<var>[^=\s]+)\s*'
                    r'(\s*|'
                    r'((?P<op>=)\s*((?P<num>[0-9.]+)|'
                    r'\s*(?P<math>((?P<s11>[\"][\S\s]*[\"])|(?P<s12>[\d.]+)|(?P<s13>[^=\s]+))\s*(?P<mul>[*+/%\-])\s*((?P<bs>[\"][\S\s]*[\"])|(?P<bn>[\d]+)|(?P<bv>[^=\s]+)))|'
                    r'\s*(?P<string>[\"][\S\s]*[\"])|'
                    r'\s*(?P<char>[\'][\S\s]*[\']))))\s*;')
equal = re.compile(r'(?P<var>[^=\s*]+)\s*=\s*'
                   r'(?P<right>\.?\d+\.?\d*|'
                   r'(?P<math>((?P<s11>[\"][\S\s]*[\"])|(?P<s12>[\d.]+)|(?P<s13>[^=\s]+))'
                   r'\s*(?P<mul>[*+/%\-])\s*'
                   r'((?P<bs>[\"][\S\s]*[\"])|(?P<bn>[\d]+)|(?P<bv>[^=\s]+)))|'
                   r'[\"\'][\S\s]*[\"\']|'
                   r'[^=\s*]+)'
                   r'\s*;', re.I)
condition = re.compile(r'if\s*\(\s*((?P<s11>[\"][\S\s]*[\"])|(?P<s12>[\d.]+)|(?P<s13>[^=\s]+))'
                       r'\s*(?P<op>[=<>!]+)\s*'
                       r'((?P<bs>[\"][\S\s]*[\"])|(?P<bn>[\d]+)|(?P<bv>[^=\s]+))\s*\)\s*'
                       r'{(?P<stmt>[\s\S]+|\s*)}', re.I)
loop_for = re.compile(r'for\s*\(\s*'
                      r'(int\s+(?P<v1>[^=\s]+)\s*=\s*(?P<n1>\d+|[^=\s]+)|(?P<v11>[^=\s]+))\s*;'
                      r'\s*(?P<v2>[^=\s]+)\s*(?P<op>[=<>!]+)\s*(?P<n2>\d+|[^=\s]+)\s*;'
                      r'\s*(?P<v3>[^=\s]+)\s*(((?P<one>[+\-*/%]{2})\s*)|(?P<two>[+\-*/%]=\s*\d+\s*))\s*\)'
                      r'{(?P<stmt>[\s\S]+|\s*)}', re.I)
loop_while = re.compile(r'while\s*\(\s*((?P<s11>[\"][\S\s]*[\"])|(?P<s12>[\d.]+)|(?P<s13>[^=\s]+))'
                        r'\s*(?P<op>[=<>!]+)\s*'
                        r'((?P<bs>[\"][\S\s]*[\"])|(?P<bn>[\d]+)|(?P<bv>[^=\s]+))\s*\)\s*'
                        r'{(?P<stmt>[\s\S]+|\s*)}$', re.I)
# endregion


# region methods
def declare(entry: str) -> bool:
    if entry.startswith(('int', 'float', 'double', 'string', 'char')):
        if entry.endswith(';'):
            create = re.search(define, entry) if re.search(define, entry) else None
            if create:
                # variables ERROR
                if variable(str(create.group('var'))):
                    pass
                elif db.get(create.group('var')):
                    print(f"{er} {P}:: {code}{W} variable {G}{create.group('var')}{W}'s is already defined")
                elif not create.group('op'):
                    db[create.group('var')] = [create.group('type'), '']
                    print(f'{ok} {G}{create.group("type")} {B}{create.group("var")}{W}')
                elif create.group('math') and mth(create):
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
        elif eq.group('math') and mth(eq):
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
            elif re.match(r'(float|double)', db[eq.group('var')][0]) and re.search(r'([\d.]|[\d])', assign):
                if eq.group('right').startswith('.'):
                    val = '0' + assign
                elif eq.group('right').endswith('.'):
                    val = assign + '0'
                else:
                    val = assign + '.0'
                db[eq.group('var')][1] = val
                print(f"{ok} {P}{eq.group('var')}{W} = {B}{val}{W}")
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
                db[eq.group('var')][1] = assign[2:-1]
                print(f"{ok} {G}{eq.group('var')} = {B}{assign[2:-1]}{W}")
            else:
                db[eq.group('var')][1] = assign[1:-1]
                print(f"{ok} {P}{eq.group('var')}{W} = {B}{assign[1:-1]}{W}")
        else:
            print(f"{er} {P}:: {assign}{W} doesn't match with the variable {G}{eq.group('var')}{W}'s type => {R}"
                  f"{db[eq.group('var')][0]}{W}")
        return True


def if_cond(entry):
    if entry.endswith('}'):
        if_c = re.search(condition, entry) if re.search(condition, entry) else None
        if if_c:
            s1 = s2 = mul = op = None
            if if_c.group('s12'):
                s1 = if_c.group('s12')
            elif db.get(if_c.group('s13')):
                s1 = db[if_c.group('s13')][1]
            mul = if_c.group('op')
            if db.get(if_c.group('bv')):
                s2 = db[if_c.group('bv')][1]
            elif if_c.group('bn'):
                s2 = str(if_c.group('bn'))
            if iscond(s1, s2, mul):
                if declare(if_c.group('stmt')):
                    pass
                elif equivalent(if_c.group('stmt')):
                    pass
            else:
                print(f"{warn} condition is False so {P}::{if_c.group('stmt')}{W} is unreachable")
            return True
    else:
        print(f'{er} {P}::{code}{W} forgot closing statement')
        return True


def for_loop(entry):
    # entry = code
    if entry.endswith('}'):
        if re.search(loop_for, entry):
            tmp = re.match(loop_for, entry) if re.search(loop_for, entry) else None
            v1 = v2 = v3 = n1 = n2 = None
            if tmp:
                if tmp.group('v1') and not variable(tmp.group('v1')):
                    v1 = tmp.group('v1')
                elif tmp.group('v11') and not variable(tmp.group('v11')):
                    v1 = tmp.group('v11')
                    if not db.get(v1):
                        print(f"{er} {P}:: {v1}{W} undefined variable")
                v2, v3 = tmp.group('v2'), tmp.group('v3')
                n1, n2 = tmp.group('n1') if tmp.group('n1') else db[v1][1], tmp.group('n2')
                op = tmp.group('op') if tmp.group('op') in ('=', '<', '>', '<=', '=>', '!=') else None
                if not v1 == v2 == v3:
                    print(f"{er} ::{P}({v1}|{v2}|{v3}){W} don't use multi iterable objects in for loop")
                if not op:
                    print(f"{er} {P}:: {tmp.group('op')}{W} use valid operands like ({C} = , < , > , <= , >= , != {W})")
                until = {'=': 0, '<': -1, '>': 1, '<=': 'equal or smaller than',
                         '>=': 'equal or greater than', '!=': 'not equal with'}
                step = ''.join(str(tmp.group('two')).split()) if tmp.group('two') else tmp.group('one')
                if all([ex for ex in (v1, v2, v3, n1, n2, op, step)]):
                    print(f"{v1} {P}from{W} {n1} till {P}{until.get(op)}{W} {n2} {P}with step ->{W} {step}")
                return True
            else:
                print(er)
                return True
    else:
        print(f"{er} {P}::{entry}{W} missing {G}{'}'}{W}")
        return True


def while_loop(entry):
    if entry.endswith('}'):
        if re.search(loop_while, entry):
            tmp = re.match(loop_while, entry) if re.search(loop_while, entry) else None
            if tmp:
                s1 = s2 = mul = op = None
                if tmp.group('s12'):
                    s1 = tmp.group('s12')
                elif db.get(tmp.group('s13')):
                    s1 = db[tmp.group('s13')][1]
                mul = tmp.group('op')
                if db.get(tmp.group('bv')):
                    s2 = db[tmp.group('bv')][1]
                elif tmp.group('bn'):
                    s2 = str(tmp.group('bn'))
                if iscond(s1, s2, mul):
                    if declare(tmp.group('stmt')):
                        pass
                    elif equivalent(tmp.group('stmt')):
                        pass
                    else:
                        print(f"{warn} empty statement!")
                else:
                    print(f"{G}WARN::{W} condition is False so {P}::{tmp.group('stmt')}{W} is unreachable")
                return True


def iscond(s1, s2, mul):
    left = right = op = None
    if re.fullmatch(r'(\d*\.\d+|\d+\.\d*|\d+)', s1) and re.fullmatch(r'(\d*\.\d+|\d+\.\d*|\d+)', s2):
        left, right = float(s1), float(s2)
        op = {'==': 'True' if left == right else 'False', '!=': 'True' if not left == right else 'False',
              '>=': 'True' if left >= right else 'False', '<=': 'True' if left <= right else 'False',
              '>': 'True' if left > right else 'False', '<': 'True' if left < right else 'False'}
    if op.get(mul) == 'True':
        return True
    else:
        return False


def variable(entry):
    if re.match(r'[\-_!@#$%^&*+()=\'".0-9]', entry):
        print(f"{er} {P}:: {entry}{W} don't start variables with {G}'_ 0..9 or symbols'{W}")
        return True
    elif re.search(r'[\-!@#$%^&*+=()"\']', entry):
        print(f"{er} {P}:: {entry}{W} don't use illegal chars in variables {G}'\"!@#$%^&*()+-={W}")
        return True
    else:
        return False


def ssmk(entry):
    s1 = s2 = mul = kind = None
    if db.get(entry.group('var')):
        kind = db[entry.group('var')][0]
    elif entry.group('type'):
        kind = entry.group('type')
    if entry.group('s11'):
        s1 = entry.group('s11')[1:-1]
    elif entry.group('s12'):
        s1 = entry.group('s12')
    elif entry.group('s13'):
        s1 = db[entry.group('s13')][1] if db.get(entry.group('s13')) else None
    mul = str(entry.group('mul'))
    if entry.group('bs'):
        s2 = entry.group('bs')[1:-1] if entry.group('bs')[0] == entry.group('bs')[-1] == '"' else None
    elif entry.group('bn'):
        s2 = entry.group('bn')
    elif entry.group('bv'):
        s2 = str(db[entry.group('bv')][1]) if db.get(entry.group('bv')) else None
    return s1, s2, mul, kind


def mth(entry):
    s1, s2, mul, kind = ssmk(entry)
    # print(s1, mul, s2)
    if mul == '*' and s1 and s2.isnumeric() and kind == 'string':
        print(f"{ok} {P}{entry.group('var')}{W} = {C}{s1*int(s2)}{W}")
        db.update({entry.group('var'): ('string', s1*int(s2))})
    elif mul == '+' and s1 and s2 and kind == 'string':
        print(f"{ok} {P}{entry.group('var')}{W} = {C}{s1+s2}{W}")
        db.update({entry.group('var'): ('string', s1+s2)})
    elif str(s1).isdigit() and str(s2).isdigit() and kind == 'int':
        print(f"{ok} {P}{entry.group('var')}{W} = {C}{int(eval(str(s1)+str(mul)+str(s2)))}{W}")
        db.update({entry.group('var'): ('int', int(eval(str(s1)+str(mul)+str(s2))))})
    elif s1.isnumeric() and s2.isnumeric() and kind == 'float':
        print(f"{ok} {P}{entry.group('var')}{W} = {C}{float(eval(entry.group('math')))}{W}")
        db.update({entry.group('var'): ('float', float(eval(entry.group('math'))))})
    else:
        return False
    return True


def xform(entry):
    if len(str(entry)) % 2 == 0:
        ppp = int((21 - len(str(entry))) / 2) + 1
    else:
        ppp = int((21 - len(str(entry))) / 2)
    lll = '_' * ppp
    return lll + str(entry) + lll if len(str(entry)) % 2 == 0 else lll + str(entry) + lll + '_'


# endregion

# event = ('string x = "sina";', 'string y = x*3;', 'string z = x+" rhn";',
#          'string p;', 'p = x+x;', 'int j = 2*2;', 'float i = 2*3;', 'rt')

# region start


i = 0
print(f'\nif you ever wanted to see database type: {C}REPORT{W} or {C}RT{W}')
while True:
    # code = event[i].strip()
    code = ' '.join(input(':\t').split())
    # print(i+1, code, end='\n')
    # define
    if declare(code):
        pass
    # equal
    elif equivalent(code):
        pass
    # if condition
    elif code.startswith('if'):
        if_cond(code)
    # for loop
    elif code.startswith('for'):
        for_loop(code)
    elif code.startswith('while'):
        while_loop(code)
    elif re.fullmatch(r'(report|rt)', code, re.I):
        print(f'\n{P} . . . VARIABLE . . . {W}||{G} . . . . TYPE . . . . {W}||{B}  . . . VALUE . . .  {W}')
        for k, v in db.items():
            print(f'{P}{xform(k)}{G}  {xform(v[0])}{B}  {xform(v[1])}{W}')
    else:
        print(f'{er} unknown token {P}{code}{W}please start with a valid token')
    i += 1
# endregion
