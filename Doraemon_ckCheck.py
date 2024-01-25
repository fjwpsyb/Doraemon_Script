import requests
from utils.User_agent import generate_random_user_agent
from utils.logger import setup_logger
from concurrent.futures import ThreadPoolExecutor, as_completed

# 初始化 log 对象
log = setup_logger()

# 校验ck是否有效
def is_login_by_x1a0he(ck):
    try:
        url = 'https://plogin.m.jd.com/cgi-bin/ml/islogin'
        headers = {
            "Cookie": ck,
            "Referer": "https://h5.m.jd.com/",
            "User-Agent": generate_random_user_agent()  # 使用 ua 获取 User-Agent 字符串
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('islogin') == '1':
                log.info(f"Cookie 有效：{ck}")
                return True
            else:
                log.error(f"Cookie 无效：{ck}")
                return False
        else:
            log.error("isLoginByX1a0He 发生错误")
            return None
    except requests.RequestException as error:
        log.error("isLoginByX1a0He 发生错误: " + str(error))
        return None

# 并发校验
def check_cookies(cookies, max_workers=10):
    valid_cookies = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ck = {executor.submit(is_login_by_x1a0he, ck): ck for ck in cookies}
        for future in as_completed(future_to_ck):
            ck = future_to_ck[future]
            try:
                if future.result():
                    valid_cookies.append(ck)
            except Exception as exc:
                log.error(f"{ck} 生成异常: {exc}")
    return valid_cookies

# 读取文件并有效的ck重写到文件中
def read_file_and_save_valid_cookies(filename, max_workers=10):
    try:
        with open(filename, 'r') as file:
            lines = file.read().splitlines()

        valid_cookies = check_cookies(lines, max_workers)

        # 将有效的 Cookie 写回文件
        with open(filename, 'w') as file:
            for cookie in valid_cookies:
                file.write(cookie + "\n")

        log.info("有效的 Cookies 已重新写入文件")

    except FileNotFoundError:
        log.error(f"文件 {filename} 未找到。")
    except IOError:
        log.error(f"读取文件 {filename} 时发生错误。")

# 如果文件在父级目录中
# filename = '../JD_COOKIE.txt'

# 如果文件在父级的同级目录中
# filename = '../AnotherFolder/JD_COOKIE.txt'

# 当前目录
filename = "JD_COOKIE.txt"

# 调用函数
read_file_and_save_valid_cookies(filename, max_workers=50)
