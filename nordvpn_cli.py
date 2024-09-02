import subprocess
import json
import os
import time
import requests
from typing import Optional


def print_error(message: str) -> None:
    # print out the message in red color
    print(f"\033[31m{message}\033[0m", file=sys.stderr)


def print_green(message: str) -> None:
    print(f"\033[32m{message}\033[0m")


def check_command(command: str) -> bool:
    return subprocess.call(["command", "-v", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def public_ip() -> str:
    return requests.get("https://ipinfo.io").text


def get_nordvpn_server(country_name: str = "United States") -> Optional[str]:
    country_id_map = {
        "albania": 2, "algeria": 3, "andorra": 5, "argentina": 10, "armenia": 11,
        "australia": 13, "austria": 14, "azerbaijan": 15, "bahamas": 16, "bangladesh": 18,
        "belgium": 21, "belize": 22, "bermuda": 24, "bhutan": 25, "bolivia": 26,
        "bosnia and herzegovina": 27, "brazil": 30, "brunei": 32, "bulgaria": 33,
        "cambodia": 36, "canada": 38, "cayman islands": 40, "chile": 43, "colombia": 47,
        "costa rica": 52, "croatia": 54, "cyprus": 56, "czech republic": 57,
        "denmark": 58, "dominican republic": 61, "ecuador": 63, "egypt": 64,
        "el salvador": 65, "estonia": 68, "finland": 73, "france": 74, "georgia": 80,
        "germany": 81, "ghana": 82, "greece": 84, "greenland": 85, "guam": 88,
        "guatemala": 89, "honduras": 96, "hong kong": 97, "hungary": 98, "iceland": 99,
        "india": 100, "indonesia": 101, "ireland": 104, "isle of man": 243, "israel": 105,
        "italy": 106, "jamaica": 107, "japan": 108, "jersey": 244, "kazakhstan": 110,
        "kenya": 111, "laos": 118, "latvia": 119, "lebanon": 120, "liechtenstein": 124,
        "lithuania": 125, "luxembourg": 126, "malaysia": 131, "malta": 134, "mexico": 140,
        "moldova": 142, "monaco": 143, "mongolia": 144, "montenegro": 146, "morocco": 147,
        "myanmar": 149, "nepal": 152, "netherlands": 153, "new zealand": 156, "nigeria": 159,
        "north macedonia": 128, "norway": 163, "pakistan": 165, "panama": 168,
        "papua new guinea": 169, "paraguay": 170, "peru": 171, "philippines": 172,
        "poland": 174, "portugal": 175, "puerto rico": 176, "romania": 179, "serbia": 192,
        "singapore": 195, "slovakia": 196, "slovenia": 197, "south africa": 200,
        "south korea": 114, "spain": 202, "sri lanka": 203, "sweden": 208,
        "switzerland": 209, "thailand": 214, "trinidad and tobago": 218, "turkey": 220,
        "ukraine": 225, "united arab emirates": 226, "united kingdom": 227,
        "united states": 228, "uruguay": 230, "uzbekistan": 231, "venezuela": 233,
        "vietnam": 234
    }

    for cmd in ["curl", "jq", "tr"]:
        if not check_command(cmd):
            print_error(f"{cmd} not found. Install it with `brew install {cmd}`")
            return None

    country_id = country_id_map.get(country_name.lower())
    if country_id is None:
        print_error("Warning: use the server from the closest location/country")
        return None

    url = f"https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&filters={{\"country_id\":{country_id}}}"
    response = requests.get(url)
    if response.status_code != 200:
        print_error(f"Failed to get server recommendations: HTTP {response.status_code}")
        return None

    try:
        server_name = response.json()[0]["hostname"]
    except (json.JSONDecodeError, IndexError, KeyError):
        print_error(f"Server name not found for {country_name}")
        return None

    return f"{server_name}.tcp"


def connect_nordvpn(cred_file_path: str, country_name: str = "United States") -> None:
    disconnect_nordvpn()

    for cmd in ["openvpn", "mkdir", "unzip", "rm", "sleep"]:
        if not check_command(cmd):
            print_error(f"{cmd} not found. Install it with `brew install {cmd}`")
            return

    if not os.path.isfile(cred_file_path):
        print_error("Cred file not found")
        return

    server_name = get_nordvpn_server(country_name)
    if not server_name:
        return

    if not os.path.isdir("/etc/nordvpn_file"):
        os.makedirs("/etc/nordvpn_file", exist_ok=True)
        subprocess.run(["curl", "-fsSL", "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip", "-o",
                        "/etc/nordvpn_file/ovpn.zip"], check=True)
        subprocess.run(["unzip", "-qq", "/etc/nordvpn_file/ovpn.zip", "-d", "/etc/nordvpn_file/"], check=True)
        os.remove("/etc/nordvpn_file/ovpn.zip")
        subprocess.run(["rm", "-rf", "/etc/nordvpn_file/ovpn_udp/"], check=True)

    ovpn_file = f"/etc/nordvpn_file/ovpn_tcp/{server_name}.ovpn"
    if not os.path.isfile(ovpn_file):
        print_error(f"{ovpn_file} not found")
        return

    try:
        subprocess.run(["sudo", "openvpn", "--config", ovpn_file, "--auth-user-pass", cred_file_path, "--daemon"],
                       check=True)
        print_green(f"Connected to {server_name}")
        time.sleep(5)
        print_green(public_ip())
    except subprocess.CalledProcessError:
        print_error(f"Cannot connect to {server_name}")


def disconnect_nordvpn() -> None:
    if not check_command("pkill"):
        print_error("pkill not found. Install it with `brew install proctools`")
        return

    try:
        subprocess.run(["sudo", "pkill", "openvpn"], check=True)
        print_green("NordVPN is disconnected")
    except subprocess.CalledProcessError:
        print_error("NordVPN is not disconnected")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python script.py [connect|disconnect] [cred_file_path] [country_name]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "connect":
        if len(sys.argv) < 3:
            print("Usage: python script.py connect cred_file_path [country_name]")
            sys.exit(1)
        cred_file_path = sys.argv[2]
        country_name = sys.argv[3] if len(sys.argv) > 3 else "United States"
        connect_nordvpn(cred_file_path, country_name)
    elif action == "disconnect":
        disconnect_nordvpn()
    else:
        print("Invalid action. Use 'connect' or 'disconnect'.")
        sys.exit(1)
