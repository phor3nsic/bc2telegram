import requests
import time
import base64
import argparse
import sys
import os

banner = """
BC2Telegram
===========
by: @ricardo_iramar
python code: @phor3nsic_br
"""

def send_message(user_id, token, message):
	url = "https://api.telegram.org/"
	requests.get(url+f"bot{token}/sendMessage?chat_id={user_id}&text={message}&parse_mode=markdown")

def get_date(time):
	date_request = os.popen(f"echo {time} | date").read()
	date_request = date_request.replace(" -03","")
	return(date_request)

def check_black_list(ip):
	black_list = open("blacklist.txt").readlines()
	if ip in black_list:
		return False
	else:
		return True

def generate_message_http(domain, request, res, origin, date):
	message = f"""
Interaction HTTP Detected!
==========================
> Domain:   `{domain}`
> Request:
`{base64.b64decode(request).decode("utf-8")}`
> Response:
`{base64.b64decode(res).decode("utf-8")}`
> Origin: `{origin}`
> Date: `{date}`
"""
	return message

def generate_message_dns(domain, subdomain, origin, date):
	message = f"""
Interaction DNS Detected!
=========================
> Domain:   `{domain}`
> Subdomain: `{subdomain}`
> Origin: `{origin}`
> Date: `{date}`
"""
	return message

def logs(msg,output):
	arq = open(output,"a+")
	arq.write(msg+"\n\n")
	arq.close()

def check(burp_token, user_id, token, output):
	burp_token = burp_token.replace("+","%2b")
	burp_token = burp_token.replace("=","%3d")
	url = f"https://polling.burpcollaborator.net/burpresults?biid={burp_token}"
	req = requests.get(url)
	resp = req.json()
	
	if req.text != "{}":
		response = resp["responses"]
		for x in response:
			protocol = x["protocol"]
			if protocol == "http":
				domain = x["interactionString"]+".burpcollaborator.net"
				request = x["data"]["request"].encode('ascii')
				res = x["data"]["response"].encode('ascii')
				origin = x["client"]
				if check_black_list(origin) == True:
					date = get_date(int(x["time"]))
					send_message(user_id, token, generate_message_http(domain, request, res, origin,date))
					logs(generate_message_http(domain, request, res, origin,date),output)

			if protocol == "dns":
				domain = x["interactionString"]+".burpcollaborator.net"
				subdomain = x["data"]["subDomain"]
				origin = x["client"]
				if check_black_list(origin) == True:
					date = get_date(int(x["time"]))
					send_message(user_id, token, generate_message_dns(domain, subdomain, origin,date))
					logs(generate_message_dns(domain, subdomain, origin,date),output)


def main(biid, chat_id, bot_token, output):
	try:
		while True:
			check(biid, chat_id, bot_token, output)
			time.sleep(2)
	except KeyboardInterrupt:
		sys.exit()

if __name__ == '__main__':

	print(banner)
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("-b", "--biid", required=True, help="Token Burp")
	parser.add_argument("-c", "--chat_id", required=True, help="Chat Id of Telegram")
	parser.add_argument("-t", "--bot_token", required=True, help="Token of Bot")
	parser.add_argument("-l", "--logs", required=True, help="Log output")
	args = parser.parse_args()
	main(args.biid, args.chat_id, args.bot_token, args.logs)
