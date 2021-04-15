from typing import List
from config import args

RESERVED_WORD = {}
RESERVED_WORD['int'] = 2
RESERVED_WORD['struct'] = 3
RESERVED_WORD['bool'] = 4
RESERVED_WORD['float'] = 5
RESERVED_WORD['if'] = 6
RESERVED_WORD['else'] = 7
RESERVED_WORD['do'] = 8
RESERVED_WORD['while'] = 9
RESERVED_WORD['return'] = 10
RESERVED_WORD['void'] = 11
RESERVED_WORD['true'] = 39
RESERVED_WORD['false'] = 40


def isreserved(s: str) -> int:
    '''判断是否为保留字

    若为保留字则返回相应的类别码
    否则，返回'id'

    Args:
        s: 待判断的字符串

    Returns:
        一个整数
    '''
    if s in RESERVED_WORD:
        return s
    return 'id'


def isconst(s: str) -> bool:
    '''判断是否为常数值

    判断的依据为八进制数、十进制数、十六进制数、浮点数、科学计数法

    Args:
        s: 待判断的字符串

    Returns:
        是否为合法常数值
    '''
    if len(s) == 1:
        return True

    if s[0] == '0':
        if s[1] != 'x':
            for i in range(2, len(s)):
                if not s[i].isdigit():
                    return False
            return True
        elif s[1] == 'x':
            for i in range(2, len(s)):
                if not(s[i].isdigit() or (s[i] in ['A', 'B', 'C', 'D', 'E', 'F', 'a', 'b', 'c', 'd', 'e', 'f'])):
                    return False
            return True
    elif s.count('.') == 1:
        current = s.split('.')
        left = current[0]
        right = current[1]

        if not left.isdigit():
            return False
        if right.isdigit():
            return True

        if not('e' in right) or s.count('e') != 1:
            return False
        current = right.split('e')
        left = current[0]
        right = current[1]
        if left.isdigit() and right.isdigit():
            return True
    elif s.count('e') == 1:
        current = s.split('e')
        left = current[0]
        right = current[1]
        if left.isdigit() and right.isdigit():
            return True
    elif s.isdigit():
        return True

    return False


def analyzer(code: List[str]):
    """对给定的代码进行词法分析

    采用恐慌模式处理错误

    Args:
        code: 给定代码

    Returns:
        token序列，格式为'code <class, value>'
        若存在词法错误，则额外返回错误信息，格式为'Lexical error at Line [Line No]: [comment]'
    """
    token = []
    error = []
    for i in range(len(code)):
        if len(code[i]) == 0:
            continue

        j = 0
        while j < len(code[i]):
            if code[i][j] == '_' or code[i][j].isalpha():
                # 处理标识符和保留字
                rec = code[i][j]
                j += 1
                while j < len(code[i]):
                    if not(code[i][j] == '_' or code[i][j].isalpha() or code[i][j].isdigit()):
                        j -= 1
                        break
                    rec = rec + code[i][j]
                    j += 1

                kind = isreserved(rec)
                if kind == 'id':
                    token.append(rec + ' <' + kind +
                                 ', ' + rec + '> ' + str(i))
                else:
                    token.append(rec + ' <' + kind + ', ' + '_> ' + str(i))
            elif code[i][j].isdigit():
                # 处理常数值
                rec = code[i][j]
                j += 1
                while j < len(code[i]):
                    if not(code[i][j] == '.' or code[i][j] == 'e' or code[i][j] == 'x' or code[i][j] == 'X' or code[i][j].isdigit() or code[i][j].isalpha()):
                        j -= 1
                        break
                    rec = rec + code[i][j]
                    j += 1

                if isconst(rec):
                    token.append(rec + ' <const, ' + rec + '> ' + str(i))
                else:
                    error.append(
                        'Lexical error at Line [' + str(i + 1) + ']: illegal constant ' + rec)
                    while len(rec) != 0:
                        rec = rec[1:]
                        if isconst(rec):
                            token.append(rec + ' <const, ' +
                                         rec + '> ' + str(i))
                            break
            elif code[i][j] in ['+', '-', '*', '[', ']', ';', '.', '{', '}', '(', ')', ',']:
                token.append(code[i][j] + ' <' + code[i][j] + ', _> ' + str(i))
            elif code[i][j] == '"':
                j += 1
                rec = ""
                while j < len(code[i]) and code[i][j] != '"':
                    rec = rec + code[i][j]
                    j += 1
                token.append('" <", _> ' + str(i))
                token.append(rec + ' <const, ' + rec + '> ' + str(i))
                token.append('" <", _> ' + str(i))
            elif code[i][j] in ['=', '<', '>', '!']:
                if j < len(code[i]) - 1 and code[i][j+1] == '=':
                    token.append(code[i][j] + '= <' + code[i]
                                 [j] + '=, _> ' + str(i))
                    j += 1
                else:
                    if code[i][j] == '!':
                        token.append('! <not, _> ' + str(i))
                    else:
                        token.append(code[i][j] + ' <' +
                                     code[i][j] + ', _> ' + str(i))
            elif code[i][j] in ['&', '|']:
                if j < len(code[i]) - 1 and code[i][j+1] == code[i][j]:
                    if code[i][j] == '&':
                        token.append('&& <and, _> ' + str(i))
                    elif code[i][j] == '|':
                        token.append('|| <or, _> ' + str(i))
                else:
                    token.append(code[i][j] + ' <' + code[i]
                                 [j] + ', _> ' + str(i))
            elif code[i][j] == '/':
                if j < len(code[i]) - 1 and code[i][j+1] == '*':
                    token.append('/* </*, _> ' + str(i))
                    token.append('*/ <*/, _> ' + str(i))
                    break
                else:
                    token.append('/ </, _> ' + str(i))
            elif code[i][j] == ' ':
                j += 1
                continue
            else:
                error.append(
                    'Lexical error at Line [' + str(i + 1) + ']: illegal character ' + code[i][j])

            j += 1

    return token, error


if __name__ == '__main__':
    code: List[str] = []
    with open(args.load_path, 'r') as f:
        for line in f:
            code.append(line.strip())

    token, error = analyzer(code)
    print('lexical analyse finished')

    with open(args.dump_path, 'w') as f:
        for t in token:
            f.write(t + '\n')
    
    with open(args.log_path, 'w') as f:
        for e in error:
            f.write(e + '\n')
