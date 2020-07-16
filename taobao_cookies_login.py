import json
import os
import re
import requests
import requests.utils

s = requests.Session()


# cookie序列化版
class UsernameLogin:
    def __init__(self, username, ua, TPL_password2):
        """
        账号登录对象
        :param username: 用户名
        :param ua: 淘宝的ua参数
        :param TPL_password2: 加密后的密码


        """
        # 检测是否需要验证码的URL
        self.nick_check_url = "https://login.taobao.com/newlogin/account/check.do?appName=taobao&fromSite=0"
        # 验证淘宝用户名密码的URL
        self.login_url = "https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0"
        # 带st码访问的地址
        self.vst_url = "https://login.taobao.com/member/vst.htm?st={}"

        # 淘宝用户名
        self.username = username
        # 淘宝关键参数ua, 包含用户浏览器等一些信息, 很多地方会使用, 从浏览器或抓包工具中复制, 可重复使用.
        self.ua = ua
        # 加密后的密码, 从浏览器或抓包工具中复制j, 可重复使用.
        self.TPL_password2 = TPL_password2

        # 请求超时时间
        self.timeout = 5

    def get_formdata(self):
        """
        获取登录时需要的三个随机参数
        :return:
        """
        get_url = "https://login.taobao.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        }
        formdata = re.findall(r'"loginFormData":({.*});', requests.get(get_url, headers=headers).text)[0]

        return {
            '_csrf_token': re.findall(r'"_csrf_token":"(.*?)",', formdata)[0],
            'umidToken': re.findall(r'"umidToken":"(.*?)",', formdata)[0],
            'hsiz': re.findall(r'"hsiz":"(.*?)",', formdata)[0],
        }

    def _nick_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'loginId': self.username,
            'ua': self.ua,
        }
        try:
            resp = s.post(self.nick_check_url, data=data, timeout=self.timeout)
        except Exception as e:
            print('检测是否需要验证码请求失败, 因为: {}'.format(e))
            return True
        try:
            isCheckCodeShowed = resp.json(strict=False)['isCheckCodeShowed']
            print('是否需要滑块验证: %s ' % '是' if isCheckCodeShowed else '否')
            print('请手动打开浏览器登录, 并通过滑块验证后再试. ')
            return isCheckCodeShowed
        except Exception as e:
            print('恭喜你, 经检测不需要滑块验证. ')

    def _verify_password(self):
        verify_password_headers = {
            # ":authority": "login.taobao.com",
            # ":method": "POST",
            # ":path": "/newlogin/login.do?appName=taobao&fromSite=0",
            # ":scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            # "content-length": "2845",
            "content-type": "application/x-www-form-urlencoded",
            # "cookie": "cna=izqDFzNtlm0CAbaIda94XTnJ; _m_h5_tk=46a1065b197677dd3952f1613f911c8c_1594792516969; _m_h5_tk_enc=2cd44d955cdccea59d67e0c7ecbd8b14; cookie2=18622af4189f775d8281094bc358b793; uc1=cookie14=UoTV6OkzNg3FRA%3D%3D; t=f098d1fb08db2fc8b65411aaa427267f; _tb_token_=7deb38d71e9e3; XSRF-TOKEN=4ac2f85e-d09d-42c9-88bd-2dad2bc7d449; _samesite_flag_=true; UM_distinctid=17352cc39d2169-09034c866a03ef-4353760-100200-17352cc39d31d; thw=cn; l=eB_s1QY7OOJsAWTFBO5wlurza77tyIRf1sPzaNbMiInca6pdtFqWsNQqtjzySdtjgtfvsnxrb3kJjRUJP5zLRx1Hrt7APlUOrl96-; isg=BDw8SfU9T8AfMnuW3dIpQ0J0DdruNeBfNRX36xa98Ccb4d9rIEG77x4XwQmZqRi3; tfstk=cDxGBjqxfF7si37HPcs63EIWMC3RaR2N1aQeYhK__Z-RFy-lQscQ8zW-T51esnUf.",
            "dnt": "1",
            "origin": "https://login.taobao.com",
            "referer": "https://login.taobao.com/member/login.jhtml",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        }

        # 登录taobao.com提交的数据, 如果登录失败, 可以从浏览器复制你的form data
        verify_password_data = {
            "loginId": self.username,
            "password2": self.TPL_password2,
            "keepLogin": "false",
            "ua": self.ua,
            "umidGetStatusVal": "255",
            "screenPixel": "1366x768",
            "navlanguage": "zh-CN",
            "navUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "navPlatform": "Win32",
            "appName": "taobao",
            "appEntrance": "taobao_pc",
            "bizParams": "",
            "style": "default",
            "appkey": "00000000",
            "from": "tbTop",
            "isMobile": "false",
            "lang": "zh_CN",
            "returnUrl": "https://ai.taobao.com/search/index.htm",
            "fromSite": "0",
        }

        # verify_password_data = password_data.update(self.get_formdata())      有时候出现问题, 造成verify_password_data数据为None.
        # 添加进这三个网页随机生成的数据
        verify_password_data['_csrf_token'] = self.get_formdata()['_csrf_token']
        verify_password_data['umidToken'] = self.get_formdata()['umidToken']
        verify_password_data['hsiz'] = self.get_formdata()['hsiz']
        try:
            resp = s.post(self.login_url, headers=verify_password_headers, data=verify_password_data,
                          timeout=self.timeout)
            # 提取申请st码地址
            # st_code_url = re.search(r'', resp.text).group(1)
            st_code_url = resp.json()['content']['data']['asyncUrls'][0]
        except Exception as e:
            print('验证用户名和密码请求失败, 因为: {}'.format(e))
            return None
        # 提取成功则返回
        if st_code_url:
            print('验证用户名密码成功, st码申请地址: {}'.format(st_code_url))
            return st_code_url
        else:
            print('用户名密码验证失败, 请更换data参数.')
            return None

    def _apply_st(self, st_url):
        """
        申请st码
        :return: st码
        """
        try:
            st_resp = s.get(st_url)
        except Exception as e:
            print('申请st码请求失败, 因为: {}'.format(e))
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', st_resp.text)
        if st_match:
            print('获取st码成功, st码: {}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败! ')

    def login(self):
        """
        使用st码登录.
        :return:
        """
        # 判断是否存在cookies_login.txt文件
        if os.path.exists(cookies_file_path):
            return 'cookie_login'
        else:
            # 询问是否继续
            question = input('未找到cookies_login.txt文件, 是否继续通过账号密码登录 ? (y/n)')
            if question == 'y' or question == 'Y':
                pass
            else:
                print('程序已结束. ')
                os._exit(0)
        # 目前requests库还没有很好的办法破解淘宝滑块验证
        self._nick_check()
        st = self._apply_st(self._verify_password())
        # 参数太多好像也请求不成功, 可能是我某个参数有问题. 所以注释了一些参数
        headers = {
            "Host": "login.taobao.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            # "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            # "Referer": "https://login.taobao.com/member/login.jhtml",
            # "Upgrade-Insecure-Requests": "1",
            # "Pragma": "no-cache",
            # "Cache-Control": "no-cache",
        }
        try:
            response = s.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登陆请求失败, 因为: {}'.format(e))
            raise e

        # 登录成功, 提取跳转淘宝个人主页链接
        my_taobao_url = re.search(r'top.location.href = "(.*)";', response.text).group(1)

        if my_taobao_url:
            print('登录淘宝成功, 跳转链接: {}'.format(my_taobao_url))
            self._serialization_cookies()
            return my_taobao_url
        else:
            raise RuntimeError('登录失败! response: {}'.format(response.text))

    def get_taobao_nick_name(self, my_taobao_url):
        """
        获取淘宝昵称
        :return:
        """

        # 参数太多好像也请求不成功, 可能是我某个参数有问题. 所以注释了一些参数
        headers = {
            # "Host": "www.taobao.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            # "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            # "Referer": "https://www.taobao.com/",
            # "Upgrade-Insecure-Requests": "1",
            # "Pragma": "no-cache",
            # "Cache-Control": "no-cache",
        }
        try:
            if my_taobao_url == 'cookie_login':
                # 加载cookies_login.txt文件
                if self._load_cookies():
                    pass
                else:
                    print('cookies 文件读取失败. ')
                try:
                    response = s.get('https://i.taobao.com/my_taobao.htm', headers=headers)
                except Exception as e1:
                    # 3. 判断cookie是否过期
                    print('获取淘宝用户主页请求失败! 因为: {}'.format(e1))
                    # os.remove(cookies_file_path)
                    print('cookies过期, 已删除cookies文件! ')
                    raise e1
            else:
                try:
                    response = s.get(my_taobao_url, headers=headers)
                    response.raise_for_status()
                except Exception as e2:
                    print('获取淘宝用户主页请求失败! 因为: {}'.format(e2))
                    raise e2
            # 提取淘宝昵称
            nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*)"/>', response.text).group(
                1)
            if nick_name_match:
                print('牛啊, 老哥 : {} , 登陆成功! '.format(nick_name_match))
                return nick_name_match
            else:
                raise RuntimeError('获取淘宝昵称失败! response: {}'.format(response.text))
        except Exception as e:
            print('请先登录...')

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(cookies_file_path, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)

        print('已保存cookies: {}'.format(cookies_dict))

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(cookies_file_path, 'r', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies_jar = requests.utils.cookiejar_from_dict(cookies_dict)
            print('已加载cookies文件. ')
            return cookies_jar

    def _load_cookies(self):
        # 1. 判断cookies序列化文件是否存在
        if not os.path.exists(cookies_file_path):
            return False

        # 2. 加载cookies
        s.cookies = self._deserialization_cookies()

        print('加载cookies 登录淘宝成功! ')
        return True


if __name__ == '__main__':
    # 请输入淘宝账号(手机号)
    while True:
        username = input('请输入淘宝账号(手机号): ')
        if re.findall(r"^(1[3-9][0-9]|14[5|7]|15[0|1|2|3|4|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$", username):
            break
        else:
            print('账号输入错误, 请重新输入...')

    print("ua参数和password2参数 需要自己在浏览器的 F12开发者模式 里获得. ")
    ua = input('请输入淘宝登录参数 ua : ')
    password2 = input('请输入加密后的淘宝账号的登录密码 password2 : ')
    # cookies保存的路径, 可以根据需要修改.
    cookies_file_path = os.getcwd() + '\{}cookies.txt'.format(username)
    # 实例化对象
    taobao = UsernameLogin(username, ua, password2)
    # 先登录, 获取淘宝用户主页URL
    my_taobao_url = taobao.login()
    # 然后获取用户昵称
    nick_name = taobao.get_taobao_nick_name(my_taobao_url)
    if nick_name:
        print('现在你可以带着cookies爬取商品数据了. ')
