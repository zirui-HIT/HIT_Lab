from sys import exit
from typing import Dict, List


class Node(object):
    def __init__(self, word: str, depth: int):
        self.__word = word
        self.__depth = depth
        self.__attribute = {}
        self.__child = []

    def word(self):
        return self.__word

    def depth(self):
        return self.__depth

    def append(self, node):
        self.__child.append(node)

    def update(self, attr: str, value):
        self.__attribute[attr] = value

    def attribute(self, attr: str):
        if attr != 'line' and not (attr in self.__attribute):
            print('Semantic error at Line [%d]: missed attribute' %
                  (self.__attribute['line']))
            exit(-1)
        return self.__attribute[attr]

    def child(self):
        return self.__child


class Tetrad(object):
    def __init__(self, op, value1, value2, result):
        self._op = op
        self._value1 = value1
        self._value2 = value2
        self._result = result

    def update_result(self, result: str):
        self._result = result

    def __str__(self):
        if self._op is None:
            return ''
        return '(%s, %s, %s, %s)' % (self._op, self._value1, self._value2,
                                     self._result)

    def operate(self):
        if self._op is None:
            return ''

        if self._op[0] == 'j':
            if isinstance(self._result, int):
                target = 'L' + str(self._result)
            else:
                target = self._result

            if len(self._op) > 1:
                return 'if %s%s%s goto %s' % (self._value1, self._op[1:],
                                              self._value2, target)
            else:
                return 'goto %s' % (target)

        if self._op in ['+', '-', '*', '/']:
            return '%s = %s %s %s' % (self._result, self._value1, self._op,
                                      self._value2)
        if self._op == '=':
            return '%s = %s' % (self._result, self._value1)

        if self._op == 'call':
            return 'call %s' % (self._result)
        if self._op == 'param':
            return 'param %s' % (self._result)
        if self._op == 'pop':
            return 'pop %s' % (self._result)
        if self._op == 'push':
            return 'push %s' % (self._value1)
        if self._op == 'return':
            return self._op


def build_tree(path: str) -> Node:
    '''从路径中读取语法树

    Args:
        path: 语法树路径

    Returns:
        语法树的根
    '''
    root = Node('Start', -1)
    stack = [root]

    with open(path, 'r') as f:
        for line in f:
            depth = line.count('\t')
            words = line.strip().split()
            current = Node(words[0], depth)

            if words[0] == 'id':
                current.update('lexeme', words[-2])
            if words[0] == 'const':
                current.update('value', words[-2])
                current.update('type', _type(words[-2]))
            if words[0] in ['int', 'float', 'bool']:
                current.update('type', words[0])
            if words[0] in ['+', '-', '*', '/']:
                current.update('op', words[0])
            current.update('line', int(words[-1][1:-1]))

            while depth != stack[-1].depth() + 1:
                stack.pop()

            if stack[-1].word() == 'Relop':
                current.update('sign', words[0])

            stack[-1].append(current)
            stack.append(current)

    return root


def _enter(lexeme: str, t: str, symbols: Dict[str, Dict]) -> str:
    '''在符号表中登录符号

    Args:
        lexeme: 符号名
        t: 类型
        symbols: 符号表

    Returns:
        如果无语义错误，返回'OK'
        否则，返回相应语义错误
    '''
    if lexeme in symbols:
        return '%s is defined' % (lexeme)

    base, size = _size(t, True)
    t = t.split()

    global CURRENT_OFFSET
    symbols[lexeme] = {
        'type': t[0],
        'type_size': base,
        'offset': CURRENT_OFFSET,
        'size': [int(t[i]) for i in range(1, len(t))]
    }
    CURRENT_OFFSET += size

    return 'OK'


def _size(t: str, ret_base: bool = False) -> int:
    '''计算数据类型对应的字节长度

    Args:
        t: 数据类型，格式为t num1 num2 ...
        ret_base: 是否返回基础类型字节长

    Returns:
        对应字节长度
    '''
    global STRUCTS
    t = t.split()
    if t[0].endswith('*'):
        base = 64
    elif t[0] in STRUCTS:
        base = STRUCTS[t[0]]['size']
    else:
        base = SYMBOL[t[0]]
    size = 1
    for i in range(1, len(t)):
        size *= int(t[i])

    if ret_base:
        return base, base * size
    return base * size


def _offset(lexeme: str, index: str) -> int:
    '''计算数组对应的偏置

    Args:
        lexeme: 变量名
        index: 角标，格式为"idx1 idx2 ... idxn"

    Returns:
        若无语义错误，则返回偏置
        否则，返回-1
    '''
    index = index.split()
    index = [int(x) for x in index]

    lexeme = symbols[lexeme]
    if len(lexeme['size']) != len(index):
        return -1
    if len(index) == 0:
        return lexeme['offset']

    offset = 0
    cum = 1
    for i in range(len(index) - 1, -1, -1):
        offset += index[i] * cum
        cum *= lexeme['size'][i]

    return lexeme['offset'] + offset * lexeme['type_size']


def _array(const: str, t: str):
    '''生成数组
    '''
    return '%s %s' % (t, const)


def _newtemp() -> str:
    '''生成新的临时变量

    Args:
        type: 临时变量类型

    Returns:
        变量名
    '''
    global TEMP_VARIABLE_CNT
    TEMP_VARIABLE_CNT += 1
    name = 't%d' % (TEMP_VARIABLE_CNT)
    return name


def _gen(op: str, value1: str, value2: str, result: str,
         tetrads: List[Tetrad]):
    '''生成四元组并保存
    '''
    tetrads.append(Tetrad(op, value1, value2, result))


def _type(num: str) -> str:
    '''返回num对应的数值类型

    Args:
        num: 待检查数值

    Returns:
        int, float
    '''
    if num.isdigit():
        return 'int'
    return 'float'


def analyze(node: Node,
            symbols: Dict[str, Dict],
            tetrads: List[Tetrad],
            functions: Dict[str, Dict],
            update: bool = True):
    '''根据语法树生成符号表和四元式序列

    Args:
        root: 语法树根
        symbols: 符号表
        tetrads: 四元式序列
        functions: 过程表
        update: 是否更新符号表
    '''
    current_child = node.child()

    # 处理布尔表达式语句
    if node.word() == 'Condition':
        if current_child[1].word() == 'and':
            analyze(current_child[0], symbols, tetrads)
            for i in current_child[0].attribute('true_list'):
                tetrads[i].update_result(len(tetrads))

            analyze(current_child[2], symbols, tetrads)
            node.update('true_list', current_child[2].attribute('true_list'))
            node.update(
                'false_list', current_child[0].attribute('false_list') +
                current_child[2].attribute('false_list'))

            return
        elif current_child[1].word() == 'or':
            analyze(current_child[0], symbols, tetrads)
            for i in current_child[0].attribute('false_list'):
                tetrads[i].update_result(len(tetrads))

            analyze(current_child[2], symbols, tetrads)
            node.update(
                'true_list', current_child[0].attribute('true_list') +
                current_child[2].attribute('true_list'))
            node.update('false_list', current_child[2].attribute('false_list'))

            return

    # 处理控制流语句
    if node.word() == 'Module':
        if len(current_child) == 0:
            node.update('next_list', [])
        elif current_child[0].word() == 'Control':
            analyze(current_child[0], symbols, tetrads, functions)
            for x in current_child[0].attribute('next_list'):
                tetrads[x].update_result(len(tetrads))

            analyze(current_child[1], symbols, tetrads, functions)
            node.update('next_list', current_child[1].attribute('next_list'))

            return
    elif node.word() == 'If':
        analyze(current_child[2], symbols, tetrads, functions)
        for i in current_child[2].attribute('true_list'):
            tetrads[i].update_result(len(tetrads))

        node.update(
            'next_list', current_child[2].attribute('false_list') +
            current_child[5].attribute('next_list'))

        return
    elif node.word() == 'IfElse':
        analyze(current_child[2], symbols, tetrads, functions)
        for i in current_child[2].attribute('true_list'):
            tetrads[i].update_result(len(tetrads))

        analyze(current_child[5], symbols, tetrads, functions)
        temp_next_list = [len(tetrads)]
        _gen('j', '-', '-', '_', tetrads)

        for i in current_child[2].attribute('false_list'):
            tetrads[i].update_result(len(tetrads))

        analyze(current_child[9], symbols, tetrads, functions)
        node.update(
            'next_list',
            temp_next_list + current_child[5].attribute('next_list') +
            current_child[9].attribute('next_list'))

        return
    elif node.word() == 'While':
        temp_quad = len(tetrads)

        analyze(current_child[2], symbols, tetrads, functions)
        for i in current_child[2].attribute('true_list'):
            tetrads[i].update_result(len(tetrads))
        node.update('next_list', current_child[2].attribute('false_list'))

        analyze(current_child[5], symbols, tetrads, functions)
        for i in current_child[5].attribute('next_list'):
            tetrads[i].update_result(temp_quad)

        _gen('j', '-', '-', temp_quad, tetrads)
        return

    # 处理过程声明语句
    if node.word() == 'Function':
        lexeme = current_child[1].attribute('lexeme')
        start_line = 'L%d' % (len(tetrads))

        for c in current_child:
            analyze(c, symbols, tetrads, functions)

        functions[lexeme] = {
            'type': current_child[0].attribute('type'),
            'parameter': current_child[3].attribute('parameter'),
            'start_line': start_line
        }
        t = _newtemp()
        _gen('pop', '-', '-', t, tetrads)
        _gen('j', '-', '-', t, tetrads)

        if current_child[0].attribute('type') != current_child[6].attribute(
                'type'):
            print("Semantic error at Line [%d]: %s" %
                  (current_child[2].attribute('line'), 'type mismatch'))

        return
    elif node.word() == 'Parameter':
        for c in current_child:
            analyze(c, symbols, tetrads, functions)
        if len(current_child) == 0:
            node.update('parameter', [])
        elif len(current_child) == 1:
            lexeme = current_child[0].attribute('lexeme')
            node.update('parameter', [lexeme])
        else:
            lexeme = current_child[0].attribute('lexeme')
            node.update('parameter',
                        [lexeme] + current_child[2].attribute('parameter'))
        return
    elif node.word() == 'Process':
        for c in current_child:
            analyze(c, symbols, tetrads, functions)

        node.update('type', current_child[1].attribute('type'))
        return
    elif node.word() == 'Return':
        for c in current_child:
            analyze(c, symbols, tetrads, functions)

        node.update('type', current_child[1].attribute('type'))
        if len(current_child) > 1:
            _gen('=', current_child[1].attribute('addr'), '-', 'ret', tetrads)
        return

    # 递归调用
    if node.word() == 'Struct':
        for c in current_child:
            analyze(c, symbols, tetrads, functions, False)
    else:
        for c in current_child:
            analyze(c, symbols, tetrads, functions)

    # 处理声明语句
    if node.word() == 'Defination':
        if update:
            error = _enter(current_child[1].attribute('lexeme'),
                           current_child[0].attribute('type'), symbols)

            if error != 'OK':
                print('Semantic error at Line [%d]: %s' %
                      (current_child[0].attribute('line'), error))
                exit(-1)

        node.update('lexeme', current_child[1].attribute('lexeme'))
        node.update('type', current_child[0].attribute('type'))
    elif node.word() == 'Data':
        if current_child[0].word() == 'Type':
            node.update(
                'type', current_child[0].attribute('type') +
                current_child[1].attribute('point') * '*')
        elif current_child[0].word() == 'Data':
            node.update(
                'type',
                _array(current_child[2].attribute('value'),
                       current_child[0].attribute('type')))
    elif node.word() == 'Type':
        node.update('type', current_child[0].attribute('type'))
    elif node.word() == 'Point':
        if len(current_child) == 0:
            node.update('point', 0)
        else:
            node.update('point', current_child[1].attribute('point') + 1)

    # 处理结构声明语句
    if node.word() == 'Struct':
        size = 0
        current = current_child[3]

        for s in current.attribute('type'):
            size += _size(s)

        struct = {
            'size': size,
            'var': current.attribute('var'),
            'type': current.attribute('type')
        }

        global STRUCTS
        STRUCTS[current_child[1].attribute('lexeme')] = struct
    elif node.word() == 'Statement':
        if len(current_child) == 2:
            node.update('var', [current_child[0].attribute('lexeme')])
            node.update('type', [current_child[0].attribute('type')])
        else:
            node.update('var', [current_child[0].attribute('lexeme')] +
                        current_child[2].attribute('var'))
            node.update('type', [current_child[0].attribute('type')] +
                        current_child[2].attribute('type'))

    # 处理赋值语句
    if node.word() == 'Assignment':
        if symbols[current_child[0].attribute(
                'lexeme')]['type'] != current_child[3].attribute('type'):
            print("Semantic error at Line [%d]: %s" %
                  (current_child[2].attribute('line'), 'not same type'))
            exit(-1)

        if len(symbols[current_child[0].attribute('lexeme')]['size']) != len(
                current_child[1].attribute('index').split()):
            print("Semantic error at Line [%d]: %s" %
                  (current_child[2].attribute('line'), 'not match array dim'))
            exit(-1)

        _gen(
            '=', current_child[3].attribute('addr'), '-',
            _offset(current_child[0].attribute('lexeme'),
                    current_child[1].attribute('index')), tetrads)
    elif node.word() == 'Value':
        if current_child[0].word() == 'Value':
            if current_child[0].attribute(
                    'type') != current_child[2].attribute('type'):
                print("Semantic error at Line [%d]: %s" %
                      (current_child[1].attribute('line'), 'not same type'))
                exit(-1)

            node.update('addr', _newtemp())
            node.update('type', current_child[0].attribute('type'))
            _gen(current_child[1].attribute('op'),
                 current_child[0].attribute('addr'),
                 current_child[2].attribute('addr'), node.attribute('addr'),
                 tetrads)
        elif current_child[0].word() == '-':
            node.update('addr', _newtemp())
            node.update('type', current_child[1].attribute('type'))
            _gen('*', -1, current_child[1].attribute('addr'),
                 node.attribute('addr'), tetrads)
        elif current_child[0].word() == '(':
            node.update('addr', current_child[1].attribute('addr'))
        elif current_child[0].word() == 'const':
            node.update('type', _type(current_child[0].attribute('value')))
            node.update('value', current_child[0].attribute('value'))
            node.update('addr', _newtemp())
            _gen('=', '$' + current_child[0].attribute('value'), '-',
                 node.attribute('addr'), tetrads)
        elif current_child[0].word() == 'id':
            node.update(
                'addr',
                _offset(current_child[0].attribute('lexeme'),
                        current_child[1].attribute('index')))
            node.update('type',
                        symbols[current_child[0].attribute('lexeme')]['type'])
        elif current_child[0].word() == 'Call':
            node.update('addr', _newtemp())
            node.update('type', current_child[0].attribute('type'))
            _gen('=', 'ret', '-', node.attribute('addr'), tetrads)
    elif node.word() == 'Index':
        if len(current_child) == 0:
            node.update('index', '')
        else:
            if not (current_child[1].attribute('value').isdigit()):
                print("Semantic error at Line [%d]: %s" %
                      (current_child[1].attribute('line'), 'must int index'))
                exit(-1)

            node.update(
                'index', '%s %s' % (current_child[1].attribute('value'),
                                    current_child[3].attribute('index')))

    # 处理控制流语句
    if node.word() == 'Module':
        if len(current_child) == 0:
            node.update('next_list', [])
        elif current_child[0] != 'Control':
            node.update('next_list', [])
    elif node.word() == 'Control':
        node.update('next_list', current_child[0].attribute('next_list'))

    # 处理布尔表达式语句
    if node.word() == 'Condition':
        if current_child[1].word() == 'Relop':
            node.update('true_list', [len(tetrads)])
            node.update('false_list', [len(tetrads) + 1])
            _gen('j%s' % (current_child[1].attribute('sign')),
                 current_child[0].attribute('addr'),
                 current_child[2].attribute('addr'), '_', tetrads)
            _gen('j', '-', '-', '_', tetrads)
        elif current_child[0].word() == 'true':
            node.update('true_list', [len(tetrads)])
            _gen('j', '-', '-', '_', tetrads)
        elif current_child[0].word() == 'false':
            node.update('false_list', [len(tetrads)])
            _gen('j', '-', '-', '_', tetrads)
        elif current_child[0].word() == '(':
            node.update('true_list', current_child[1].attribute('true_list'))
            node.update('false_list', current_child[1].attribute('false_list'))
        elif current_child[0].word() == 'not':
            node.update('true_list', current_child[1].attribute('false_list'))
            node.update('false_list', current_child[1].attribute('true_list'))
    elif node.word() == 'Relop':
        node.update('sign', current_child[0].attribute('sign'))

    # 处理过程调用语句
    global PARAMETER_QUEUE
    if node.word() == 'Call':
        if not (current_child[0].attribute('lexeme') in functions):
            print("Semantic error at Line [%d]: %s" %
                  (current_child[0].attribute('line'),
                   'function is not defined'))

        f = functions[current_child[0].attribute('lexeme')]
        if len(f['parameter']) != len(PARAMETER_QUEUE):
            print("Semantic error at Line [%d]: %s" %
                  (current_child[0].attribute('line'),
                   'function parameter mismatch'))
            exit(-1)

        node.update('addr', current_child[0].attribute('lexeme'))
        node.update('type', f['type'])

        for i in range(len(f['parameter'])):
            p_type = symbols[f['parameter'][i]]['type']
            t_type = PARAMETER_QUEUE[i].attribute('type')
            if p_type != t_type:
                print("Semantic error at Line [%d]: %s" %
                      (current_child[0].attribute('line'),
                       'function parameter mismatch'))
                exit(-1)

            _gen('=', PARAMETER_QUEUE[i].attribute('addr'), '-',
                 f['parameter'][i], tetrads)
        _gen('push', 'L%d' % (len(tetrads) + 2), '-', '-', tetrads)
        _gen('j', '-', '-', f['start_line'], tetrads)
    elif node.word() == 'Transmit':
        if len(current_child) == 0:
            PARAMETER_QUEUE = []
        elif current_child[-1].word() == 'Transmit':
            PARAMETER_QUEUE.append(current_child[0])
        elif current_child[0].word() == 'Value':
            PARAMETER_QUEUE = [current_child[0]]


if __name__ == '__main__':
    SYMBOL = {'int': 32, 'float': 32, 'bool': 1}
    CURRENT_OFFSET = 0
    PARAMETER_QUEUE = []
    TEMP_VARIABLE_CNT = 0
    STRUCTS = {}

    root = build_tree('Compile_System/Lab2/data/result.txt')

    symbols = {}
    tetrads = []
    functions = {}
    structs = {}
    analyze(root, symbols, tetrads, functions, structs)

    with open('Compile_System/Lab3/data/symbols.txt', 'w') as f:
        for s in symbols:
            current = 0
            f.write('%s %s %d\n' %
                    (s, symbols[s]['type'], symbols[s]['offset']))
    with open('Compile_System/Lab3/data/tetrads.txt', 'w') as f:
        for i in range(len(tetrads)):
            f.write('L%d: %s \t %s\n' %
                    (i, tetrads[i].__str__(), tetrads[i].operate()))
        f.write('L%d:\n' % (len(tetrads)))
