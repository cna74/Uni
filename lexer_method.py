import re
# region colors
G, W, R, B, C, P = "\033[32;1m", "\033[37m", "\033[31;1m", "\033[34;1m", "\033[36;1m", "\033[35;1m"
er, ok = "\033[31;1;4m", "\033[34;1;4m"
# endregion

code = 'if((:'.strip()

# region re
define = re.compile(r'(?P<type>int|flt|dbl|str)\s+([a-z]+[0-9_]*[a-z]*)'
                    r'(\s*|\s*=\s*(?P<num>[0-9.]+)\s*|\s*=\s*(?P<string>([\']|\")[\S\d\s]*([\']|\")));', re.I)

equal = re.compile(r'((\S+[0-9_]*)\s+[=]\s*'
                   r'(\d+\.|[a-z]+[0-9._]*)'
                   r'\s*;$)', re.I)

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

# define
if code.startswith(('int', 'flt', 'dbl', 'str')):
    if code.endswith(';'):
        tmp = re.search(define, code) if re.search(define, code) else None
        if not tmp:
            print("{}Error::{} missing {}'='".format(er, W, R, ))
        # string
        elif str(tmp.group('type')) == 'str':
            c_str = str(tmp.group('string'))
            if not re.search(r'=', code):
                print('{}{}{} {}{}'.format(C, tmp.group('type'), B, tmp.group(2), W))
            elif not c_str[0] == c_str[-1]:
                print("{}Error:{} string quote's ain't match together".format(R, W))
            elif re.search(r'([\']|[\"])', c_str[1:-1]):
                print('{}Error:{} strings contain extra quote'.format(R, W))
            else:
                print('{0}{1}{4} {2}{3}{4}'.format(C, 'string', G, c_str[1:-1], W))

        # numeric
        elif str(tmp.group('type')) == 'int' or 'flt' or 'dbl':
            c_int = str(tmp.group('num'))
            if re.search(r'([.]+\d*[.]+)', c_int):
                print('{0}Error::{1} too mani dot {0}{2}{1}'.format(er, W, c_int))
            else:
                if str(tmp.group('type')) == 'int' and re.fullmatch(r'(\d+[^.])', str(tmp.group(4))):
                    print('{}int{} {}{}{}'.format(C, W, B, c_int, W))
                elif str(tmp.group('type')) in ('flt', 'dbl') and re.search(r'(\d+\.?)', str(tmp.group(4))):
                    val = str(tmp.group(4)) + '.0' if not re.search(r'\.', tmp.group(4)) else str(tmp.group(4))
                    val = val + '0' if val.endswith('.') else val
                    print('{0}{1}{2} {3}{4}{2}'.format(C, tmp.group('type'), W, B, tmp.group(4)))
                elif not re.search(r'=', code):
                    print('{}{}{} {}{} {}{}'.format(ok, 'ok::', C, tmp.group('type'), B, tmp.group(2), W))
                else:
                    print('{0}Error::{1} check the {2}variable-type{1} and the {2}value{1}'.format(er, W, P))

# if condition
elif code.startswith('if'):
    if code.endswith((':', '{')):
        tmp = re.search(condition, code) if re.search(condition, code) else '{}ERROR::{} invalid syntax {}{}{}'.format(
            er, W, P, code, W)
        if str(type(tmp)) == "<class 'str'>":
            print(tmp)
        elif re.match(r'\.?\d+\.?\d*', tmp.group(1)) and re.match(r'\.?\d+\.?\d*', tmp.group(3)):
            left, right = float(tmp.group(1)), float(tmp.group(3))
            op = {'==': 'True' if left == right else 'False', '!=': 'True' if not left == right else 'False',
                  '>=': 'True' if left >= right else 'False', '<=': 'True' if left <= right else 'False',
                  '>': 'True' if left > right else 'False', '<': 'True' if left < right else 'False'}
            print('{}{} {}{} {}{}\n{}{}{}'.format(
                G, left, C, tmp.group(2), G, right, B, str(op.get(tmp.group(2))), W))
        elif re.search(r'[a-z]+[0-9_]*[a-z]*', code):
            print('{}{} {}{} {}{}'.format(
                G, tmp.group(1), C, tmp.group(2), G, tmp.group(3)))
            # need to resume

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
    print('{}ERROR::{} unknown token {}{}{} please start with a valid token'.format(er, W, P, code, W))
