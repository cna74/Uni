import re
# region colors
G, W, R, B, C, P = "\033[32;1m", "\033[37;1;0m", "\033[31;1m", "\033[34;1m", "\033[36;1m", "\033[35;1m"
er, ok = "\033[31;1;4m"+"ERROR::"+W, "\033[34;1;4m"+"OK::"+W
# endregion

# region re
define = re.compile(r'(?P<type>int|float|double|string)\s+'
                    r'(?P<var>\S+)\s*'
                    r'(\s*|((?P<op>=)(\s*(?P<num>[0-9.]+)|\s*(?P<string>[\'\"][\S\d\s]*[\'\"]))))\s*;')
equal = re.compile(r'(?P<left>\S+)\s+=\s*'
                   r'(?P<right>\.?\d+\.?\d?|\S+)'
                   r'\s*;$', re.I)
condition = re.compile(r'if\s*\(\s*(?P<left>[a-z]+[0-9_]*[a-z]*|\.?\d+\.?\d*)'
                       r'\s*(?P<op>==|!=|>=|<=|>|<)\s*'
                       r'(?P<right>\.?\d+\.?\d*|[a-z]+[0-9_]*[a-z]*)\s*\)\s*((:?)|{)$', re.M)
loop_for = re.compile(r'for\s*\(\s*int\s+([a-z]+[0-9_]*[a-z]*)\s*=(\d*)\s*;\s*([a-z]+[0-9_]*[a-z]*)'
                      r'\s*(=|<=|>=|!=|<|>)\s*(\d*)\s*;\s*([a-z]+[0-9_]*[a-z]*)\s*'
                      r'(((?P<one>[+\-*/%])\s*(?P=one))|(?P<two>[+\-*/%]=\s*[0-9]+))\s*\):$', re.I)
loop_while = re.compile(r'while\s*\(?(True|False|[a-z]+[0-9_]*[a-z]*)\s*'
                        r'(?P<op>==|!=|>=|<=|>|<)\s*'
                        r'[0-9.]+\s*\)?:$', re.I)
# endregion

db = {}


def variable(tmp):
    if re.match(r'[_0-9]', str(tmp.group('var'))):
        print(f"{er} {P}:: {tmp.group('var')}{W} don't start variables with {P}'_ 0..9'{W}")
        return True
    elif not tmp.group('op'):
        db[tmp.group('var')] = [tmp.group('type'), '']
        print(f'{ok} {G}{tmp.group("type")} {C}{tmp.group("var")} {W}')
        return True
    else:
        return False


def declare(entry):
    if entry.startswith(('int', 'float', 'double', 'string')):
        if entry.endswith(';'):
            tmp = re.search(define, entry) if re.search(define, entry) else None
            if tmp:
                # variables ERROR
                if variable(tmp=tmp):
                    return True
                # string
                elif str(tmp.group('type')) == 'string':
                    c_str = tmp.group('string')
                    if not c_str:
                        print(f"{er} {P}{entry}{W} check the {P}variable-type{W} with the {P}value{W}")
                    elif not c_str[0] == c_str[-1]:
                        print(f"{er} {P}:: {c_str} {W}string quote's ain't match together")
                    elif re.search(r'([\']|[\"])', c_str[1:-1]):
                        print(f'{er} string {P}:: {c_str[1:-1]}{W} contain extra quote')
                    else:
                        db[tmp.group('var')] = {tmp.group('type'), c_str[1:-1]}
                        print(f'{ok} {G}string {C}{tmp.group("var")}{W} = {c_str[1:-1]}{W}')

                # numeric
                elif str(tmp.group('type')) == 'int' or 'float' or 'double':
                    c_int = tmp.group('num')
                    if not c_int:
                        print(f"{er} {P}:: {entry}{W} check the {P}variable-type{W} with the {P}value{W}")
                    elif re.search(r'([.]+\d*[.]+)', c_int):
                        print(f'{er} too mani dot {P}:: {c_int}{W}')
                    elif re.search(r'(\d+\.?)', c_int) and re.match(r'(float|double)', tmp.group('type')):
                        if not re.search(r'(\.(?=\d+)|(?<=\d)\.)', c_int):
                            db[tmp.group('var')] = [tmp.group('type'), c_int]
                            print(f'{ok} {G}{tmp.group("type")} {P}{tmp.group("var")} = {B}{c_int}{W}')
                        else:
                            if tmp.group('num').startswith('.'):
                                val = '0' + c_int
                            elif tmp.group('num').endswith('.'):
                                val = c_int + '0'
                            else:
                                val = c_int
                            db[tmp.group('var')] = [tmp.group('type'), val]
                            print(f'{ok} {G}{tmp.group("type")} {P}{tmp.group("var")}{W} = {B}{val}{W}')
                    elif re.match(r'\d+', str(tmp.group('num'))) and re.fullmatch(r'int', tmp.group('type')):
                        if re.search(r'\.', tmp.group('num')):
                            print(f"{er} {P}:: {entry}{W} can't define a int with float number")
                        else:
                            db[tmp.group('var')] = [tmp.group('type'), c_int]
                            print(f'{ok} {G}{tmp.group("type")} {C}{tmp.group("var")} = {B}{c_int}{W}')
            else:
                print(f'{er} {P}:: {entry}{W} invalid syntax')
        else:
            print(f'{er} {P}:: {entry} {W} semicolon missing')


def equivalent(entry):
    tmp = re.fullmatch(equal, entry) if re.fullmatch(equal, entry) else print('no')
    if tmp:
        if db[tmp.group('left')][0] == 'int':
            c_int = tmp.group('right')
            if re.search(r'(\d+\.?)', c_int):
                if not re.search(r'(\.(?=\d+)|(?<=\d)\.)', c_int):
                    db['left'][1] = tmp.group('right')
                else:
                    if tmp.group('right').startswith('.'):
                        val = '0' + c_int
                    elif tmp.group('right').endswith('.'):
                        val = c_int + '0'
                    else:
                        val = c_int
                    print(val)
    # if db[tmp.group('left')][0] == 'int':
    #     db[tmp.group('left')][1] = tmp.group('right')
    #     return True
    else:
        return False


# start
while True:
    code = input(':\n').strip()
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

    else:
        print(f'{er} unknown token {P}{code}{W} please start with a valid token')
    print(db)
