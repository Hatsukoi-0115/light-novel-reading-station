import requests
import urllib.parse
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# 网站专属配置
TARGET_SEARCH_URL = "https://www.wenku8.net/modules/article/search.php"
# 1. 从浏览器复制的完整请求头（必须严格匹配）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Host": "www.wenku8.net",
    "Referer": "https://www.wenku8.net/modules/article/search.php",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}

# 2. 全局会话（维护Cookie）
session = requests.Session()

def wenku8_login():
    LOGIN_URL = "https://www.wenku8.net/login.php"
    USERNAME = "2260972991@qq.com"
    PASSWORD = "jjy2260972991"

    try:
        # 步骤1：先访问首页，获取基础Cookie
        session.get("https://www.wenku8.net", headers=HEADERS, timeout=10)

        # 步骤2：访问登录页，获取登录所需的Cookie
        login_page = session.get(LOGIN_URL, headers=HEADERS, timeout=10)
        login_page.encoding = "gbk"

        # 步骤3：构造该网站专属的登录参数（必须包含usecookie和action）
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "usecookie": "31536000",  # 该网站要求的"记住登录"时长（1年）
            "action": "login",  # 该网站登录接口的必填参数
            "submit": "登 录"  # 按钮value必须和页面一致（带空格）
        }

        # 步骤4：发送登录请求（POST）
        login_response = session.post(
            LOGIN_URL,
            headers=HEADERS,
            data=login_data,
            timeout=10,
            allow_redirects=True
        )
        login_response.encoding = "gbk"

        # 步骤5：该网站的登录成功判断（检查"退出登录"链接）
        if "登录成功" in login_response.text or "退出登录" in login_response.text or "个人中心" in login_response.text:
            print("登录成功！")
            #is_logged_in = True
            return True
        elif "用户名或密码错误" in login_response.text:
            print("登录失败：用户名或密码错误")
            return False
        else:
            print(f"登录失败：页面内容未匹配成功标识")
            print(f"响应内容片段：{login_response.text[:500]}")
            return False
    except Exception as e:
        print(f"登录出错：{e}")
        return False

def try_to_get(url):
    response = session.get(url, headers=HEADERS, timeout=10)
    response.encoding = "gbk"
    if "login.php" in response.url or "用户名或邮箱" in response.text:
        print("登录状态失效，重新登录...")
        if wenku8_login():
            response = session.get(url, headers=HEADERS, timeout=10)
            response.encoding = "gbk"
            return {
                'html': BeautifulSoup(response.text, "html.parser"),
                'url': response.url
            }
        else:
            return False
    else:
        return {
            'html': BeautifulSoup(response.text, "html.parser"),
            'url': response.url
        }

def wenku8_gbk_encode(s):
    """该网站专属的GBK编码（处理特殊字符）"""
    if not s:
        return ""
    try:
        return urllib.parse.quote(s.encode("gbk", errors="replace"))
    except:
        return ""

@app.route('/novelgetter')
def novelgetter():
    try:
        searchtype = request.args.get("searchtype", "articlename")  # 该网站默认搜索类型是articlename
        searchkey = request.args.get("searchkey", "")
        encoded_params = f"searchtype={searchtype}&searchkey={wenku8_gbk_encode(searchkey)}"
        fullUrl = f"{TARGET_SEARCH_URL}?{encoded_params}"
        print(f"访问搜索页：{fullUrl}")

        # 5. 解析该网站的搜索结果（匹配其HTML结构）
        backpage = try_to_get(fullUrl)
        if not backpage:
            return jsonify({"error": "登录失败"}), 401

        soup=backpage['html']
        print(backpage['url'])
        if 'book' in backpage['url']:       #url判断特殊情况，搜索结果仅有一本书，不显示搜索结果页，网站自动跳转至详情页
            novelinfo = [i.text for i in soup.select_one('#content table tr+tr').select('td')]
            print(novelinfo)
            return jsonify([{
                "title": soup.select_one('#content b').text,
                "link": backpage['url'],
                "img_link": soup.select_one('#content img').get('src', ''),
                "author": f'作者:{novelinfo[1][5:]}/分类:{novelinfo[0][5:]}',                         #作者和分类字段
                "status": f'更新:{novelinfo[3][5:]}/字数:{novelinfo[4][5:-1]}/{novelinfo[2][5:]}'       #更新、字数和连载状态字段
            }])

        # 4. 验证搜索结果是否完整（检查"搜索结果"关键词）
        if "搜索结果" not in str(soup.find_all('caption')):
            print("搜索结果异常")
            return jsonify({"error": "搜索结果未加载"}), 500

        b_tags = soup.select('table b')
        print(f"匹配到的标签数量：{len(b_tags)}")
        novel_list = []

        for b_tag in b_tags:
            print(b_tag.text)
            a_tag = b_tag.find('a')
            if not a_tag:
                print('a标签不存在')
                continue
            novel_title = a_tag.get('title')

            # 补全详情页链接
            novel_link = f'https://www.wenku8.net{a_tag.get('href')}'

            # 优化图片链接查找逻辑
            img_tag = b_tag.find_parent('div').find_parent('div').find('img')
            if not img_tag:
                print('ifalse')
            img_link = img_tag.get('src', '') if img_tag else ''
            author_tag = b_tag.find_next_sibling('p')
            status_tag = author_tag.find_next_sibling('p')

            novel_list.append({
                'title': novel_title,
                'link': novel_link,
                'img_link': img_link,
                'author': author_tag.text,
                'status': status_tag.text
            })

        return jsonify(novel_list)
    except Exception as e:
        print(f"后端错误：{e}")
        return jsonify([])

@app.route('/contentgetter')
def contentgetter():
    try:
        novel_url=request.args.get("novelurl", "")

        soup = try_to_get(novel_url)['html']
        if not soup:
            return jsonify({"error": "登录失败"}), 401

        #需要在小说详情页中转，第二次请求
        content_url='https://www.wenku8.net'+soup.find('legend').find_next('a').get('href')

        soup = try_to_get(content_url)['html']
        if not soup:
            return jsonify({"error": "登录失败"}), 401

        #print(soup.find('table'))
        content_html=str(soup.find('table'))
        page_title=soup.select_one('#title').text
        return jsonify({
            'code': 200,
            'msg': 'success',
            'tagHtml': content_html,        # 提取的标签完整HTML
            'content_url': content_url,
            'pageTitle':page_title
        })
    except Exception as e:
        print("后端错误：", e)
        return jsonify([])

@app.route('/textgetter')
def textgetter():
    try:
        text_url=request.args.get("texturl", "")

        soup = try_to_get(text_url)['html']
        if not soup:
            return jsonify({"error": "登录失败"}), 401

        #print(soup.select_one('#content'))
        text_html=str(soup.select_one('#content'))
        page_title=soup.select_one('#title').text
        return jsonify({
            'code': 200,
            'msg': 'success',
            'tagHtml': text_html,            # 提取的标签完整HTML
            'pageTitle':page_title
        })
    except Exception as e:
        print("后端错误：", e)
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
