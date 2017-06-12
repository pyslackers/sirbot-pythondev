import re

from sirbot.slack.message import Attachment, Field

from . import candy, giphy, intro, pypi, files, admin, do


def add_to_slack(slack):
    slack.add_message('^help', help_, flags=re.IGNORECASE, mention=True)
    slack.add_message('tell (<(#|@)(?P<to_id>[A-Z0-9]*)(|.*)?>) (?P<item>.*)',
                      publish, flags=re.IGNORECASE, mention=True, admin=True)
    slack.add_message('hello', hello, mention=True, flags=re.IGNORECASE)

    candy.add_to_slack(slack)
    giphy.add_to_slack(slack)
    intro.add_to_slack(slack)
    pypi.add_to_slack(slack)
    files.add_to_slack(slack)
    admin.add_to_slack(slack)
    do.add_to_slack(slack)


async def hello(message, slack, *_):
    response = message.response()
    response.text = 'Hello'
    await slack.send(response)


async def publish(message, slack, _, match):
    response = message.response()

    to_id = match.group('to_id')
    item = match.group('item')

    if to_id.startswith('C'):
        to = await slack.channels.get(to_id)
        if to:
            response.text = item
            response.to = to
        else:
            response.text = 'Sorry I can not understand the destination.'
            response.to = response.frm
    elif to_id.startswith('U'):
        to = await slack.users.get(to_id, dm=True)
        if to:
            response.text = item
            response.to = to
        else:
            response.text = 'Sorry I can not understand the destination.'
            response.to = response.frm
    else:
        response.text = 'Sorry I can not understand the destination.'
        response.to = response.frm

    await slack.send(response)


async def help_(message, slack, *_):
    response = message.response()
    response.text = 'Help of the good Sir-bot-a-lot'

    help_msg = Attachment(fallback='help', color='good',
                          title='Common commands')
    hello_help = Field(title='Hello',
                       value='Say hello to Sir-bot-a-lot.'
                             '\n`@sir-bot-a-lot hello`',
                       short=True)
    admin_help = Field(title='Admin',
                       value='Send a message to the pythondev admin team.'
                             '\n `@sir-bot-a-lot admin ...`',
                       short=True)
    intro_doc_help = Field(title='Intro doc',
                           value='Link the intro doc.'
                                 '\n `@sir-bot-a-lot intro doc`',
                           short=True)
    what_to_do_help = Field(title='What to do',
                            value='Link the what to do doc.'
                                  '\n `@sir-bot-a-lot what to do`',
                            short=True)
    help_msg.fields.extend(
        (hello_help, admin_help, intro_doc_help, what_to_do_help))

    gif_help = Attachment(fallback='gif help', color='good',
                          title='Gif commands')
    gif_random_help = Field(title='Random',
                            value='Get a random gif.\n`@sir-bot-a-lot gif`',
                            short=True)
    gif_search_help = Field(title='Search',
                            value='Search for a gif.'
                                  '\n`@sir-bot-a-lot gif search ...`',
                            short=True)
    gif_trending_help = Field(title='Trending',
                              value='Get a trending gif.'
                                    '\n`@sir-bot-a-lot gif trending`',
                              short=True)
    gif_by_id_help = Field(title='By ID',
                           value='''Get a gif by it's id.
                           \n`@sir-bot-a-lot gif <gif_id>`''',
                           short=True)
    gif_help.fields.extend(
        (gif_random_help, gif_search_help, gif_trending_help, gif_by_id_help))

    response.attachments.extend((help_msg, gif_help))
    await slack.send(response)
