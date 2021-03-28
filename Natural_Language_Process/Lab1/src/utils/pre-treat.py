from copy import deepcopy


def simplify_data(data_path: str, save_path: str):
    target = open(save_path, 'w')
    with open(data_path) as f:
        for line in f:
            words = line.split()
            for i in range(len(words)):
                target.write((words[i].split('/'))[0].strip('[').strip(']') +
                             ' ')
            target.write('\n')


def check_not_mark(word: str) -> bool:
    marks = ["。", "，", "《", "》", "“", "”", "、", "！",
             "？", "‘", "’", "（", "）", "［", "］", "；", "："]
    if word in marks:
        return False
    return True


def get_dictionary(data_path: str, dictionary_path: str):
    single_dictionary = []
    double_dictionary = []
    single_cnt = {}
    double_cnt = {}

    with open(data_path, encoding='utf-8') as f:
        for line in f:
            words = line.split()

            for i in range(len(words)):
                single_dictionary.append(
                    (words[i].split('/'))[0].strip('[').strip(']'))

                last = len(single_dictionary) - 1
                if i != 0:
                    pre_word = deepcopy(single_dictionary[last - 1])
                    current_word = deepcopy(single_dictionary[last])
                    if check_not_mark(pre_word) and check_not_mark(
                            current_word):
                        double_dictionary.append(pre_word + ' ' + current_word)

    for w in single_dictionary:
        single_cnt[w] = single_cnt.get(w, 0) + 1
    for w in double_dictionary:
        double_cnt[w] = double_cnt.get(w, 0) + 1

    single_dictionary = list(set(single_dictionary))
    single_dictionary = sorted(single_dictionary)
    double_dictionary = list(set(double_dictionary))
    double_dictionary = sorted(double_dictionary)

    with open(dictionary_path, 'w') as f:
        for w in single_dictionary:
            f.write('1' + ' ' + str(single_cnt[w]) + ' ' + w + '\n')
        for w in double_dictionary:
            f.write('2' + ' ' + str(double_cnt[w]) + ' ' + w + '\n')


if __name__ == '__main__':
    # simplify_data('../data/199801_seg&pos.txt', '../result/simplified.txt')

    get_dictionary('../data/199801_seg&pos.txt', '../result/dic.txt')
