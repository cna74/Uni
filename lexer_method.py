import re

green, white, red, blue, cyan, purple = "\033[32;1m", "\033[37m", "\033[31;1m", "\033[34;1m", "\033[36;1m", "\033[35;1m"
code = '  int x1 = \'sina\';  '

define = re.compile(r'(?P<type>int|flt|dbl|str)\s+([a-z]+[0-9_]*[a-z]*)'
                    r'(\s*|\s*=\s*(?P<int>[0-9.]+)\s*|\s*=\s*(?P<string>([\']|\")[\S\d\s]*([\']|\")));', re.I)

if code.strip().startswith(('int', 'flt', 'dbl', 'str')):
    if code.strip().endswith(';'):
        tmp = re.search(define, code)
        # string
        if str(tmp.group('type')) == 'str':
            c_str = str(tmp.group('string'))
            if not c_str[0] == c_str[-1]:
                print("{}Error:{} string quote's ain't match together".format(red, white))
            elif re.search(r'([\']|[\"])', c_str[1:-1]):
                print('{}Error:{} strings contain extra quote'.format(red, white))
            else:
                print('{}{}{}'.format(green, c_str[1:-1], white))
        # int float double
        elif str(tmp.group('type')) == 'int' or 'flt' or 'dbl':
            c_int = str(tmp.group('int'))
            if re.search(r'([.]+\d*[.]+)', c_int):
                print('{0}Error:{1} too mani dot {0}{2}{1}'.format(red, white, c_int))
            else:
                if str(tmp.group('type')) == 'int' and re.fullmatch(r'(\d+[^.])', str(tmp.group(4))):
                    print('{}int{} {}{}{}'.format(cyan, white, blue, c_int, white))
                elif str(tmp.group('type')) in ('flt', 'dbl') and re.search(r'[.]', str(tmp.group(4))):
                    print('{0}{1}{2} {3}{4}{2}'.format(cyan, tmp.group('type'), white, blue, c_int))
                else:
                    print('{0}Error:{1} check the {2}variable-type{1} and the {2}value{1}'.format(red, white, purple))
