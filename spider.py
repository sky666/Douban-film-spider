import os
import requests
import pandas as pd
from pyquery import PyQuery as pq


'''
    步骤：
    1. 下载页面          
    2. 解析页面            
    3. 保存数据
'''


def cached_url(url):
    """
    缓存一次, 避免重复下载浪费时间
    """
    folder = 'cached'  # 缓存在 cached 文件夹中
    filename = url.split('=', 1)[-1] + '.html'  # 用 url 中 start 后的数字命名 html 页面
    path = os.path.join(folder, filename)
    if os.path.exists(path):  # 判断是否页面已缓存在本地，如果已缓存，直接读取本地页面
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:  # 如果是第一次下载页面，使用 requests 请求页面并保存到本地文件夹
        if not os.path.exists(folder):
            # 建立 cached 文件夹
            os.makedirs(folder)

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url, headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    # 小作用域变量用单字符
    m = {}  # 保存为字典
    m['name'] = e('.title').text().split(' ')[0]  # 电影名称
    m['score'] = e('.rating_num').text()  # 电影评分
    m['quote'] = e('.inq').text()  # 电影引用
    m['cover_url'] = e('img').attr('src')  # 电影图片链接
    m['ranking'] = e('.pic').find('em').text()  # 电影排名
    m['director'] = e('.bd').find('p').text().split(' ')[1]  # 电影导演

    return m


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    # 页面只需要下载一次
    page = cached_url(url)
    e = pq(page)
    items = e('.item')
    # 调用 movie_from_div
    movies = [movie_from_div(i) for i in items]
    return movies


def download_image(url, name):
    '''
    下载电影图片
    '''
    folder = "img"
    name = name + '.jpg'
    path = os.path.join(folder, name)

    if not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(path):
        return

    headers = {
        'user-agent': '''Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8''',
    }
    # 发送网络请求, 把结果写入到文件夹中
    r = requests.get(url, headers)
    with open(path, 'wb') as f:
        f.write(r.content)


def append_to_csv(data):
    '''
    保存数据
    '''
    file_name = './电影信息.csv'
    df = pd.DataFrame(data)
    df.to_csv(file_name, mode='a', encoding='utf_8_sig', header=False, index=False)


def main():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)
        print('top250 movies', movies)
        append_to_csv(movies)  # 保存电影信息
        [download_image(m['cover_url'], m['name']) for m in movies]  # 下载电影图片


if __name__ == '__main__':
    main()
