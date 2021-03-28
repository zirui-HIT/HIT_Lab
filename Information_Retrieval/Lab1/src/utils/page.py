class Page(object):
    def __init__(self, url, title, paragraphs, file_name, file_path):
        """
        声明一个新的网页

        :param url: 网页url
        :param title: 网页标题，字符串或分词列表
        :param paragraphs: 网页正文（取description），字符串或分词列表
        :param file_name: 附件名称
        :param file_path: 存储附件的地址
        """
        self.__data = {}
        self.__data['url'] = url
        self.__data['title'] = title
        self.__data['paragraphs'] = paragraphs
        self.__data['file_name'] = file_name
        self.__data['file_path'] = file_path

    @staticmethod
    def load_url(url: str,
                 file_path: str,
                 code: int,
                 attachment_type=('txt', 'doc', 'docx')):
        """
        从url中提取信息，并保存到file_path中

        :param url: 提取url
        :param file_path: 存储附件的地址
        :param code: 网页编号
        :param attachment_type: 下载附件类型
        :param tokenizer: 分词器，None不进行分词
        """
        import re
        url_root = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
                              url)[0]

        from bs4 import BeautifulSoup
        from urllib.request import urlopen
        html = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html, features='html.parser')

        # 提取标题和正文
        title = soup.title.string
        file_path = file_path + "/" + title
        title = title + " " + str(code)
        description = soup.find(attrs={"name": "description"})
        if description is None:
            paragraphs = title
        else:
            paragraphs = description['content']

        # 提取并下载附件
        from urllib.request import urlretrieve
        all_href = soup.find_all('a')
        file_name = []
        download_url = []
        for h in all_href:
            name = h.get_text()
            if name.endswith(attachment_type):
                current_url = h['href']
                download_url.append(url_root + current_url)
                file_name.append(name)

        if len(file_name) != 0:
            import os
            if not (os.path.exists(file_path)):
                os.mkdir(file_path)

            for i in range(len(file_name)):
                urlretrieve(download_url[i], file_path + '/' + file_name[i])

        if len(file_name) == 0:
            file_path = None
        ret = Page(url, title, paragraphs, file_name, file_path)
        return ret

    def show(self):
        """
        将该网页以dict的格式返回
        """
        from copy import deepcopy
        return deepcopy(self.__data)

    def tokenize(self, tokenizer):
        """
        对该网页的title和paragraphs进行分词处理
        分词结果覆盖原数据

        :param tokenizer: 分词器
        """
        self.__data['title'] = tokenizer(self.__data['title'])
        self.__data['paragraphs'] = tokenizer(self.__data['paragraphs'])

        if len(self.__data['title']) > 0:
            self.__data['title'].pop()
        if len(self.__data['paragraphs']) > 0:
            self.__data['paragraphs'].pop()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__hash__ == other.__hash__
        else:
            return False

    def __hash__(self):
        return hash(self.__data['url'])
