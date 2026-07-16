#Join my telegram channel @FREXY_OFC
import sys
import time
import json
import re
import socket
import base64
import binascii
import threading
import pickle
import random
import urllib3
import asyncio
import http.client
import ssl
import gzip
from io import BytesIO
from threading import Thread
from datetime import datetime

# =========================
# Third-party Libraries
# =========================
import requests
import psutil
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from google.protobuf.timestamp_pb2 import Timestamp
from protobuf_decoder.protobuf_decoder import Parser

# =========================
# Project Modules
# =========================
import xKEys
from byte import xSendTeamMsg, Auth_Chat
from byte import *
from Z0B4Y4R import * 

# =========================
# Disable warnings
# =========================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

connected_clients = {}
connected_clients_lock = threading.Lock()

app = Flask(__name__)
CORS(app)

API_KEY = "FREXY"

class SimpleAPI:
    def __init__(self):
        self.running = True
        self.team_data_cache = {}
        
    def validate_api_key(self, api_key):
        return api_key == API_KEY
        
    def process_ghost_command(self, teamcode, name):
        try:
            if not ChEck_Commande(teamcode):
                return {"status": "error", "message": "TeamCode Is Wrong ⚠️"}
            
            results = []
            
            with connected_clients_lock:
                if not connected_clients:
                    return {"status": "error", "message": "The Account Not Online❌"}
                
                clients_list = list(connected_clients.values())
                
                if len(clients_list) < 3:
                    return {"status": "error", "message": f"You Need 3 Accounts In File accs.txt To Start⚠️"}
                
                master_client = clients_list[0]
                team_data_result = self.get_team_data(master_client, teamcode)
                
                if not team_data_result["success"]:
                    return {"status": "error", "message": f"Error To Get Info Sq"}
                
                team_id = team_data_result["team_id"]
                sq_value = team_data_result["sq"]
                
                results.append({
                    "message": f"Done To Get Info Sq ✅ ID={team_id}, SQ={sq_value}"
                })
                
                ghost_clients = clients_list[:3]
                success_count = 0
                threads = []
                
                for i, client in enumerate(ghost_clients, 1):
                    thread = threading.Thread(target=self.execute_ghost_command_api, 
                                            args=(client, team_id, name, sq_value, i, results))
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join(timeout=10)
                
                for result in results:
                    if result.get("status") == "success":
                        success_count += 1
                
                return {
                    "message": f"Done Sent Ghosts ✅"
                }
                    
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
    
    def get_team_data(self, client, teamcode):
        try:
            if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
                
                join_packet = JoinTeamCode(teamcode, client.key, client.iv)
                client.CliEnts2.send(join_packet)
                
                start_time = time.time()
                response_received = False
                
                while time.time() - start_time < 8:
                    try:
                        if hasattr(client, 'DaTa2') and client.DaTa2 and len(client.DaTa2.hex()) > 30:
                            hex_data = client.DaTa2.hex()
                            if '0500' in hex_data[0:4]:
                                try:
                                    if "08" in hex_data:
                                        decoded_data = DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}')
                                    else:
                                        decoded_data = DeCode_PackEt(hex_data[10:])
                                    
                                    dT = json.loads(decoded_data)
                                    
                                    if "5" in dT and "data" in dT["5"]:
                                        team_data = dT["5"]["data"]
                                        
                                        if "31" in team_data and "data" in team_data["31"]:
                                            sq = team_data["31"]["data"]
                                            idT = team_data["1"]["data"]
                                            
                                            client.CliEnts2.send(ExitBot('000000', client.key, client.iv))
                                            time.sleep(0.2)
                                            
                                            return {
                                                "success": True,
                                                "team_id": idT,
                                                "sq": sq
                                            }
                                        
                                except Exception as decode_error:
                                    pass
                        
                        time.sleep(0.1)
                        
                    except Exception as loop_error:
                        time.sleep(0.1)
                
                return {"success": False, "message": "Timeout without receiving a valid response"}
                
            else:
                return {"success": False, "message": "Client is not properly connected"}
                
        except Exception as e:
            return {"success": False, "message": f"An error occurred: {str(e)}"}
    
    def execute_ghost_command_api(self, client, team_id, name, sq_value, client_number, results):
        try:
            result = {"account_number": client_number, "account_id": client.id, "status": "processing"}
            
            if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
                
                ghost_packet = GhostPakcet(team_id, name, sq_value, client.key, client.iv)
                client.CliEnts2.send(ghost_packet)
                time.sleep(0.5)
                
                result["status"] = "success"
                result["message"] = f""
                
            else:
                result["status"] = "error"
                result["message"] = "Client is not properly connected"
                
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"An error occurred while executing command: {str(e)}"
            
        results.append(result)

api_handler = SimpleAPI()

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Request successful by ghost hbb",
        "endpoints": {
            "/ghost?teamcode=CODE&name=NAME&api_key=KEY"
        }
    })

@app.route('/ghost')
def ghost():
    teamcode = request.args.get('teamcode')
    name = request.args.get('name')
    api_key = request.args.get('api_key')
    
    if not api_key:
        return jsonify({"status": "error", "message": "Error In Api Key⚠️"}), 401
        
    if not api_handler.validate_api_key(api_key):
        return jsonify({"status": "error", "message": "Error In Api Key⚠️"}), 401
        
    if not teamcode or not name:
        return jsonify({"status": "error", "message": "Please enter teamcode and name"}), 400
        
    result = api_handler.process_ghost_command(teamcode, name)
    return jsonify(result)

def run_flask_api():
    print("Starting API Server...")
    app.run(host='0.0.0.0', port=6002, debug=False)

def generate_random_color():
    color_list = [
        "[00FF00][b][c]", "[FFDD00][b][c]", "[3813F3][b][c]", "[FF0000][b][c]",
        "[0000FF][b][c]", "[FFA500][b][c]", "[DF07F8][b][c]", "[11EAFD][b][c]",
        "[DCE775][b][c]", "[A8E6CF][b][c]", "[7CB342][b][c]", "[FF0000][b][c]",
        "[FFB300][b][c]", "[90EE90][b][c]", "[FF4500][b][c]", "[FFD700][b][c]",
        "[32CD32][b][c]", "[87CEEB][b][c]", "[9370DB][b][c]", "[FF69B4][b][c]",
        "[8A2BE2][b][c]", "[00BFFF][b][c]", "[1E90FF][b][c]", "[20B2AA][b][c]",
        "[00FA9A][b][c]", "[008000][b][c]", "[FFFF00][b][c]", "[FF8C00][b][c]",
        "[DC143C][b][c]", "[FF6347][b][c]", "[FFA07A][b][c]", "[FFDAB9][b][c]",
        "[CD853F][b][c]", "[D2691E][b][c]", "[BC8F8F][b][c]", "[F0E68C][b][c]",
        "[556B2F][b][c]", "[808000][b][c]", "[4682B4][b][c]", "[6A5ACD][b][c]",
        "[7B68EE][b][c]", "[8B4513][b][c]", "[C71585][b][c]", "[4B0082][b][c]",
        "[B22222][b][c]", "[228B22][b][c]", "[8B008B][b][c]", "[483D8B][b][c]",
        "[556B2F][b][c]", "[800000][b][c]", "[008000][b][c]", "[000080][b][c]",
        "[800080][b][c]", "[808080][b][c]", "[A9A9A9][b][c]", "[D3D3D3][b][c]",
        "[F0F0F0][b][c]"
    ]
    return random.choice(color_list)

def AuTo_ResTartinG():
    time.sleep(6 * 60 * 60)
    print('Bot restarted successfully!')
    p = psutil.Process(os.getpid())
    for handler in p.open_files():
        try: os.close(handler.fd)
        except Exception as e: print(f" - Error Close Files : {e}")
    for conn in p.net_connections():
        try:
            if hasattr(conn, 'fd'): os.close(conn.fd)
        except Exception as e: print(f" - Error Close Connection : {e}")
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)
       
def ResTarT_BoT():
    print(' - An error occurred, restarting to fix it ')
    p = psutil.Process(os.getpid())
    open_files = p.open_files()
    connections = p.net_connections()
    for handler in open_files:
        try: os.close(handler.fd)
        except Exception: pass           
    for conn in connections:
        try: conn.close()
        except Exception: pass
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)

def GeT_Time(timestamp):
    last_login = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = now - last_login   
    d = diff.days
    h , rem = divmod(diff.seconds, 3600)
    m , s = divmod(rem, 60)    
    return d, h, m, s

def Time_En_Ar(t): 
    return ' '.join(t.split(" - "))
    
Thread(target = AuTo_ResTartinG , daemon = True).start()

ACCOUNTS = []

def load_accounts_from_file(filename="accs.txt"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            account_id = parts[0].strip()
                            password = parts[1].strip()
                            accounts.append({'id': account_id, 'password': password})
                    else:
                        accounts.append({'id': line.strip(), 'password': ''})
        print(f"Loaded {len(accounts)} accounts from {filename}")
    except FileNotFoundError:
        print(f"File {filename} not found!")
    except Exception as e:
        print(f"Error occurred while reading the file: {e}")
    
    return accounts

ACCOUNTS = load_accounts_from_file()

if not ACCOUNTS:
    ACCOUNTS = [{'id': '4567974375', 'password': 'D5M_ZenithQSLYAR9XMxxxx'}]
            
class FF_CLient():

    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.DaTa2 = None
        self.Get_FiNal_ToKen_0115()     
            
    def Connect_SerVer_OnLine(self , Token , tok , host , port , key , iv , host2 , port2):
        try:
            self.AutH_ToKen_0115 = tok    
            self.CliEnts2 = socket.create_connection((host2 , int(port2)))
            self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))                  
        except Exception as e:
            print(f"Error connecting to secondary server: {e}")
            return
        
        while True:
            try:
                self.DaTa2 = self.CliEnts2.recv(99999)
                if self.DaTa2 and len(self.DaTa2) > 0:
                    hex_data = self.DaTa2.hex()
                    if '0500' in hex_data[0:4] and len(hex_data) > 30:	         	    	    
                        try:
                            self.packet = json.loads(DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}'))
                            if '5' in self.packet and 'data' in self.packet['5']:
                                self.AutH = self.packet['5']['data']['7']['data']
                                print(f"Account {self.id}: Authentication data updated")
                        except Exception as decode_error:
                            print(f"Error decoding packet: {decode_error}")
                    
            except Exception as e:
                print(f"Error receiving data: {e}")
                time.sleep(1)
                                
    def Connect_SerVer(self , Token , tok , host , port , key , iv , host2 , port2):
        self.AutH_ToKen_0115 = tok    
        try:
            self.CliEnts = socket.create_connection((host , int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))  
            self.DaTa = self.CliEnts.recv(1024)
        except Exception as e:
            print(f"Error connecting to main server: {e}")
            time.sleep(5)
            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
            return
                
        threading.Thread(target=self.Connect_SerVer_OnLine, args=(Token , tok , host , port , key , iv , host2 , port2), daemon=True).start()
        self.Exemple = xMsGFixinG('12345678')
            
        self.key = key
        self.iv = iv
            
        with connected_clients_lock:
            connected_clients[self.id] = self
            print(f"Account {self.id} registered globally, total online: {len(connected_clients)}")
            
        while True:      
            try:
                self.DaTa = self.CliEnts.recv(1024)   
                if len(self.DaTa) == 0:	            		
                    try:            		    
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'): self.CliEnts2.close()
                        self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)                    		                    
                    except:
                        try:
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'): self.CliEnts2.close()
                            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                        except:
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'): self.CliEnts2.close()
                            ResTarT_BoT()	            
                                      
                if '1200' in self.DaTa.hex()[0:4] and 900 > len(self.DaTa.hex()) > 100:
                    if b"***" in self.DaTa:
                        self.DaTa = self.DaTa.replace(b"***", b"106")         
                    try:
                        self.BesTo_data = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))	       
                        self.input_msg = 'besto_love' if '8' in self.BesTo_data["5"]["data"] else self.BesTo_data["5"]["data"]["4"]["data"]
                    except: 
                        self.input_msg = None	   	 
                    self.DeCode_CliEnt_Uid = self.BesTo_data["5"]["data"]["1"]["data"]
                    self.CliEnt_Uid = EnC_Uid(self.DeCode_CliEnt_Uid , Tp = 'Uid')
                               
                if self.input_msg and 'besto_love' in self.input_msg[:10]:
                    self.CliEnts.send(GenResponsMsg(f'''@Telegram:@FREXY_OFC''', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))
                    time.sleep(0.3)
                    self.CliEnts.close()
                    if hasattr(self, 'CliEnts2'): self.CliEnts2.close()
                    self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)	                    	 	 
                                                               
                if self.input_msg and (b'@help ' in self.DaTa or b'@help' in self.DaTa or 'en' in self.input_msg[:2]):
                    self.result = ChEck_The_Uid(self.DeCode_CliEnt_Uid)
                    if self.result:
                        self.Status , self.Expire = self.result
                        self.CliEnts.send(GenResponsMsg(f'''@Telegram:@FREXY_OFC''', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))
                            
            except Exception as e:
                print(f"Error in main thread loop: {e}")
                try:
                    self.CliEnts.close()
                    if hasattr(self, 'CliEnts2'): self.CliEnts2.close()
                except: pass
                self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                                    
    def GeT_Key_Iv(self , serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp , key , iv = my_message.field21 , my_message.field22 , my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp , key , iv    

    def Guest_GeneRaTe(self , uid , password):
        self.url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        self.headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        self.dataa = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067",
        }
        try:
            self.response = requests.post(self.url, headers=self.headers, data=self.dataa, timeout=10).json()
            if 'access_token' in self.response and 'open_id' in self.response:
                self.Access_ToKen , self.Access_Uid = self.response['access_token'] , self.response['open_id']
                time.sleep(0.2)
                print(f'Starting Account: {uid}')
                return self.ToKen_GeneRaTe(self.Access_ToKen , self.Access_Uid)
            else:
                print(f" - Failed to get token from guest login: {self.response}")
                return None
        except Exception as e:
            print(f"Token generation error: {e}")
            ResTarT_BoT()    

    def ToKen_GeneRaTe(self , Access_ToKen , Access_Uid):
        try:
            self.PLaFTrom = "4"
            self.Version , self.V = '2024010012' , '1.126.2'

            self.PyL = {
                3: str(datetime.now())[:-7] ,
                4: "free fire",
                5: 2,
                7: self.V ,
                8: "Android OS 11 / API-30 (RQ3A.210805.001)",
                9: "Handheld",
                10: "Verizon",
                11: "WIFI",
                12: 1080,
                13: 2400,
                14: "440",
                15: "ARMv8",
                16: 6144,
                17: "Adreno (TM) 650",
                18: "OpenGL ES 3.2 V@1.50",
                19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57",
                20: "",
                21: "en",
                22: Access_Uid ,
                23: self.PLaFTrom,
                24: "Handheld",
                25: "google G011A", 
                29: Access_ToKen ,
                30: 3,
                41: "Verizon",
                42: "WIFI",
                57: "1ac4b80ecf0478a44203bf8fac6120f5",
                60: 32966,
                61: 29779,
                62: 2479,
                63: 914,
                64: 31176,
                65: 32966,
                66: 31176,
                67: 32966,
                70: 4,
                73: 2,
                74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
                76: 1,
                77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                78: 6,
                79: 1,
                81: "64",
                83: self.Version ,
                86: "OpenGLES3",
                87: 255,
                88: self.PLaFTrom,
                89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                90: "Phoenix",
                91: "AZ",
                92: 10214,
                93: "3rd_party",
                94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                95: 111207,
                97: 1,
                98: 1,
                99: f"{self.PLaFTrom}" ,
                100: f"{self.PLaFTrom}"
            }

            self.PyL = CrEaTe_ProTo(self.PyL).hex()        
            self.PaYload = bytes.fromhex(EnC_AEs(self.PyL))
            
            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=15)    
            headers = {
                'X-Unity-Version': '2018.4.11f1',
                'ReleaseVersion': 'OB54',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-GA': 'v1 1',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
                'Host': 'loginbp.ggpolarbear.com',
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip'}

            conn.request("POST", "/MajorLogin", body=self.PaYload, headers=headers)
            response = conn.getresponse()
            raw_data = response.read()
            if response.getheader('Content-Encoding') == 'gzip':
                with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                    raw_data = f.read()
                    
            if response.status not in [200, 201]:
                print("Failed to get token")
                sys.exit()

            self.BesTo_data = json.loads(DeCode_PackEt(raw_data.hex()))
            self.JwT_ToKen = self.BesTo_data['8']['data']           
            self.combined_timestamp , self.key , self.iv = self.GeT_Key_Iv(raw_data)
            
            ip , port , ip2 , port2 = self.GeT_LoGin_PorTs(self.JwT_ToKen , self.PaYload)            
            return self.JwT_ToKen , self.key , self.iv, self.combined_timestamp , ip , port , ip2 , port2
        except Exception as e:
            print(f"Error in ToKen_GeneRaTe: {e}")
            sys.exit()

    def GeT_LoGin_PorTs(self , JwT_ToKen , PayLoad):
        self.UrL = 'https://clientbp.common.ggbluefox.com/GetLoginData'
        self.HeadErs = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': 'clientbp.common.ggbluefox.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',
        }       
        try:
            self.Res = requests.post(self.UrL , headers=self.HeadErs , data=PayLoad , verify=False, timeout=15)
            decoded = DeCode_PackEt(self.Res.content.hex())
            if not decoded:
                print(" - Failed to decode response")
                return None, None, None, None

            self.BesTo_data = json.loads(decoded)  

            if '32' not in self.BesTo_data or '14' not in self.BesTo_data:
                print(f" - Missing port data in response: {self.BesTo_data.keys()}")
                return None, None, None, None

            address , address2 = self.BesTo_data['32']['data'] , self.BesTo_data['14']['data']

            try:
                ip , port = address.rsplit(":", 1)
                ip2 , port2 = address2.rsplit(":", 1)
                port = int(port)
                port2 = int(port2)
            except Exception as e:
                print(f" - Port parsing error: {e}")
                return None, None, None, None

            print(f" - Got ports: Chat={ip}:{port}, Game={ip2}:{port2}")
            return ip , port , ip2 , port2
        except requests.RequestException as e:
            print(f" - Bad Requests: {e}")
        except Exception as e:
            print(f" - Error getting ports: {e}")
        print(" - Failed To Get Ports!")
        return None, None, None, None
      
    def Get_FiNal_ToKen_0115(self):
        token_res = self.Guest_GeneRaTe(self.id , self.password)
        if not token_res:
            print(f" - Token generation failed for {self.id}")
            return None
            
        token , key , iv , Timestamp , ip , port , ip2 , port2 = token_res
        self.JwT_ToKen = token        
        try:
            self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
            self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
            self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
            self.HeX_VaLue = DecodE_HeX(Timestamp)
            self.TimE_HEx = self.HeX_VaLue
            self.JwT_ToKen_ = token.encode().hex()
        except Exception as e:
            print(f" - Error In Token : {e}")
            return
        try:
            self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
            length = len(self.EncoDed_AccounT)
            self.__ = '00000000'
            if length == 9: self.__ = '0000000'
            elif length == 8: self.__ = '00000000'
            elif length == 10: self.__ = '000000'
            elif length == 7: self.__ = '000000000'
            else:
                print('Unexpected length encountered')                
            self.Header = f'0115{self.__}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
            self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_ , key , iv)
        except Exception as e:
            print(f" - Error In Final Token : {e}")
        self.AutH_ToKen = self.FiNal_ToKen_0115
        self.Connect_SerVer(self.JwT_ToKen , self.AutH_ToKen , ip , port , key , iv , ip2 , port2)        
        return self.AutH_ToKen , key , iv

def start_account(account):
    try:
        print(f"Starting account: {account['id']}")
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        print(f"Error starting account {account['id']}: {e}")
        time.sleep(5)
        start_account(account)

def StarT_SerVer():
    api_thread = threading.Thread(target=run_flask_api, daemon=True)
    api_thread.start()
    
    threads = []
    
    for account in ACCOUNTS:
        thread = threading.Thread(target=start_account, args=(account,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(3)
    
    for thread in threads:
        thread.join()
  
if __name__ == '__main__':
    StarT_SerVer()
