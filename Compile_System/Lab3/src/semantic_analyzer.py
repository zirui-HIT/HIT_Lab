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
        return self.__attribute[attr]

    def child(self):
        return self.__child


class Tetrad(object):
    def __init__(self, op, value1, value2, result):
        self.__op = op
        self.__value1 = value1
        self.__value2 = value2
        self.__result = result

    def update_result(self, result: str):
        self.__result = result

    def __str__(self):
        if self.__op is None:
            return ''
        return '(%s, %s, %s, %s)' % (self.__op, self.__value1, self.__value2,
                                     self.__result)

    def operate(self):
        if self.__op is None:
            return ''

        if self.__op[0] == 'j':
            if len(self.__op) > 1:
                return 'if %s%s%s goto L%s' % (self.__value1, self.__op[1:],
                                               self.__value2, self.__result)
            else:
                return 'goto L%s' % (self.__result)

        if self.__op in ['+', '-', '*', '/']:
            return '%s = %s %s %s' % (self.__result, self.__value1, self.__op,
                                      self.__value2)
        if self.__op == '=':
            return '%s = %s' % (self.__result, self.__value1)

        if self.__op == 'call':
            return 'call %s' % (self.__result)
        if self.__op == 'param':
            return 'param %s' % (self.__result)


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
            if words[0] in ['int', 'float', 'bool']:
                current.update('type', words[0])
            if words[0] in ['+', '-', '*', '/']:
                current.update('op', words[0])

            while depth != stack[-1].depth() + 1:
                stack.pop()

            if stack[-1].word() == 'Relop':
                current.update('sign', words[0])

            stack[-1].append(current)
            stack.append(current)

    return root


def _enter(lexeme: str, t: str, symbols: Dict[str, Dict]):
    '''在符号表中登录符号
    '''
    t = t.split()
    if t[0].endswith('*'):
        base = 64
    else:
        base = SYMBOL[t[0]]
    size = 1
    for i in range(1, len(t)):
        size *= int(t[i])

    global CURRENT_OFFSET
    symbols[lexeme] = {
        'type': t[0],
        'type_size': base,
        'offset': CURRENT_OFFSET,
        'size': [int(t[i]) for i in range(1, len(t))]
    }
    CURRENT_OFFSET += size * base


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


def analyze(node: Node, symbols: Dict[str, str], tetrads: List[Tetrad]):
    '''根据语法树生成符号表和四元式序列

    Args:
        root: 语法树根
        symbols: 符号表
        tetrads: 四元式序列
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
            analyze(current_child[0], symbols, tetrads)
            for x in current_child[0].attribute('next_list'):
                tetrads[x].update_result(len(tetrads))

            analyze(current_child[1], symbols, tetrads)
            node.update('next_list', current_child[1].attribute('next_list'))

            return
    elif node.word() == 'If':
        analyze(current_child[2], symbols, tetrads)
        for i in current_child[2].attribute('true_list'):
            tetrads[i].update_result(len(tetrads))

        node.update(
            'next_list', current_child[2].attribute('false_list') +
            current_child[5].attribute('next_list'))

        return
    elif node.word() == 'IfElse':
        analyze(current_child[2], symbols, tetrads)
        for i in current_child[2].attribute('true_list'):
            tetrads[i].update_result(len(tetrads))

        analyze(current_child[5], symbols, tetrads)
        temp_next_list = [len(tetrads)]
        _gen('j', '-', '-', '_', tetrads)

        for i in current_child[2].attribute('false_list'):
            tetrads[i].update_result(len(tetrads))

        analyze(current_child[9], symbols, tetrads)
        node.update(
            'next_list',
            temp_next_list + current_child[5].attribute('next_list') +
            current_child[9].attribute('next_list'))

        return
    elif node.word() == 'While':
        temp_quad = len(tetrads)

        analyze(current_child[2], symbols, tetrads)
        for i in current_child[2].attribute('true_list'):
            tetrads[i].update_result(len(tetrads))
        node.update('next_list', current_child[2].attribute('false_list'))

        analyze(current_child[5], symbols, tetrads)
        for i in current_child[5].attribute('next_list'):
            tetrads[i].update_result(temp_quad)

        _gen('j', '-', '-', temp_quad, tetrads)
        return

    # 递归调用
    for c in current_child:
        analyze(c, symbols, tetrads)

    # 处理声明语句
    if node.word() == 'Defination':
        _enter(current_child[1].attribute('lexeme'),
               current_child[0].attribute('type'), symbols)
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

    # 处理赋值语句
    if node.word() == 'Assignment':
        _gen(
            '=', current_child[3].attribute('addr'), '-',
            _offset(current_child[0].attribute('lexeme'),
                    current_child[1].attribute('index')), tetrads)
    elif node.word() == 'Value':
        if current_child[0].word() == 'Value':
            node.update('addr', _newtemp())
            _gen(current_child[1].attribute('op'),
                 current_child[0].attribute('addr'),
                 current_child[2].attribute('addr'), node.attribute('addr'),
                 tetrads)
        elif current_child[0].word() == '-':
            node.update('addr', _newtemp())
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
            # TODO type of function
            node.update('addr', _newtemp())
            _gen('=', 'ret', '-', node.attribute('addr'), tetrads)
    elif node.word() == 'Index':
        if len(current_child) == 0:
            node.update('index', '')
        else:
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
        cnt = 0
        for t in PARAMETER_QUEUE:
            _gen('param', '-', '-', t, tetrads)
            cnt += 1
        _gen('call', '-', '-',
             '%s,%s' % (current_child[0].attribute('lexeme'), cnt), tetrads)
        node.update('addr', current_child[0].attribute('lexeme'))
    elif node.word() == 'Transmit':
        if len(current_child) == 0:
            PARAMETER_QUEUE = []
        elif current_child[-1].word() == 'Transmit':
            PARAMETER_QUEUE.append(current_child[0].attribute('addr'))
        elif current_child[0].word() == 'Value':
            PARAMETER_QUEUE = [current_child[0].attribute('addr')]


if __name__ == '__main__':
    SYMBOL = {'int': 32, 'float': 32, 'bool': 1}
    CURRENT_OFFSET = 0
    PARAMETER_QUEUE = []
    TEMP_VARIABLE_CNT = 0

    root = build_tree('Compile_System/Lab2/data/result.txt')

    symbols = {}
    tetrads = []
    analyze(root, symbols, tetrads)

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
