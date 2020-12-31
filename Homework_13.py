import asyncio
import os
import time

file_type = ['txt', 'py', 'c', 'java', 'csv']


class SearchPath:
    """
    以查找文件名的类
    """
    def __init__(self, keywords):
        self.keywords = keywords
    @staticmethod
    async def find(self, path):
        file_list = os.listdir(path)
        for dirs in file_list:
            if dirs == self.keywords and os.path.isfile(os.path.join(path, dirs)):
                print('Find file in:', os.path.join(path, dirs))
            elif os.path.isdir(os.path.join(path, dirs)):
                try:
                    await self.find(path=os.path.join(path, dirs))
                except Exception as e:
                    pass


class SearchContent:
    """
    查找文件内容的类
    """
    def __init__(self, keywords):
        self.keywords = keywords

    async def find(self, path):
        file_list = os.listdir(path)
        for files in file_list:
            if os.path.isdir(os.path.join(path, files)):
                try:
                    await self.find(path=os.path.join(path, files))
                except Exception as e:
                    pass
            elif os.path.isfile(os.path.join(path, files)):
                if files.split('.')[-1] in file_type:
                    try:
                        with open(os.path.join(path, files)) as f:
                            line = f.readlines()

                            for i in range(len(line)):
                                if self.keywords in line[i]:
                                    print('Find Keywords In File:', os.path.join(path, files),
                                          '\nFile Name:', files,
                                          '\nlines:', i+1,
                                          '\nindex:', line[i].find(self.keywords),
                                          '\nRaw Content:', line[i])
                    except Exception as e:
                        pass


class LocalMiner:
    """
    查找类
    """
    def __init__(self, keywords, search_path, search_type):
        self.keywords = keywords
        self.search_path = search_path
        self.search_type = search_type

    async def run(self):
        if self.search_type == 'path':
            search_path = SearchPath(keywords=self.keywords)
            task = asyncio.create_task(search_path.find(path=self.search_path))
            await task

        elif self.search_type == 'content':
            search_content = SearchContent(keywords=self.keywords)
            await search_content.find(path=self.search_path)


def normal_search(path = '/Users/xie/PycharmProjects/现代程设/', keywords='xie'):
    file_list = os.listdir(path)
    for files in file_list:
        if os.path.isdir(os.path.join(path, files)):
            try:
                normal_search(path=os.path.join(path, files))
            except Exception as e:
                pass
        elif os.path.isfile(os.path.join(path, files)):
            if files.split('.')[-1] in file_type:
                try:
                    with open(os.path.join(path, files)) as f:
                        line = f.readlines()

                        for i in range(len(line)):
                            if keywords in line[i]:
                                print('Find Keywords In File:', os.path.join(path, files),
                                      '\nFile Name:', files,
                                      '\nlines:', i + 1,
                                      '\nindex:', line[i].find(keywords),
                                      '\nRaw Content:', line[i])
                except Exception as e:
                    pass


def main():
    LM = LocalMiner(keywords='xie', search_path='/Users/xie/PycharmProjects/', search_type='content')
    asyncio.run(LM.run())
    #normal_search()



if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print('END! Run Time: ', end-start)



