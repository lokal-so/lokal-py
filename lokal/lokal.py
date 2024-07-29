import requests
from enum import Enum
from typing import List, Optional
import random
import string
from packaging import version
from colorama import Fore, Style, init

SERVER_MIN_VERSION = "0.6.0"

class TunnelType(str):
    HTTP = "HTTP"

class Options:
    def __init__(self):
        self.basic_auth: List[str] = []
        self.cidr_allow: List[str] = []
        self.cidr_deny: List[str] = []
        self.request_header_add: List[str] = []
        self.request_header_remove: List[str] = []
        self.response_header_add: List[str] = []
        self.response_header_remove: List[str] = []
        self.header_key: List[str] = []
    
    def to_dict(self):
        return self.__dict__

class Tunnel:
    def __init__(self, lokal):
        self.lokal = lokal
        self.id: str = ""
        self.name: str = ""
        self.tunnel_type: TunnelType = TunnelType.HTTP
        self.local_address: str = ""
        self.server_id: str = ""
        self.address_tunnel: str = ""
        self.address_tunnel_port: int = 0
        self.address_public: str = ""
        self.address_mdns: str = ""
        self.inspect: bool = False
        self.options: Options = Options()
        self.ignore_duplicate: bool = False
        self.startup_banner: bool = False

    def to_dict(self):
        return {
            **self.__dict__,
            'options': self.options.to_dict()
        }

    def set_local_address(self, local_address: str):
        self.local_address = local_address
        return self

    def set_tunnel_type(self, tunnel_type: TunnelType):
        self.tunnel_type = tunnel_type
        return self

    def set_inspection(self, inspect: bool):
        self.inspect = inspect
        return self

    def set_lan_address(self, lan_address: str):
        self.address_mdns = lan_address.rstrip('.local')
        return self

    def set_public_address(self, public_address: str):
        self.address_public = public_address
        return self

    def set_name(self, name: str):
        self.name = name
        return self

    def ignore_duplicate(self):
        self.ignore_duplicate = True
        return self

    def show_startup_banner(self):
        self.startup_banner = True
        return self

    def create(self):
        if not self.address_mdns and not self.address_public:
            raise ValueError("Please enable either LAN address or random/custom public URL")

        payload = self.to_dict().copy()
        del payload['lokal']

        response = self.lokal.rest.post(self.lokal.base_url + "/api/tunnel/start", json=payload)
        data = response.json()

        if not data.get('success'):
            if self.ignore_duplicate and data.get('message', '').endswith("address is already being used"):
                self.address_public = data['data'][0]['address_public']
                self.address_mdns = data['data'][0]['address_mdns']
                self.id = data['data'][0]['id']
                self.print_startup_banner()
                return self
            raise ValueError(data.get('message', 'Tunnel creation failed'))

        self.address_public = data['data'][0]['address_public']
        self.address_mdns = data['data'][0]['address_mdns']
        self.id = data['data'][0]['id']

        self.print_startup_banner()
        return self

    def get_lan_address(self) -> str:
        if not self.address_mdns:
            raise ValueError("LAN address is not being set")
        return f"{self.address_mdns}.local" if not self.address_mdns.endswith('.local') else self.address_mdns

    def get_public_address(self) -> str:
        if not self.address_public:
            raise ValueError("Public address is not requested by client")
        if self.tunnel_type != TunnelType.HTTP and ':' not in self.address_public:
            self.update_public_url_port()
            raise ValueError("Tunnel is using a random port, but it has not been assigned yet. Please try again later")
        return self.address_public

    def update_public_url_port(self):
        response = self.lokal.rest.get(f"/api/tunnel/info/{self.id}")
        data = response.json()

        if not data.get('success'):
            raise ValueError(data.get('message', 'Could not get tunnel info'))

        if ':' not in data['data'][0]['address_public']:
            raise ValueError("Could not get assigned port")

        self.address_public = data['data'][0]['address_public']

    def print_startup_banner(self):
        if not self.startup_banner:
            return

        banner = """
    __       _         _             
   / /  ___ | | ____ _| |  ___  ___  
  / /  / _ \| |/ / _  | | / __|/ _ \ 
 / /__| (_) |   < (_| | |_\__ \ (_) |
 \____/\___/|_|\_\__,_|_(_)___/\___/ """

        colors = [Fore.MAGENTA, Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.RED]
        chosen_color = random.choice(colors)
        print(chosen_color + Style.BRIGHT + banner + Style.RESET_ALL)
        print()

        print(f"{Fore.RED}Minimum Lokal Client\t{Style.RESET_ALL}{SERVER_MIN_VERSION}")
        try:
            print(f"{Fore.CYAN}Public Address\t\t{Style.RESET_ALL}https://{self.get_public_address()}")
        except ValueError:
            pass
        try:
            print(f"{Fore.GREEN}LAN Address\t\t{Style.RESET_ALL}https://{self.get_lan_address()}")
        except ValueError:
            pass
        print()

class Lokal:
    def __init__(self):
        self.base_url = "http://127.0.0.1:6174"
        self.rest = requests.Session()
        self.rest.headers.update({
            "User-Agent": "Lokal Python - github.com/lokal-so/lokal-python"
        })

    def set_base_url(self, url: str):
        self.base_url = url
        return self

    def set_basic_auth(self, username: str, password: str):
        self.rest.auth = (username, password)
        return self

    def set_api_token(self, token: str):
        self.rest.headers.update({"X-Auth-Token": token})
        return self

    def new_tunnel(self) -> Tunnel:
        return Tunnel(self)

    def request(self, method, url, **kwargs):
        response = self.rest.request(method, f"{self.base_url}{url}", **kwargs)
        server_version = response.headers.get('Lokal-Server-Version')
        
        if server_version:
            if version.parse(server_version) < version.parse(SERVER_MIN_VERSION):
                raise ValueError(f"Your local client is outdated, please update to minimum version {SERVER_MIN_VERSION}")
        else:
            raise ValueError("Your local client might be outdated, please update")

        response.raise_for_status()
        return response

def new_default() -> Lokal:
    return Lokal()
