#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re
import time
import os.path
try:
    from PIL import Image
except:
    pass
header = '''Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.8
Cache-Control:max-age=0
Content-Type:application/x-www-form-urlencoded
Host:218.75.197.123:83
Origin:http://218.75.197.123:83
Proxy-Connection:keep-alive
Referer:http://218.75.197.123:83/
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Mobile Safari/537.36'''
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")
def get_headers(headers):
    list = [str(i) for i in headers.split('\n')]
    list2 = []
    for i in list:
        list3 = i.split(':',1)
        list2.append(list3)
    dict1 = dict(list2)
    return dict1
headers = get_headers(header)
def isLogin():
    url = "http://218.75.197.123:83/xs_main.aspx?xh=14408400126"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False
def get_view():
    '''_view 是一个动态变化的参数'''
    index_url = 'http://218.75.197.123:83/'
    # 获取登录时需要用到的_viewstate
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="__VIEWSTATE" value="(.*?)"'
    # 这里的_viewstate 返回的是一个list
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]
def get_captcha():
    captcha_url = 'http://218.75.197.123:83/CheckCode.aspx'
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha
def save_cookies_lwp(cookiejar, filename):
    lwp_cookiejar = cookielib.LWPCookieJar()
    for c in cookiejar:
        args = dict(vars(c).items())
        args['rest'] = args['_rest']
        del args['_rest']
        c = cookielib.Cookie(**args)
        lwp_cookiejar.set_cookie(c)
    lwp_cookiejar.save(filename, ignore_discard=True)
def login(secret, account):
    __VIEWSTATE = get_view()
    # 通过输入的用户名判断是否是手机号
    post_url = 'http://218.75.197.123:83/index.aspx'
    postdata = {
        '__VIEWSTATE': __VIEWSTATE,
        'TextBox2': secret,
        'txtUserName': account,
        'txtSecretCode':'rrrr',
        'RadioButtonList1': '(unable to decode value)',
        'Button1':'',
        'lbLanguage':'',
        'hidPdrs':'',
        'hidsc':'',
    }
    # 不需要验证码直接登录成功
    postdata["txtSecretCode"] = get_captcha()
    login_page = session.post(post_url, data=postdata, headers=headers)
    #print login_page.text
    # 保存 cookies 到文件，
    # 下次可以使用 cookie 直接登录，不需要输入账号和密码
    print session.cookies
    save_cookies_lwp(session.cookies, 'cookies')

try:
    input = raw_input
except:
    pass
if __name__ == '__main__':
    if isLogin():
        print('您已经登录')
    else:
        account = input('请输入你的用户名\n>  ')
        secret = input("请输入你的密码\n>  ")
        login(secret, account)
        if isLogin():
            print('您已经登录')
        else:
            print('登录失败')