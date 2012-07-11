# ctrader.py

ctrader.py is a Python client to answer [captcha.trader](http://www.captchatrader.com) captchas.

## Usage
	python ctrader.py [-u USERNAME] [-p PASSWORD] [-c CONFIG]

## Options	On the commandline you can provide:
- -u/--username: username
- -p/--password: password for user
- -c/--config: configuration file


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
