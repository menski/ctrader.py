# ctrader.py

ctrader.py is a Python client to answer [captcha.trader](http://www.captchatrader.com) captchas.

## Usage
	usage: ctrader.py [-h] [-u USERNAME] [-p PASSWORD] [-c CONFIG]

	Answer captchas from www.captchatrader.com

	optional arguments:
		-h, --help            show this help message and exit
		-u USERNAME, --username USERNAME
		-p PASSWORD, --password PASSWORD
		-c CONFIG, --config CONFIG

## Configurtion
If you want to save the login credentials create a file (default: `~/.ctrader`) with the following content:

	[user]
	username=USERNAME
	password=PASSWORD or PASSKEY

Your passkey is visible on your [account page](http://www.captchatrader.com/account/).

## Input
If you not provide any commandline options and no configuration file exists the programm will ask you for your credentials.

	Username: heinz
	Password/Passkey: 

## Multi-user support
If want to use multiple accounts you can configure all accounts in the configuration file. The Implementation uses a process per user.

	[user1]
	username=USERNAME1
	password=PASSWORD1 or PASSKEY1
	[user2]
	username=USERNAME2
	password=PASSWORD2 or PASSKEY2
	...
	[userX]
	username=USERNAMEX
	password=PASSWORDX or PASSKEYX
