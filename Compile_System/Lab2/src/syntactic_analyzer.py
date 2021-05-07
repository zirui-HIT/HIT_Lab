from typing import Dict, List


class Word(object):
    def __init__(self, word: str, kind: str, line: int):
        self.__word = word
        self.__kind = kind
        self.__line = line

    def word(self):
        return self.__word

    def kind(self):
        return self.__kind

    def line(self):
        return self.__line

    def __eq__(self, other):
        if not isinstance(other, Word):
            return False

        if self.__kind != other.kind():
            return False

        if self.__word != other.word():
            return False

        return True

    def __hash__(self):
        return hash(self.__word + self.__kind)


def load_table(path: str) -> Dict[int, Dict[str, str]]:
    ret = {}
    with open(path, 'r') as f:
        for line in f:
            current = line.split()
            state = int(current[0])

            if not state in ret:
                ret[state] = {}
            ret[state][current[1]] = current[2]
    return ret


def load_words(path: str) -> List[Word]:
    '''加载词法分析结果

    Args:
        path: 加载路径

    Returns:
        格式为[{'class': ..., 'value': ...}, ...]
    '''
    ret = []
    with open(path, 'r') as f:
        for line in f:
            if len(line.strip()) == 0:
                continue
            if line.strip() == 'lexical analyse finished':
                break

            current = line.split()[1:]
            current[0] = current[0][1:-1]
            current[1] = current[1][:-1]

            ret.append(Word(current[1], current[0], int(current[2])))
    ret.append(Word('_', '$', -1))
    return ret


def analyse(words: List[Word], action: Dict[int, Dict[str, str]],
            goto: Dict[int, Dict[str, str]]):
    '''根据action和goto表构造语法分析树

    采用恐慌模式处理语法错误

    Args:
        words: 词法分析结果，格式为value (class, value)
        action: action表
        goto: goto表

    Returns:
        语法分析树，格式为[{'word': ..., 'child': [id1, id2, ...], 'id': ...}]
        其中id为节点在返回列表中的角标
    '''
    stack = [{'state': 0, 'id': -1}]
    ret = []
    roots = []
    error = []
    i = 0
    while i < len(words):
        current_action = action[stack[-1]['state']][words[i].kind()]

        if current_action.startswith('s'):
            next_state = int(current_action[1:])
            stack.append({'state': next_state, 'id': len(ret)})
            roots.append(len(ret))
            ret.append({'word': words[i], 'child': [], 'id': len(ret)})
            i += 1
        elif current_action[0].isupper():
            current_action = current_action.split('-')
            current_grammar_length = int(current_action[1])

            current_node = {
                'word':
                Word('_', current_action[0],
                     ret[stack[-current_grammar_length]['id']]['word'].line()),
                'child': [],
                'id':
                len(ret)
            }
            roots.append(len(ret))

            for j in range(current_grammar_length):
                current_node['child'].append(stack[-1]['id'])
                roots.remove(stack[-1]['id'])
                stack.pop()
            current_node['child'].reverse()

            next_state = int(goto[stack[-1]['state']][current_action[0]])
            stack.append({'state': next_state, 'id': len(ret)})

            ret.append(current_node)
        elif current_action == 'acc':
            print('analyse finished')
            return ret, roots, error
        else:
            error.append('Syntax error at Line [%d]: illegal %s' %
                         (words[i].line(), words[i].kind()))

            i += 1
            continue

    raise Exception('syntactic analyze error')


def DFS(tree: List[Dict], current: int, depth: int, f):
    '''遍历输出语法树
    '''
    sentence = '\t' * depth + tree[current]['word'].kind()
    if tree[current]['word'].word() != '_':
        sentence = sentence + ' : ' + tree[current]['word'].word()
    sentence = sentence + ' (' + str(tree[current]['word'].line()) + ')'
    f.write(sentence + '\n')

    for c in tree[current]['child']:
        DFS(tree, c, depth + 1, f)


if __name__ == '__main__':
    action = load_table('Compile_System/Lab2/data/table/action.txt')
    goto = load_table('Compile_System/Lab2/data/table/goto.txt')
    words = load_words('Compile_System/Lab1/data/result.txt')

    tree, root, error = analyse(words, action, goto)

    with open('Compile_System/Lab2/data/result.txt', 'w') as f:
        for r in root:
            DFS(tree, r, 0, f)
    with open('Compile_System/Lab2/data/error.log', 'w') as f:
        for e in error:
            f.write(e + '\n')
