# NordVPN python interface on macOS

An unofficial python interface to handle [NordVPN](https://nordvpn.com) connection on macOS.

## Getting Started

### NordVPN credentials 
Retrieve your NordVPN credentials for manual configuration from [here](https://my.nordaccount.com/dashboard/nordvpn/manual-configuration/)
and place those in a file `.nordvpn-credentials` located at `path-to-credentials/.nordvpn-credentials`:
```text
nordvpn-username
nordvpn-password
```

### Set up python environment

After cloning the repository on your local machine with 
```shell
git clone https://github.com/niccolozanotti/ -b master
```
create a local python environment `.venv` and activate it:
```shell
python3 -m venv .venv
source .venv/bin/activate
```
Install python dependency [requests](https://docs.python-requests.org/en/latest/):
```shell
pip3 install requests
```
### Run

As an example, if you want to connect to the fastest server (determined by NordVPN) in 
the country `'Country'` you can run
```shell
# openvpn requires admin privilege
sudo python3 nordvpn_cli.py connect path-to-credentials/.nordvpn-credentials 'Country'
```
For instance, if you placed your credentials in your root User folder run:
```shell
# If no Country is specified the system defaults to the US
sudo python3 nordvpn_cli.py connect ~/.nordvpn-credentials 
```
in which case a possible output of successful connection might be
```shell
NordVPN is disconnected
Connected to us6497.nordvpn.com.tcp
{
  "ip": "89.187.178.35",
  "hostname": "unn-89-187-178-35.cdn77.com",
  "city": "New York City",
  "region": "New York",
  "country": "US",
  "loc": "40.7143,-74.0060",
  "org": "AS60068 Datacamp Limited",
  "postal": "10001",
  "timezone": "America/New_York",
  "readme": "https://ipinfo.io/missingauth"
}
```
To disconnect simply run:
```shell
sudo python3 nordvpn_cli.py disconnect 
```
giving the output
```shell
NordVPN is disconnected
```
