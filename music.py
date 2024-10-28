import re  # 导入正则表达式模块
from tqdm import tqdm  # 导入进度条模块
import requests  # 导入 HTTP 请求模块
from pyquery import PyQuery  # 导入 pyquery，用于解析 HTML
import mysql.connector
import os
import tkinter as tk
from tkinter import messagebox

import os

#连接mysql数据库
# db = mysql.connector.connect(
#     host="127.0.0.1",
#     user="root",
#     password="123456",  # 替换为你的 MySQL 密码
#     database="musicDB"
# )
# cursor = db.cursor()
def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="123456",  # 替换为你的 MySQL 密码
        database="musicDB"
    )



# 创建保存音乐到数据库的函数
# def insert_music_to_db(title, music_data):
#
#     sql = "INSERT INTO music_files (title, music_data) VALUES (%s, %s)"
#     cursor.execute(sql, (title, music_data))
#     db.commit()

def insert_music_to_db(title, music_data):
    db = connect_db()
    cursor = db.cursor()
    sql = "INSERT INTO music_files (title, music_data) VALUES (%s, %s)"
    cursor.execute(sql, (title, music_data))
    db.commit()
    cursor.close()
    db.close()

# 定义函数获取音乐的索引
def get_music_index(name):
    # 构造请求的 URL，包含用户输入的歌曲名称
    url = f'https://www.2t58.com/so/{name}/.html'
    # 发送 GET 请求获取网页内容
    response = requests.get(url)
    # 使用 PyQuery 解析网页内容
    doc = PyQuery(response.content)
    # 获取所有 class 为 "name" 的元素
    names = doc(".name").items()
    a = 1
    # 遍历获取到的歌曲名称
    for j in names:
        # 打印歌曲名称和序号
        print(f"选项 {a}: {j.text()}")
        a += 1
        # 如果序号等于 8，则停止遍历
        if a == 8:
            break
    # 正则表达式，用于提取歌曲 ID
    ex = '<div class="name"><a href="/song/(.*?).html" target="_mp3">.*?</a></div>'
    # 使用正则表达式提取所有歌曲 ID
    return re.findall(ex, response.text, re.S)

# 定义函数下载音乐
def download_music(file_all, music_id):
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
    # 构造 POST 请求的数据
    data = {'id': music_id, 'type': 'music'}
    # 要请求的 URL
    url2 = 'https://www.2t58.com/js/play.php'
    # 发送 POST 请求获取歌曲播放信息
    resp2 = requests.post(url=url2, headers=headers, data=data)
    # 解析返回的 JSON 数据
    json_data = resp2.json()
    # 获取音乐播放 URL
    music_url = json_data['url']
    # 发送 GET 请求下载音乐文件，使用流式读取
    music_response = requests.get(url=music_url, stream=True)
    # 生成文件名
    filename = json_data['title'] + '.mp3'

    # 打开文件以写入二进制数据
    with open(f"{file_all}\\{filename}", 'wb') as f:
        # 使用 tqdm 显示下载进度条
        qbar = tqdm(music_response.iter_content(chunk_size=1024), desc=filename, total=int(music_response.headers['Content-Length']) / 1024, unit_scale=True)
        # 将下载的音乐文件内容写入文件
        for data in qbar:
            f.write(data)

    # 将音乐数据保存到数据库
    #通过拿到music_url选定音乐的url链接，用requests.get()方法爬取到选定歌曲的音乐资源存入到mysic_data里面
    music_data = requests.get(music_url).content
    #然后把music_data传入到插入数据库的方法内，通过kv对应存入到数据库内
    insert_music_to_db(json_data['title'], music_data)
    # 打印下载成功的消息
    print(f"{filename} 下载成功,并保存到数据库！")

# 登录界面函数
def login():
    def validate_login():
        username = entry_username.get()
        password = entry_password.get()

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE user_name = %s AND pwd = %s", (username, password))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("登录成功", "登录成功！")
            root.destroy()  # 关闭登录窗口
            main()  # 调用主函数
        else:
            messagebox.showerror("登录失败", "用户名或密码错误！")

        cursor.close()
        db.close()

    root = tk.Tk()
    root.title("登录界面")
    #这个是定义一个输入框叫root
    label_username = tk.Label(root, text="用户名:")
    #显示这个root的输入框
    label_username.pack(pady=5)
    #把那个root的输入框拿到的输入值存入到entry_username这个里面，然后在登录验证的地方拿来跟数据库拿到的做对比验证（明文对比）

    entry_username = tk.Entry(root)
    entry_username.pack(pady=5)
    #密码的部分同上
    label_password = tk.Label(root, text="密码:")
    label_password.pack(pady=5)
    entry_password = tk.Entry(root, show='*')
    entry_password.pack(pady=5)

    button_login = tk.Button(root, text="登录", command=validate_login)
    button_login.pack(pady=20)

    root.mainloop()

# 主函数
def main():
    # 获取用户输入的歌曲名称
    name = input("name:")
    # 获取用户输入的文件保存路径
    file_all = input("file_all:")
    # 获取歌曲索引
    music_index = get_music_index(name)
    # 获取用户选择的歌曲序号
    num = int(input("num:"))
    # 从索引中选择对应的歌曲 ID
    selected_music_id = music_index[num - 1]
    # 下载选定的音乐
    download_music(file_all, selected_music_id)

# 如果脚本是作为主程序执行，则调用主函数
if __name__ == "__main__":
    login()

