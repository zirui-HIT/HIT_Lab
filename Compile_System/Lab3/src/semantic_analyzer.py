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

    def __str__(self):
        return '(%s, %s, %s, %s)' % (self.__op, self.__value1, self.__value2, self.__result)

    def operate(self):
        if self.__op == 'j<':
            return 'if %s<%s goto L%s' % (self.__value1, self.__value2, self.__result)
        if self.__op == 'j':
            return 'goto L%s' % (self.__result)
        if self.__op in ['+', '-', '*', '/']:
            return '%s = %s %s %s' % (self.__result, self.__value1, self.__op, self.__value2)
        if self.__op == '=':
            return '%s = %s' % (self.__result, self.__value1)
        if self.__op == 'call':
            return '%s = call %s' % (self.__result, self.__value1)


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

            stack[-1].append(current)
            stack.append(current)

    return root


def _enter(lexeme: str, t: str, symbols: Dict[str, str]):
    '''在符号表中登录符号
    '''
    symbols[lexeme] = t


def _array(const: str, t: str):
    '''生成数组
    '''
    return '%s[%s]' % (t, const)


TEMP_VARIABLE_CNT = 0


def _newtemp():
    '''生成新的临时变量
    '''
    global TEMP_VARIABLE_CNT
    TEMP_VARIABLE_CNT += 1
    return 't%d' % (TEMP_VARIABLE_CNT)


def _gen(op: str, value1: str, value2: str, result: str, tetrads: List[Tetrad]):
    '''生成四元组并保存
    '''
    tetrads.append(Tetrad(op, value1, value2, result))


def analyze(node: Node, symbols: Dict[str, str], tetrads: List[Tetrad]):
    '''根据语法树生成符号表和四元式序列

    Args:
        root: 语法树根
        symbols: 符号表
        tetrads: 四元式序列
    '''
    current_child = node.child()

    for c in current_child:
        analyze(c, symbols, tetrads)

    # 处理声明语句
    if node.word() == 'Defination':
        _enter(current_child[1].attribute(
            'lexeme'), current_child[0].attribute('type'), symbols)
    elif node.word() == 'Data':
        if current_child[0].word() == 'Type':
            node.update('type', current_child[0].attribute('type'))
        elif current_child[0].word() == 'Data':
            node.update('type', _array(current_child[2].attribute(
                'value'), current_child[0].attribute('type')))
    elif node.word() == 'Type':
        node.update('type', current_child[0].attribute('type'))

    # 处理赋值语句
    if node.word() == 'Assignment':
        _gen('=', current_child[3].attribute(
            'addr'), '-', current_child[0].attribute('lexeme') + current_child[1].attribute('index'), tetrads)
    elif node.word() == 'Value':
        if current_child[0].word() == 'Value':
            node.update('addr', _newtemp())
            _gen(current_child[1].attribute('op'), current_child[0].attribute(
                'addr'), current_child[2].attribute('addr'), node.attribute('addr'), tetrads)
        elif current_child[0].word() == '-':
            node.update('addr', _newtemp())
            _gen(
                '*', -1, current_child[1].attribute('addr'), node.attribute('addr'), tetrads)
        elif current_child[0].word() == '(':
            node.update('addr', current_child[1].attribute('addr'))
        elif current_child[0].word() == 'const':
            node.update('addr', _newtemp())
            _gen('=', current_child[0].attribute('value'),
                 '-', node.attribute('addr'), tetrads)
        elif current_child[0].word() == 'id':
            node.update('addr', current_child[0].attribute(
                'lexeme') + current_child[1].attribute('index'))
        elif current_child[0].word() == 'Call':
            node.update('addr', _newtemp())
            _gen('call', current_child[0].attribute(
                'lexeme'), '-', node.attribute('addr'), tetrads)
    elif node.word() == 'Index':
        if len(current_child) == 0:
            node.update('index', '')
        else:
            node.update('index', '[%s]%s' % (current_child[1].attribute(
                'value'), current_child[3].attribute('index')))

    # 处理过程调用语句
    if node.word() == 'Call':
        node.update('lexeme', current_child[0].attribute('lexeme'))


if __name__ == '__main__':
    root = build_tree('Compile_System/Lab2/data/result.txt')

    symbols = {}
    tetrads = []
    analyze(root, symbols, tetrads)

    with open('Compile_System/Lab3/data/symbols.txt', 'w') as f:
        for s in symbols:
            f.write('%s %s\n' % (s, symbols[s]))
    with open('Compile_System/Lab3/data/tetrads.txt', 'w') as f:
        for i in range(len(tetrads)):
            f.write('L%d: %s \t %s\n' %
                    (i, tetrads[i].__str__(), tetrads[i].operate()))
