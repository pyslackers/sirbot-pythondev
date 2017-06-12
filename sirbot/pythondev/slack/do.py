DIGITAL_OCEAN_REFFERRAL_URL = 'https://m.do.co/c/457f0988c477'
DIGITAL_OCEAN_URL = 'https://digitalocean.com'

DIGITAL_OCEAN_TEXT = '''Here at Python Developers we host our website and
Slack bot on <{}|Digital Ocean>. If you are planning on using Digital Ocean,
please use our <{}|referral code>. You get 10 USD, while helping support the
 community by contributing to hosting fees for our site and @sirbotalot!
 '''.format(DIGITAL_OCEAN_URL, DIGITAL_OCEAN_REFFERRAL_URL)


def add_to_slack(slack):
    slack.add_command('/do', func=share_digital_ocean, public=True)


async def share_digital_ocean(command, slack, facades):
    response = command.response()
    response.text = DIGITAL_OCEAN_TEXT
    await slack.send(response)
