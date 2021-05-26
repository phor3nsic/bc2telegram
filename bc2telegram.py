import requests
import time
import base64
import argparse

banner = """
BC2Telegram
===========
by: @ricardo_iramar
python code: @phor3nsic_br
"""
def send_message(user_id, token, message):
	url = "https://api.telegram.org/"
	requests.get(url+f"bot{token}/sendMessage?chat_id={user_id}&text={message}&parse_mode=markdown")

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
> Date: `{time.strftime("%H:%M %D", time.localtime(date))}`
"""
	return message

def generate_message_dns(domain, subdomain, origin, date):
	message = f"""
Interaction DNS Detected!
=========================
> Domain:   `{domain}`
> Subdomain: `{subdomain}`
> Origin: `{origin}`
> Date: `{time.strftime("%H:%M %D", time.localtime(date))}`
"""
	return message

def check(burp_token, user_id, token):
	url = f"https://polling.burpcollaborator.net/burpresults?biid={burp_token}"
	req = requests.get(url)
	resp = req.json()
	try:
		response = resp["responses"]
		for x in response:
			protocol = x["protocol"]
			if protocol == "http":
				domain = x["interactionString"]+".burpcollaborator.net"
				request = x["data"]["request"].encode('ascii')
				res = x["data"]["response"].encode('ascii')
				origin = x["client"]
				date = int(x["time"])
				send_message(user_id, token, generate_message_http(domain, request, res, origin,date))
			if protocol == "dns":
				domain = x["interactionString"]+".burpcollaborator.net"
				subdomain = x["data"]["subDomain"]
				origin = x["client"]
				date = int(x["time"])
				send_message(user_id, token, generate_message_dns(domain, subdomain, origin,date))
	except:
		pass

def main(btoken, chat_id, bot_token):
	
	while True:
		time.sleep(2)
		check(btoken, chat_id, bot_token)

if __name__ == '__main__':

	print(banner)
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("-bt", "--btoken", required=True, help="Token Burp")
	parser.add_argument("-cid", "--chad_id", required=True, help="Chat Id of Telegram")
	parser.add_argument("-bot", "--bot_token", required=True, help="Token of Bot")
	args = parser.parse_args()
	main(args.btoken, args.chat_id, args.bot_token)