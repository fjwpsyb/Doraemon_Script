import json
import requests
import re
from json import dumps as jsonDumps

from utils.logger import setup_logger

log = setup_logger()

class ql:
    def __init__(self, address: str, id: str, secret: str) -> None:
        """
        初始化
        """
        self.address = address
        self.id = id
        self.secret = secret
        self.valid = True
        self.login()

    def log(self, content: str) -> None:
        """
        日志
        """
        print(content)

    def login(self) -> None:
        """
        登录
        """
        url = f"{self.address}/open/auth/token?client_id={self.id}&client_secret={self.secret}"
        try:
          rjson = requests.get(url).json()
          if (rjson['code'] == 200):
            log.info('登录成功')
            self.auth = f"{rjson['data']['token_type']} {rjson['data']['token']}"
          else:
            log.error(f"登录失败：{rjson['message']}")
        except Exception as e:
          self.valid = False
          log.error(f"登录失败：{str(e)}")

    def getEnvs(self, Name=None) -> list:
        """
        获取环境变量
        """
        if Name != None:
            url = f"{self.address}/open/envs?searchValue={Name}"
        else:
            url = f"{self.address}/open/envs?searchValue="
        headers = {"Authorization": self.auth}
        try:
            rjson = requests.get(url, headers=headers).json()
            if (rjson['code'] == 200):
                return rjson['data']
            else:
                self.log(f"获取环境变量失败：{rjson['message']}")
        except Exception as e:
            self.log(f"获取环境变量失败：{str(e)}")

    def move(self, id: int, fromIndex: int, toIndex: int):
        """
        环境变量p排序
        """
        url = f"{self.address}/open/envs/{id}/move"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=json.dumps(({"fromIndex": fromIndex, "toIndex": toIndex}))).json()
            print(rjson)
            if (rjson['code'] == 200):
                self.log(f"环境变量排序成功：{fromIndex}-{toIndex}")
                return True
            else:
                self.log(f"环境变量排序失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"环境变量排序失败：{str(e)}")
            return False

    def disEnvs(self, ids: list):
        """
        禁用环境变量
        """
        url = f"{self.address}/open/envs/disable"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=jsonDumps(ids)).json()
            print(rjson)
            if (rjson['code'] == 200):
                self.log(f"禁用环境变量成功：{len(ids)}")
                return True
            else:
                self.log(f"禁用环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"禁用环境变量失败：{str(e)}")
            return False

    def deleteEnvs(self, ids: list):
        """
        删除环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.delete(url, headers=headers, data=jsonDumps(ids)).json()
            print(rjson)
            if (rjson['code'] == 200):
                self.log(f"删除环境变量成功：{len(ids)}")
                return True
            else:
                self.log(f"删除环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"删除环境变量失败：{str(e)}")
            return False

    def addEnvs(self, envs: list) -> bool:
        """
        新建环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.post(url, headers=headers, data=jsonDumps(envs)).json()
            if (rjson['code'] == 200):
                self.log(f"新建环境变量成功：{len(envs)}")
                return True
            else:
                self.log(f"新建环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"新建环境变量失败：{str(e)}")
            return False

    def updateEnv(self, env: dict) -> bool:
        """
        更新环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=jsonDumps(env)).json()
            if (rjson['code'] == 200):
                self.log(f"更新环境变量成功")
                return True
            else:
                self.log(f"更新环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"更新环境变量失败：{str(e)}")
            return False

    def getConfig(self, filename: str) -> str:
      """
      获取青龙文件内容
      """
      url = f"{self.address}/open/configs/{filename}"
      headers = {"Authorization": self.auth}
      try:
        rjson = requests.get(url, headers=headers).json()
        if (rjson['code'] == 200):
          return rjson['data']
        else:
          log.error(f"获取环境变量失败：{rjson['message']}")
      except Exception as e:
        log.error(f"获取环境变量失败：{str(e)}")

    def updateConfig(self, filename: str, content: str) -> bool:
      """
      更新青龙文件内容
      """

      obj = {
        "name": filename,
        "content": content
      }

      url = f"{self.address}/open/configs/save"
      headers = {"Authorization": self.auth, "content-type": "application/json"}
      try:
        rjson = requests.post(url, headers=headers, data=jsonDumps(obj)).json()
        log.info(rjson)
        if (rjson['code'] == 200):
          log.info(f"更新{filename}文件成功")
          return True
        else:
          log.error(f"更新文件失败：{rjson['message']}")
          return False
      except Exception as e:
        self.log(f"更新文件失败：{str(e)}")
        return False

    def common_update_data(self, config, envs):
      """
      新增/替换配置文件中的value
      """
      for env in envs:
        # 正则表达式匹配模式：匹配环境变量声明的行
        pattern = re.compile(r'^export[ ]+{name}[ ]*=[ ]*".*"$'.format(name=re.escape(env['name'])), re.MULTILINE)
        # 新的环境变量声明
        new_declaration = 'export {name}="{value}"'.format(name=env['name'], value=env['value'])
        
        # 检查配置中是否已存在此环境变量的声明
        if pattern.search(config):
          # 如果存在，则替换其值
          config = pattern.sub(new_declaration, config)
        else:
          # 如果不存在，则在配置字符串末尾添加新的环境变量声明
          # 确保配置字符串以换行符结束，以便添加新的声明
          if not config.endswith('\n'):
            config += '\n'
          config += new_declaration + '\n'

      return config


    def modify_QL_Config(self, envs):
      """
      修改青龙配置文件变量
      """
      configData = self.getConfig(filename = 'config.sh')
      configData = self.common_update_data(config = configData,  envs = envs)
      return self.updateConfig(filename = 'config.sh', content = configData)
