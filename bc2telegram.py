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
	date_request = os.popen(f"echo {time} | TZ=\"America/Sao_Paulo\" date").read()
	date_request = date_request.replace(" -03","")
	return(date_request)

def check_black_list(ip):
	file = open("blacklist.txt").readlines()
	blacklist = []
	for x in file:
		x = x.replace("\n","")
		blacklist.append(x) 

	if ip not in blacklist:
		return True
		
def generate_message_http(request, res, origin, date):
	message = f"""
👀 Interaction HTTP Detected!
==========================
> Request:
`{request}`
> Response:
`{res}`
> Origin: `{origin}`
> Date: `{date}`
"""
	return message

def generate_message_dns(domain, origin, date):
	message = f"""
👀 Interaction DNS Detected!
=========================
> Domain:   `{domain}`
> Origin: `{origin}`
> Date: `{date}`
"""
	return message

def logs(msg,output):
	arq = open(output,"a+")
	arq.write(msg+"\n\n")
	arq.close()

def check(burp_token, user_id, token, output, polling):
	burp_token = burp_token.replace("+","%2b")
	burp_token = burp_token.replace("=","%3d")
	url = f"{polling}/burpresults?biid={burp_token}"
	try:
		req = requests.get(url)
		resp = req.json()
	except:
		req.text = "{}"
	
	if req.text != "{}":
		response = resp["responses"]
		for x in response:
			protocol = x["protocol"]
			if protocol == "http":
				request = base64.b64decode(x["data"]["request"]).decode()
				res = base64.b64decode(x["data"]["response"]).decode()
				origin = str(x["client"])
				
				if check_black_list(origin) == True:
					date = get_date(int(x["time"]))
					print(generate_message_http(request, res, origin,date))
					send_message(user_id, token, generate_message_http(request, res, origin,date))
					logs(generate_message_http(request, res, origin,date),output)
				

			if protocol == "dns":
				domain = x["data"]["subDomain"]
				origin = x["client"]

				if check_black_list(origin) == True:
					date = get_date(int(x["time"]))
					print(generate_message_dns(domain, origin,date))
					send_message(user_id, token, generate_message_dns(domain, origin,date))
					logs(generate_message_dns(domain, origin,date),output)
			


def main(biid, chat_id, bot_token, output, polling):
	try:
		while True:
			check(biid, chat_id, bot_token, output, polling)
			time.sleep(5)
	except KeyboardInterrupt:
		sys.exit()

if __name__ == '__main__':

	print(banner)
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("-b", "--biid", required=True, help="Token Burp")
	parser.add_argument("-c", "--chat_id", required=True, help="Chat Id of Telegram")
	parser.add_argument("-t", "--bot_token", required=True, help="Token of Bot")
	parser.add_argument("-l", "--logs", required=True, help="Log output")
	parser.add_argument("-p", "--polling", required=False, help="Burp pooling", default="https://polling.burpcollaborator.net")
	args = parser.parse_args()

	main(args.biid, args.chat_id, args.bot_token, args.logs, args.polling)
