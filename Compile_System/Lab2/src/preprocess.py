from typing import List
from typing import Dict


class Item(object):
    def __init__(self, nonterminal: str, grammar: List[str], character: str):
        self.__nonterminal = nonterminal
        self.__grammar = grammar
        self.__character = character

    def nonterminal(self):
        return self.__nonterminal

    def grammar(self):
        return self.__grammar

    def character(self):
        return self.__character

    def operate_position(self):
        for i in range(len(self.__grammar)):
            if self.__grammar[i] == '@':
                return i

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        if self.__nonterminal != other.nonterminal():
            return False
        if self.__character != other.character():
            return False

        grammar = other.grammar()
        if len(grammar) != len(self.__grammar):
            return False
        for i in range(len(grammar)):
            if grammar[i] != self.__grammar[i]:
                return False

        return True

    def __hash__(self):
        return hash('[' + self.__nonterminal + '->' + self.__grammar + ',' + self.__character + ']')


def load_grammar(path: str) -> Dict[str, List[List[str]]]:
    '''从指定路径中读取文法

    Args:
        path: 读取路径，以end为结尾，格式为T -> S1 | S2 ...，符号间以空格分隔

    Returns:
        文法集合
    '''
    grammar = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            current = line.strip().split('->')
            if current[0] == 'end':
                return grammar
            if len(current) <= 1:
                continue

            rule = current[1].split('|')
            rule = [s.split() for s in rule]
            for i in range(len(rule)):
                for j in range(len(rule[i])):
                    rule[i][j] = rule[i][j].strip()

            nonterminal = current[0].strip()
            if not(nonterminal in grammar):
                grammar[nonterminal] = []
            grammar[nonterminal] = grammar[nonterminal] + rule


def get_character(grammar: Dict[str, List[List[str]]]) -> List[str]:
    '''获得文法中的所有文法符号

    Args:
        grammar: 文法

    Returns:
        所有文法符号
    '''
    ret = ['$']
    for g in grammar:
        for x in grammar[g]:
            for t in x:
                if not(t in ret):
                    ret.append(t)
        if not(g in ret):
            ret.append(g)
    return ret


def get_sentence_first(first: List[str], s: List[str]) -> List[str]:
    '''计算一个字符串的first集合

    Args:
        first: 单字符的first集合
        s: 字符串

    Returns:
        字符串的first集合
    '''
    ret = []
    for x in s:
        ret = ret + first[x]
        if not('epsilon' in first[x]):
            break
    return list(set(ret))


def get_first(grammar: Dict[str, List[List[str]]]) -> Dict[str, List[str]]:
    '''计算一个文法的first集合

    Args:
        grammar: 文法

    Returns:
        first集合
    '''
    first = {}
    for g in grammar:
        first[g] = []
        for r in grammar[g]:
            for x in r:
                if x[0] == 'epsilon':
                    first[g].append('epsilon')
                if not x[0].isupper():
                    first[x] = [x]
    first['$'] = ['$']

    while True:
        flag = False
        for g in grammar:
            for r in grammar[g]:
                current = get_sentence_first(first, r)
                for c in current:
                    if not(c in first[g]):
                        first[g].append(c)
                        flag = True
        if not flag:
            return first


def get_follow(grammar: Dict[str, List[List[str]]], start: str) -> Dict[str, List[str]]:
    '''计算一个文法的follow集合

    Args:
        grammar: 文法
        start: 起始符号

    Returns:
        follow集合
    '''
    first = get_first(grammar)

    follow = {}
    for g in grammar:
        follow[g] = []
    follow[start].append('$')

    while True:
        flag = False
        for g in grammar:
            for r in grammar[g]:
                for i in range(len(r) - 1):
                    if r[i][0].isupper():
                        next_first = get_sentence_first(first, r[i+1:])
                        for c in next_first:
                            if c == 'epsilon':
                                continue
                            if not (c in follow[r[i]]):
                                flag = True
                                follow[r[i]].append(c)

                        if 'epsilon' in next_first:
                            for c in follow[g]:
                                if not (c in follow[r[i]]):
                                    flag = True
                                    follow[r[i]].append(c)

                last = r[-1]
                if last[0].isupper():
                    for c in follow[g]:
                        if not (c in follow[last]):
                            flag = True
                            follow[last].append(c)

        if not flag:
            return follow


def get_closure(items: List[Item], grammar: Dict[str, List[List[str]]], first: Dict[str, List[str]]) -> List[Item]:
    '''根据项目集和文法构造闭包

    Args:
        items: 项目集
        grammar: 文法
        first: first集合

    Returns:
        相应闭包
    '''
    from copy import deepcopy
    closure = deepcopy(items)
    while True:
        flag = False

        for item in closure:
            current_grammar = item.grammar()
            current_character = item.character()

            p = item.operate_position()
            if p < len(current_grammar) - 1 and current_grammar[p+1][0].isupper():
                for g in grammar[current_grammar[p+1]]:
                    current_sentence = [current_character]
                    if p != len(current_grammar) - 2:
                        current_sentence = current_grammar[p +
                                                           2:] + current_sentence

                    current_first = get_sentence_first(
                        first, current_sentence + [current_character])
                    for b in current_first:
                        if b == 'epsilon':
                            continue

                        if 'epsilon' in g:
                            current_item = Item(current_grammar[p+1], ['@'], b)
                        else:
                            current_item = Item(
                                current_grammar[p+1], ['@']+g, b)

                        if not (current_item in closure):
                            flag = True
                            closure.append(current_item)
        if not flag:
            break

    return closure


def get_goto(items: List[Item], grammar: Dict[str, List[List[str]]], char: str, first: Dict[str, List[str]]) -> List[Item]:
    '''计算一个项目集的GOTO集合

    Args:
        items: 项目集
        grammar: 文法
        char: 文法符号
        first: first集合

    Returns:
        GOTO集合
    '''
    goto = []
    for item in items:
        current_nonterminal = item.nonterminal()
        current_grammar = item.grammar()
        current_character = item.character()

        p = item.operate_position()
        if p != len(current_grammar) - 1 and current_grammar[p+1] == char:
            if p != 0:
                next_grammar = current_grammar[:p] + \
                    [current_grammar[p+1], '@']
            else:
                next_grammar = [current_grammar[p+1], '@']
            if p != len(current_grammar) - 2:
                next_grammar = next_grammar + current_grammar[p+2:]

            current_item = Item(current_nonterminal,
                                next_grammar, current_character)
            if not(current_item in goto):
                goto.append(current_item)

    return get_closure(goto, grammar, first)


def check_equal(a: List[Item], b: List[Item]) -> bool:
    '''检查两个集合是否相同
    '''
    if len(a) != len(b):
        return False

    for x in a:
        if not(x in b):
            return False
    return True


def check_not_include(A: List[List[Item]], a: List[Item]) -> bool:
    '''检查A中是否包含集合a
    '''
    for x in A:
        if check_equal(x, a):
            return True
    return False


def get_items(grammar: Dict[str, List[List[str]]], start: str):
    '''计算一个文法的LR(1)项集族

    以@表示处理位置，$表示句子结尾，以Start表示开始

    Args:
        grammar: 文法
        Start: 开始符号

    Returns:
        项集族
    '''
    first = get_first(grammar)
    characters = get_character(grammar)
    ret = [get_closure([Item('Start', ['@', start], '$')], grammar, first)]

    while True:
        flag = False
        for items in ret:
            for c in characters:
                current_goto = get_goto(items, grammar, c, first)
                if len(current_goto) == 0:
                    continue

                if not check_not_include(ret, current_goto):
                    flag = True
                    ret.append(current_goto)
        if not flag:
            return ret


def get_action_and_goto(items: List[List[Item]], grammar: Dict[str, List[List[str]]], start: str):
    '''计算项集族对应的ACTION和GOTO表

    Args:
        items: 项集族
        grammar: 文法
        start: 开始符号

    Returns:
        ACTION表
        GOTO表
    '''
    action = {}
    goto = {}
    first = get_first(grammar)
    characters = get_character(grammar)

    for i in range(len(items)):
        action[i] = {}
        goto[i] = {}
        for c in characters:
            if c[0].isupper():
                goto[i][c] = 'error'
            else:
                action[i][c] = 'error'

    from tqdm import tqdm
    for i in tqdm(range(len(items))):
        for item in items[i]:
            current_nonterminal = item.nonterminal()
            current_character = item.character()
            current_grammar = item.grammar()
            p = item.operate_position()

            if current_nonterminal == 'Start' and len(current_grammar) == 2 \
                    and current_grammar[0] == start and current_character == '$':
                action[i]['$'] = 'acc'
                continue

            if p == len(current_grammar) - 1:
                if current_nonterminal != 'Start':
                    action[i][current_character] = current_nonterminal + '-' + \
                        str(len(current_grammar[:-1]))
            else:
                current_goto = get_goto(
                    items[i], grammar, current_grammar[p+1], first)

                pos = -1
                for j in range(len(items)):
                    if check_equal(items[j], current_goto):
                        pos = j
                        break

                if current_grammar[p+1][0].isupper():
                    goto[i][current_grammar[p+1]] = str(pos)
                else:
                    action[i][current_grammar[p+1]] = 's' + str(pos)

    return action, goto


def dump(table: Dict[int, Dict[str, str]], path: str):
    '''保存数据表
    '''
    with open(path, 'w') as f:
        for i in table:
            for c in table[i]:
                f.write(str(i) + ' ' + c + ' ' + table[i][c] + '\n')


if __name__ == '__main__':
    print('loading grammar')
    grammar = load_grammar('Compile_System/Lab2/data/CFG.txt')

    print('getting items')
    items = get_items(grammar, 'Module')

    # TODO 仅用于验证
    '''
    items[2], items[3], items[1] = items[1], items[2], items[3]
    items[8], items[7] = items[7], items[8]
    items[10], items[9] = items[9], items[10]
    '''

    print('getting action and goto table')
    action, goto = get_action_and_goto(items, grammar, 'Module')

    print('dumping result')
    dump(action, 'Compile_System/Lab2/data/table/action.txt')
    dump(goto, 'Compile_System/Lab2/data/table/goto.txt')
