import asyncio
import json
import re

from sirbot.core import registry
from sirbot.slack.message import SlackMessage, Attachment, Field, Button, \
    Select


class SlackEndpoint:
    def __init__(self, config):
        self.config = config

        self.config['candy']['user_regex'] = re.compile('<@U.{8}>')
        self.config['candy']['trigger_regex'] = re.compile(
            self.config['candy']['trigger']
        )

    def add(self):
        slack = registry.get('slack')
        slack.add_message('^help', self.help_, flags=re.IGNORECASE,
                          mention=True)
        slack.add_message('tell (<(#|@)(?P<to_id>[A-Z0-9]*)(|.*)?>)'
                          ' (?P<item>.*)',
                          self.publish, flags=re.IGNORECASE, mention=True,
                          admin=True)
        slack.add_message('hello', self.hello, mention=True,
                          flags=re.IGNORECASE)

        slack.add_command('/admin', func=self.share_admin)

        slack.add_message(self.config['candy']['trigger'],
                          self.add_candy_message)
        slack.add_command('/leaderboard', self.leaderboard)
        slack.add_event('reaction_added', self.add_candy_reaction)

        slack.add_command('/do', self.share_digital_ocean)

        slack.add_action('choose_file', self.choose_file)
        slack.add_command('/file', self.file)

        slack.add_command('/gif', self.gif_search)
        slack.add_action('gif_search', self.gif_search_action)

        slack.add_event('team_join', self.team_join)
        slack.add_event('team_join', self.members_joined)

        slack.add_command('/pypi', self.pypi_search)

        slack.add_command('/moveto', self.move_to)

    async def hello(self, message, slack, *_):
        response = message.response()
        response.text = 'Hello'
        await slack.send(response)

    async def publish(self, message, slack, match):
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

    async def help_(self, message, slack, *_):
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
                                value='Get a random gif.'
                                      '\n`@sir-bot-a-lot gif`',
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
            (gif_random_help, gif_search_help, gif_trending_help,
             gif_by_id_help))

        response.attachments.extend((help_msg, gif_help))
        await slack.send(response)

    async def share_admin(self, command, slack):

        response = command.response()
        to = await slack.groups.get('G1DRT62UC')

        att = Attachment(
            fallback='admin message',
            text=command.text,
            title='Message to the admin team by <@{}>'.format(command.frm.id),
        )

        response.to = to
        response.attachments.append(att)
        await slack.send(response)

    async def add_candy_message(self, message, slack, *_):
        users_raw = self.config['candy']['user_regex'].findall(message.text)
        users = [user[2:-1] for user in users_raw if
                 user[2:-1] != message.frm.id]

        if not users:
            return

        candy = registry.get('candy')
        response = message.response()
        count = len(
            self.config['candy']['trigger_regex'].findall(message.text)
        )

        receivers_messages = list()
        for user in users:
            slack_user = await slack.users.get(user, dm=True)
            user_count = await candy.add(user, count)
            msg = response.clone()
            msg.to = slack_user

            text_message = '<@{sender}> gave you {count} {trigger}.' \
                           ' You now have {user_count} {trigger}.'
            msg.text = text_message.format(
                sender=message.frm.id,
                count=count,
                trigger=self.config['candy']['trigger'],
                user_count=user_count
            )
            receivers_messages.append(msg)

        response.to = message.frm
        response.text = 'You gave {count} {trigger} to <@{user}>'.format(
            count=count,
            trigger=self.config['candy']['trigger'],
            user=', '.join(users))

        await slack.send(response)
        for msg in receivers_messages:
            await slack.send(msg)

    async def add_candy_reaction(self, event, slack):
        if event['reaction'] == 'bdfl' and event['user'] != event['item_user']:
            candy = registry.get('candy')
            user_count = await candy.add(event['item_user'])

            message_from = SlackMessage(
                to=(await slack.users.get(event['user'], dm=True)))
            message_from.text = 'You gave 1 {trigger} to <@{user}>'.format(
                trigger=self.config['candy']['trigger'],
                user=event['item_user'])

            message_to = SlackMessage(
                to=(await slack.users.get(event['item_user'], dm=True)))
            message_to.text = '<@{sender}> gave you 1 {trigger}. ' \
                              'You now have {user_count} {trigger}.'
            message_to.text = message_to.text.format(
                sender=event['user'],
                trigger=self.config['candy']['trigger'],
                user_count=user_count
            )
            await slack.send(message_from)
            await slack.send(message_to)

        else:
            return

    async def leaderboard(self, command, slack):
        response = command.response()

        candy = registry.get('candy')
        data = await candy.top(count=10)
        att = Attachment(
            title='{} Leaderboard'.format(self.config['candy']['trigger']),
            fallback='{} Leaderboard'.format(self.config['candy']['trigger']),
            color='good'
        )

        if not data:
            response.text = 'No data to display'
        else:
            response.response_type = 'in_channel'
            for user in data:
                slack_user = await slack.users.get(user['user'])
                att.text += '{} *{}*\n'.format(slack_user.name, user['candy'])

            response.attachments.append(att)

        await slack.send(response)

    async def share_digital_ocean(self, command, slack):
        response = command.response()
        response.text = self.config['digital_ocean']['msg'].format(
            self.config['digital_ocean']['url'],
            self.config['digital_ocean']['refferral'],
        )
        await slack.send(response)

    async def file(self, command, slack, *_):
        response = command.response()

        for file in self.config['files'].values():
            if command.text == file['match']:
                response.response_type = 'in_channel'
                response.text = self.config['files_template'].format(
                    file['url'], file['name'])
                break
        else:
            response.response_type = 'ephemeral'
            att = Attachment(
                title='Choose a file to show',
                fallback='Choose a file to show',
                callback_id='choose_file'
            )

            data = [
                {'value': file['match'], 'text': file['name']}
                for file in self.config['files'].values()
            ]

            select = Select(
                name='choose_file',
                text='Choose a file',
                options=data
            )
            att.actions.append(select)
            response.attachments.append(att)

        await slack.send(response)

    async def choose_file(self, action, slack, *_):
        value = action.action['selected_options'][0]['value']
        response = action.response()
        response.text = 'No file found !'

        for file in self.config['files'].values():
            if value == file['match']:
                response.replace_original = False
                response.text = self.config['files_template'].format(
                    file['url'], file['name'])
        await slack.send(response)

    async def gif_search(self, command, slack):
        response = command.response()
        giphy = registry.get('giphy')

        if command.text:
            response.response_type = 'ephemeral'
            urls = await giphy.search(command.text)
            urls = [url.split('?')[0] for url in urls]

            att = Attachment(
                title='You searched for `{}`'.format(command.text),
                fallback='You searched for `{}`'.format(command.text),
                image_url=urls[0],
                callback_id='gif_search'
            )

            data = json.dumps(
                {'urls': urls, 'search': command.text, 'index': 0}
            )
            ok = Button(name='ok', text='Send', style='primary', value=data)
            next_ = Button(name='next', text='Next', value=data)

            att.actions = [ok, next_]
            response.attachments.append(att)
            await slack.send(response)
        else:
            url = giphy.trending()

            att = Attachment(
                title='Trending gif on giphy',
                fallback='Trending gif on giphy',
                image_url=url,
            )
            response.attachments.append(att)
            await slack.send(response)

    async def gif_search_action(self, action, slack):
        response = action.response()
        data = json.loads(action.action['value'])

        if action.action['name'] == 'ok':
            title = '<@{}> Searched giphy for: `{}`'.format(
                action.frm.id,
                data['search']
            )

            att = Attachment(
                title=title,
                fallback=title,
                image_url=data['urls'][data['index']],
            )

            response.attachments.append(att)
            response.replace_original = False
            await slack.send(response)

            confirm = action.response()
            confirm.text = 'Gif successfully sent'
            await slack.send(confirm)

        elif action.action['name'] in ('next', 'previous'):

            if action.action['name'] == 'next':
                index = data['index'] + 1
            else:
                index = data['index'] - 1

            url = data['urls'][index]

            att = Attachment(
                title='Giphy search: `{}`'.format(data['search']),
                fallback='Giphy search: `{}`'.format(data['search']),
                image_url=url,
                callback_id='gif_search'
            )

            data['index'] = index
            data_json = json.dumps(data)

            ok = Button(name='ok', text='Send', style='primary',
                        value=data_json)
            att.actions.append(ok)

            if index != 0:
                previous = Button(
                    name='previous',
                    text='Previous',
                    value=data_json
                )
                att.actions.append(previous)

            if len(data['urls']) > index + 1:
                next_ = Button(name='next', text='Next', value=data_json)
                att.actions.append(next_)

            response.attachments.append(att)
            await slack.send(response)

        else:
            return

    async def team_join(self, event, slack, _):
        await asyncio.sleep(60)
        to = await slack.users.get(event['user']['id'], dm=True)
        message = SlackMessage(to=to)
        message.text = self.config['join'].format(
            self.config['files']['intro_doc']['url'])
        await slack.send(message)

    async def pypi_search(self, command, slack):
        response = command.response()
        pypi = registry.get('pypi')
        results = await pypi.search(command.text)

        if not command.text:
            response.response_type = 'ephemeral'
            response.text = 'Please enter the package name you wish to find'
            await slack.send(response)
            return

        if results:
            for result in results[:3]:
                att = Attachment(
                    title=result['name'],
                    fallback=result['name'],
                    text=result['summary'],
                    title_link='{}/{}'.format(pypi.ROOT_URL, result['name'])
                )
                response.attachments.append(att)

            if len(results) == 4:
                att = Attachment(
                    title=results[3]['name'],
                    fallback=results[3]['name'],
                    text=results[3]['summary'],
                    title_link='{}/{}'.format(
                        pypi.ROOT_URL, results[3]['name']
                    )
                )
                response.attachments.append(att)

            elif len(results) > 3:
                path = pypi.SEARCH_PATH.format(command.text)
                more_info = Attachment(
                    title='{0} more results..'.format(len(results) - 3),
                    fallback='{0} more results..'.format(len(results) - 3),
                    title_link='{}/{}'.format(pypi.ROOT_URL, path)
                )
                response.attachments.append(more_info)

            response.response_type = 'in_channel'
            response.text = "<@{}> Searched PyPi for `{}`".format(
                command.frm.id,
                command.text)
        else:
            response.response_type = 'ephemeral'
            response.text = "Could not find anything on PyPi matching" \
                            " `{0}`".format(command.text)

        await slack.send(response)

    async def members_joined(self, event, slack, _):

        members = await slack.users.all(fetch=True, deleted=False)
        if len(members) % 1000 == 0:
            to = await slack.channels.get(name='general')
            message = SlackMessage(to=to)
            message.text = ':tada: Everyone give a warm welcome to <@{user}>' \
                           ' our {number} members ! :tada:' \
                           '\nhttps://youtu.be/pbSCWgZQf_g?t=3'
            message.text = message.text.format(number=len(members),
                                               user=event['user']['id'])
            await slack.send(message)

    async def move_to(self, command, slack):
        response = command.response(type_='ephemeral')
        command.text = command.text.strip()
        if not command.text:
            response.text = 'Please enter the channel name'
        elif command.text.startswith('<'):
            match = re.search(
                "<(#|@)(?P<to_id>[A-Z0-9]*)(|.*)?>", command.text)
            if match is None:
                response.text = 'Sorry I can not understand the destination.'
            else:
                to = await slack.channels.get(match.group('to_id'))
                if to:
                    response.response_type = 'in_channel'
                    response.text = self.config['moveto']['msg'].format(
                        to.id, to.name)
                else:
                    response.text = 'Sorry I can not \
                    understand the destination.'
        else:
            response.text = 'Sorry I can not understand the destination.'

        await slack.send(response)
