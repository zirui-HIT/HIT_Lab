from utils.page import Page
from typing import List


class Base(object):
    def __init__(self, pages: List[Page]):
        self.__pages = pages

    @staticmethod
    def load_url(url: str,
                 file_path: str,
                 count: int,
                 ends: List[str] = ('htm')):
        """
        以url为根路径进行BFS，提取count个网页的信息
        经过观察，实验选定的网页的子网页均以.htm作为结尾

        :param url: 检索根路径
        :param file_path: 网页附件保存地址
        :param count: 检索网页数量
        :param ends: 检索网页特征
        """
        from multiprocessing import Pool

        pool = Pool()
        rec = {}
        current = [url]
        pages = []
        i = 0
        code = 0

        rec[url] = True
        while i <= count:
            if len(current) == 0:
                break
            i += len(current)

            parse_jobs = []
            for u in current:
                parse_jobs.append(pool.apply_async(Page.load_url, args=(
                    u, file_path, code, )))
                code += 1
            for j in parse_jobs:
                try:
                    pages.append(j.get())
                except Exception:
                    continue

            crawl_jobs = [pool.apply_async(
                crawl, args=(u, ends, )) for u in current]
            html = [j.get() for j in crawl_jobs]

            current = []
            for h in html:
                for q in h:
                    t = q
                    if t != url:
                        t = url + t

                    if not(t in rec):
                        rec[t] = True
                        current.append(t)
        pool.close()
        pool.join()

        return Base(pages)

    def tokenize(self, tokenizer):
        """利用分词器对文本进行分词

        Args:
            tokenizer: 分词器
        """
        print("tokenizing")
        from tqdm import tqdm
        for i in tqdm(range(len(self.__pages))):
            (self.__pages[i]).tokenize(tokenizer)

    def save_json(self, output_path: str):
        """
        将网页库导出为json文件的形式

        :param output_path: 输出路径
        """
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            for page in self.__pages:
                json.dump(page.show(), f, ensure_ascii=False)
                f.write('\n')

    @staticmethod
    def load_json(input_path: str):
        """从json文件中导入网页库

        Args:
            input_path: 导入路径
        """
        pages = []
        import json
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                current = json.loads(line)
                pages.append(Page(current['url'], current['title'],
                                  current['paragraphs'], current['file_name'], current['file_path']))
        return Base(pages)


def crawl(url: str, ends: List[str]) -> List[str]:
    from bs4 import BeautifulSoup
    from urllib.request import urlopen
    html = urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, features='html.parser')

    ret = []
    all_href = soup.find_all('a')
    for h in all_href:
        try:
            next_url = h['href']
        except:
            continue

        if next_url.endswith(ends):
            ret.append(next_url)

    return ret


if __name__ == '__main__':
    test_url = 'http://jwc.hit.edu.cn/'
    save_path = 'Lab1/data/attachment'
    output_path = 'Lab1/data/result/craw.json'

    base = Base.load_url(test_url, save_path, 10)
    base.save_json(output_path)
