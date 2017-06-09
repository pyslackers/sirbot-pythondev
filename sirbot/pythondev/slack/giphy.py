import json

from sirbot.slack.message import Attachment, Button


def add_to_slack(slack):
    slack.add_command('/gif', gif_search, public=False)
    slack.add_action('gif_search', gif_search_action, public=False)


async def gif_search(command, slack, facades):
    response = command.response()
    giphy = facades.get('giphy')

    if command.text:
        urls = await giphy.search(command.text)

        att = Attachment(
            title='You searched for `{}`'.format(command.text),
            fallback='You searched for `{}`'.format(command.text),
            image_url=urls[0],
            callback_id='gif_search'
        )

        data = json.dumps({'urls': urls, 'search': command.text, 'index': 0})
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


async def gif_search_action(action, slack, facades):
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

        ok = Button(name='ok', text='Send', style='primary', value=data_json)
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
