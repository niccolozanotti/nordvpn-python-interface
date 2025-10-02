import subprocess
import json
import os
import sys
import time
import requests
import random
import glob
from typing import Optional


def print_error(message: str) -> None:
    # print out the message in red color
    print(f"\033[31m{message}\033[0m", file=sys.stderr)


def print_green(message: str) -> None:
    print(f"\033[32m{message}\033[0m")


def check_command(command: str) -> bool:
    return subprocess.call(["command", "-v", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def public_ip() -> str:
    try:
        response = requests.get("https://ipinfo.io")
        if response.status_code == 200:
            data = response.json()
            # Format the IP information in a cleaner way
            ip_info = f"IP: {data.get('ip', 'Unknown')}"
            if 'city' in data and 'region' in data:
                ip_info += f" | Location: {data['city']}, {data['region']}"
            if 'country' in data:
                ip_info += f" | Country: {data['country']}"
            if 'org' in data:
                ip_info += f" | ISP: {data['org']}"
            return ip_info
        else:
            return f"Failed to get IP info (HTTP {response.status_code})"
    except Exception as e:
        return f"Error fetching IP info: {e}"


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

    # Since the API endpoint is returning 403, use a fallback approach
    # Randomly select from available servers in the specified country
    
    # Map country names to their 2-letter country codes for file matching
    country_code_map = {
        "united states": "us",
        "united kingdom": "uk", 
        "germany": "de",
        "france": "fr",
        "canada": "ca",
        "australia": "au",
        "japan": "jp",
        "netherlands": "nl",
        "sweden": "se",
        "norway": "no",
        "switzerland": "ch",
        "singapore": "sg",
        "brazil": "br",
        "mexico": "mx",
        "spain": "es",
        "italy": "it",
        "poland": "pl",
        "czech republic": "cz",
        "finland": "fi",
        "denmark": "dk",
        "belgium": "be",
        "austria": "at",
        "portugal": "pt",
        "ireland": "ie",
        "new zealand": "nz",
        "south korea": "kr",
        "hong kong": "hk",
        "india": "in",
        "south africa": "za",
        "turkey": "tr",
        "israel": "il",
        "ukraine": "ua",
        "romania": "ro",
        "bulgaria": "bg",
        "croatia": "hr",
        "slovenia": "si",
        "slovakia": "sk",
        "hungary": "hu",
        "latvia": "lv",
        "lithuania": "lt",
        "estonia": "ee",
        "greece": "gr",
        "cyprus": "cy",
        "malta": "mt",
        "luxembourg": "lu",
        "iceland": "is"
    }
    
    country_code = country_code_map.get(country_name.lower())
    if country_code is None:
        print_error(f"Country '{country_name}' not supported. Using default US server.")
        country_code = "us"
    
    # Find all available servers for this country
    nordvpn_dir = os.path.expanduser("~/.nordvpn_configs/ovpn_tcp")
    pattern = f"{nordvpn_dir}/{country_code}*.nordvpn.com.tcp.ovpn"
    available_servers = glob.glob(pattern)
    
    if not available_servers:
        print_error(f"No servers found for {country_name}. Using default US server.")
        # Fallback to US servers
        pattern = f"{nordvpn_dir}/us*.nordvpn.com.tcp.ovpn"
        available_servers = glob.glob(pattern)
        if not available_servers:
            print_error("No US servers found either. Please check your NordVPN config files.")
            return None
    
    # Randomly select a server
    selected_server = random.choice(available_servers)
    server_name = os.path.basename(selected_server).replace('.nordvpn.com.tcp.ovpn', '')
    
    return f"{server_name}.nordvpn.com.tcp"


def connect_nordvpn(cred_file_path: str, country_name: str = "United States") -> None:
    disconnect_nordvpn(quiet=True)

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

    # Use a local directory instead of /etc to avoid permission issues
    nordvpn_dir = os.path.expanduser("~/.nordvpn_configs")
    if not os.path.isdir(nordvpn_dir):
        os.makedirs(nordvpn_dir, exist_ok=True)
        subprocess.run(["curl", "-fsSL", "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip", "-o",
                        f"{nordvpn_dir}/ovpn.zip"], check=True)
        subprocess.run(["unzip", "-qq", f"{nordvpn_dir}/ovpn.zip", "-d", nordvpn_dir], check=True)
        os.remove(f"{nordvpn_dir}/ovpn.zip")
        subprocess.run(["rm", "-rf", f"{nordvpn_dir}/ovpn_udp/"], check=True)

    ovpn_file = f"{nordvpn_dir}/ovpn_tcp/{server_name}.ovpn"
    if not os.path.isfile(ovpn_file):
        print_error(f"{ovpn_file} not found")
        return

    try:
        subprocess.run(["sudo", "openvpn", "--config", ovpn_file, "--auth-user-pass", cred_file_path, "--daemon"],
                       check=True)
        print_green(f"Connected to {server_name}")
        print("Waiting for connection to stabilize...")
        time.sleep(5)
        print("Fetching your new IP address...")
        print_green(public_ip())
    except subprocess.CalledProcessError:
        print_error(f"Cannot connect to {server_name}")


def disconnect_nordvpn(quiet: bool = False) -> None:
    if not check_command("pkill"):
        print_error("pkill not found. Install it with `brew install proctools`")
        return

    # Check if any openvpn process is running before attempting to disconnect
    try:
        result = subprocess.run(
            ["pgrep", "-x", "openvpn"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            if not quiet:
                print_green("No active VPN connection found.")
            return
    except Exception as e:
        print_error(f"Error checking openvpn process: {e}")
        return

    try:
        subprocess.run(["sudo", "pkill", "openvpn"], check=True)
        print_green("NordVPN is disconnected.")
    except subprocess.CalledProcessError:
        # If pkill fails, check again if openvpn is still running
        try:
            result = subprocess.run(
                ["pgrep", "-x", "openvpn"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0 or not result.stdout.strip():
                if not quiet:
                    print_green("No active VPN connection found.")
                pass
            else:
                print_error("Failed to disconnect NordVPN. openvpn process may still be running.")
        except Exception as e:
            print_error(f"Error verifying openvpn process after disconnect attempt: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python script.py [connect|disconnect] [cred_file_path] [country_name]")
        print("Note: If no country is specified, defaults to 'United States'")
        sys.exit(1)

    action = sys.argv[1]
    if action == "connect":
        if len(sys.argv) < 3:
            print("Usage: python script.py connect cred_file_path [country_name]")
            print("Note: If no country is specified, defaults to 'United States'")
            sys.exit(1)
        cred_file_path = sys.argv[2]
        # Default to United States if no country is provided
        country_name = sys.argv[3] if len(sys.argv) > 3 else "United States"
        print(f"Connecting to NordVPN server in: {country_name}")
        connect_nordvpn(cred_file_path, country_name)
    elif action == "disconnect":
        disconnect_nordvpn()
    else:
        print("Invalid action. Use 'connect' or 'disconnect'.")
        sys.exit(1)
