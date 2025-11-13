#!/usr/bin/env python3
"""
简易 HTTP/HTTPS 代理服务器
用于让内网服务器通过本机访问外部 API
"""

import socket
import threading
import select
import sys

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 8888
BUFFER_SIZE = 8192

class ProxyServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(100)
        print(f"🌐 代理服务器启动成功！")
        print(f"📍 监听地址: {host}:{port}")
        print(f"💡 在服务器上配置:")
        print(f"   export HTTP_PROXY=http://192.168.31.133:{port}")
        print(f"   export HTTPS_PROXY=http://192.168.31.133:{port}")
        print(f"\n等待连接...\n")

    def handle_client(self, client_socket, address):
        try:
            # 接收客户端请求
            request = client_socket.recv(BUFFER_SIZE)
            if not request:
                return

            # 解析请求
            first_line = request.split(b'\n')[0].decode('utf-8', errors='ignore')
            print(f"📥 [{address[0]}] {first_line}")

            # 提取目标服务器信息
            url = first_line.split(' ')[1]
            
            # 处理 CONNECT 方法（HTTPS）
            if first_line.startswith('CONNECT'):
                self.handle_https(client_socket, request, first_line)
            else:
                # 处理 HTTP
                self.handle_http(client_socket, request, url)

        except Exception as e:
            print(f"❌ 错误: {e}")
        finally:
            client_socket.close()

    def handle_https(self, client_socket, request, first_line):
        """处理 HTTPS CONNECT 请求"""
        try:
            # 解析目标地址
            host_port = first_line.split(' ')[1]
            host, port = host_port.split(':')
            port = int(port)

            # 连接到目标服务器
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((host, port))

            # 发送连接成功响应
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            print(f"✅ HTTPS 隧道建立: {host}:{port}")

            # 双向转发数据
            self.forward_data(client_socket, remote_socket)

        except Exception as e:
            print(f"❌ HTTPS 连接失败: {e}")
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')

    def handle_http(self, client_socket, request, url):
        """处理 HTTP 请求"""
        try:
            # 解析 URL
            if url.startswith('http://'):
                url = url[7:]
            
            host_end = url.find('/')
            if host_end == -1:
                host_end = len(url)
            
            host_port = url[:host_end]
            if ':' in host_port:
                host, port = host_port.split(':')
                port = int(port)
            else:
                host = host_port
                port = 80

            # 连接到目标服务器
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((host, port))

            # 转发请求
            remote_socket.send(request)
            print(f"✅ HTTP 请求转发: {host}:{port}")

            # 接收响应并转发给客户端
            while True:
                response = remote_socket.recv(BUFFER_SIZE)
                if not response:
                    break
                client_socket.send(response)

            remote_socket.close()

        except Exception as e:
            print(f"❌ HTTP 请求失败: {e}")
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')

    def forward_data(self, client_socket, remote_socket):
        """双向转发数据（用于 HTTPS）"""
        try:
            sockets = [client_socket, remote_socket]
            while True:
                readable, _, _ = select.select(sockets, [], [], 60)
                if not readable:
                    break

                for sock in readable:
                    data = sock.recv(BUFFER_SIZE)
                    if not data:
                        return

                    if sock is client_socket:
                        remote_socket.send(data)
                    else:
                        client_socket.send(data)

        except Exception as e:
            print(f"❌ 数据转发错误: {e}")

    def run(self):
        """运行代理服务器"""
        try:
            while True:
                client_socket, address = self.server.accept()
                # 为每个连接创建新线程
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            print("\n\n👋 代理服务器已停止")
            sys.exit(0)

if __name__ == '__main__':
    proxy = ProxyServer(LISTEN_HOST, LISTEN_PORT)
    proxy.run()

