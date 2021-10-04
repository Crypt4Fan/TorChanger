import logging
import socket
import time

import requests

logger = logging.getLogger(__name__)


class TorChanger():

    def __init__(self,
                 host: str,
                 proxy_port: int,
                 ctrl_port: int,
                 pwd :str):
        self.host = host
        self.proxy_port = proxy_port
        self.ctrl_port = ctrl_port
        self.pwd = pwd
        self.proxies = {
            'http': f'socks5h://{host}:{proxy_port}',
            'https': f'socks5h://{host}:{proxy_port}'
        }


    def _authenticate(self, sock: socket.socket):
        sock.send(f'AUTHENTICATE "{self.pwd}"\r\n'.encode())
        res = sock.recv(1024).decode()
        logger.debug(f'AUTHENTICATE signal return: {res}')
        if not res.startswith('250'):
            raise Exception(f'AUTHENTICATE signal return: {res}')


    def _send_newnym(self, sock: socket.socket):
        sock.send('signal NEWNYM\r\n'.encode())
        res = sock.recv(1024).decode()
        logger.debug(f'NEWNYM signal return: {res}')
        if not res.startswith('250'):
            raise Exception(f'NEWNYM signal return: {res}')


    def _change_tor_chain(self):
        sock = socket.socket()
        sock.connect((self.host, self.ctrl_port))
        self._authenticate(sock)
        self._send_newnym(sock)
        sock.close()


    def get_current_ip(self):
        return requests.get(
            'https://ipinfo.io',
            proxies=self.proxies
        ).json()['ip']


    def change_ip(self, delay: int = 10, retry: int = 3):
        last_error = None
        for _ in range(retry):
            try:
                cur_ip = self.get_current_ip()
                logger.debug(f'Current IP: {cur_ip}')
                self._change_tor_chain()
                logging.debug(f'Sleep for {delay} seconds')
                time.sleep(delay)
                new_ip = self.get_current_ip()
                logger.debug(f'New IP: {new_ip}')
                if new_ip != cur_ip:
                    return new_ip
            except Exception as error:
                logger.debug(f'Exception raised while change ip: {error}')
                last_error = error
                continue
        logging.debug(f"Can't change ip, {retry} attempts")
        raise last_error
