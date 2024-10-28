import re  # 导入正则表达式模块
from tqdm import tqdm  # 导入进度条模块
import requests  # 导入 HTTP 请求模块
from pyquery import PyQuery  # 导入 pyquery，用于解析 HTML
import time  # 导入时间模块
import mysql.connector

# MySQL connection
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="123456",
    database="musicDB"
)
cursor = db.cursor()

# Function to save music file to the database
def save_music_to_db(title, file_path, file_data):
    # 定义一个函数 save_music_to_db，用于将音乐文件保存到数据库中
    # 参数包括：
    # title: 音乐的标题
    # file_path: 音乐文件的存储路径
    # file_data: 音乐文件的二进制数据

    query = "INSERT INTO music (title, file_path, file) VALUES (%s, %s, %s)"
    # 定义插入 SQL 查询，向 music 表中插入 title, file_path, 和 file 的值
    # %s 是占位符，将在执行时被实际的参数值替代

    cursor.execute(query, (title, file_path, file_data))
    # 使用游标执行 SQL 语句，将实际的 title, file_path 和 file_data 作为参数传递进去

    db.commit()
    # 提交当前事务，确保将插入的数据保存到数据库中


# 获取用户输入的歌曲名称
name = input("name:")
# 获取用户输入的文件保存路径
file_all = input("file_all:")
# 构造要请求的 URL，包含歌曲名称
url = 'https://www.2t58.com/so/{}/.html'.format(name)
# 发送 GET 请求获取网页内容
response = requests.get(url)
# 使用 PyQuery 解析网页内容
doc = PyQuery(response.content)
# 获取所有 class 为 "name" 的元素
names = doc(".name").items()
# 正则表达式，用于提取歌曲 ID
ex = '<div class="name"><a href="/song/(.*?).html" target="_mp3">.*?</a></div>'
# 使用正则表达式提取所有歌曲 ID
musicIndex = re.findall(ex, response.text, re.S)
j = 1
# 遍历获取到的歌曲名称
for i in names:
    # 打印歌曲名称和序号
    print(i.text(), [j])
    # 如果序号等于 7，则停止遍历
    if j == 7:
        break
    j += 1
# 获取用户输入的歌曲序号
num = int(input("num:"))
# 创建一个列表来存储选择的歌曲 ID
smallmusicList = []
# 将用户选择的歌曲 ID 添加到列表中
smallmusicList.append(musicIndex[num - 1])

# 设置 HTTP 请求头
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',  # 接受的内容类型
    'Accept-Encoding': 'gzip, deflate',  # 支持的编码格式
    'Accept-Language': 'zh-CN,zh;q=0.9',  # 支持的语言
    'Connection': 'keep-alive',  # 连接保持活跃
    'Content-Length': '26',  # 内容长度
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',  # 内容类型
    'Cookie': 'Hm_lvt_b8f2e33447143b75e7e4463e224d6b7f=1690974946; Hm_lpvt_b8f2e33447143b75e7e4463e224d6b7f=1690976158',  # Cookie
    'Host': 'www.2t58.com',  # 请求的主机
    'Origin': 'https://www.2t58.com',  # 请求的来源
    'Referer': 'https://www.2t58.com/song/bWhzc3hud25u.html',  # 请求的来源页面
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',  # 用户代理
    'X-Requested-With': 'XMLHttpRequest'  # 请求类型
}

# 遍历选择的歌曲 ID 列表
for i in smallmusicList:
    # 构造 POST 请求的数据
    data = {'id': i, 'type': 'music'}
    # 要请求的 URL
    url2 = 'https://www.2t58.com/js/play.php'
    # 发送 POST 请求获取歌曲播放信息
    response2 = requests.post(url=url2, headers=headers, data=data)
    # 解析返回的 JSON 数据
    json_data = response2.json()
    # 获取音乐播放 URL
    musicList = json_data['url']
    # 发送 GET 请求下载音乐文件
    musicResponse = requests.get(url=musicList)
    # 生成文件名
    filename = json_data['title'] + '.mp3'

#第一版
    # # 使用 tqdm 显示下载进度条
    # qbar = tqdm(musicResponse.iter_content(chunk_size=1024), desc=filename, total=int(musicResponse.headers['Content-Length']) / 1024, unit_scale=True)
    # # 将下载的音乐文件保存到指定路径
    # with open(file_all + "\\" + filename, 'wb') as f:
    #     # 写入文件内容
    #     for data in qbar:
    #         f.write(data)
    #     # 关闭文件
    #     f.close()
    #     # 暂停 0.5 秒
    #     time.sleep(0.5)
    #     # 打印下载成功的消息
    #     print(filename + '下载成功！')

#第二版
    # Save music locally
    file_path = file_all + "\\" + filename
    with open(file_path, 'wb') as f:
        qbar = tqdm(musicResponse.iter_content(chunk_size=1024), desc=filename, total=int(musicResponse.headers['Content-Length']) / 1024, unit_scale=True)
        file_data = b""
        for data in qbar:
            f.write(data)
            file_data += data
        f.close()

    # Save music to MySQL database
    save_music_to_db(json_data['title'], file_path, file_data)
    time.sleep(0.5)
    print(filename + '下载成功！')
