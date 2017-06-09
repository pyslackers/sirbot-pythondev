import re

from sirbot.slack.message import Attachment, Select


def add_to_slack(slack):
    slack.add_message('intro doc',
                      intro_doc, mention=True, flags=re.IGNORECASE)
    slack.add_message('what to do',
                      what_to_do, mention=True, flags=re.IGNORECASE)

    slack.add_action('choose_file', choose_file, public=False)
    slack.add_command('/file', file, public=False)


async def file(command, slack, *_):
    response = command.response()

    if command.text == 'intro':
        response.response_type = 'in_channel'
        response.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'  # noQa
    elif command.text == 'what to do':
        response.response_type = 'in_channel'
        response.text = 'https://pythondev.slack.com/files/ndevox/F4A137J0J/What_to_do_next_on_your_Python_journey'  # noQa
    else:
        att = Attachment(
            title='Choose a file to show',
            fallback='Choose a file to show',
            callback_id='choose_file'
        )

        data = [
            {
                'text': 'Intro doc',
                'value': 'intro_doc'
            },
            {
                'text': 'What to do doc',
                'value': 'what_to_do_doc'
            }
        ]

        select = Select(
            name='choose_file',
            text='Choose a file',
            options=data
        )
        att.actions.append(select)
        response.attachments.append(att)

    await slack.send(response)


async def choose_file(action, slack, *_):
    value = action.action['selected_options'][0]['value']
    response = action.response()

    if value == 'intro_doc':
        response.replace_original = False
        response.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'  # noQa
    elif value == 'what_to_do_doc':
        response.replace_original = False
        response.text = 'https://pythondev.slack.com/files/ndevox/F4A137J0J/What_to_do_next_on_your_Python_journey'  # noQa
    else:
        response.text = '''Sorry we could not find this file'''

    await slack.send(response)


async def intro_doc(message, slack, *_):
    response = message.response()
    response.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'  # noqa
    await slack.send(response)


async def what_to_do(message, slack, *_):
    response = message.response()
    response.text = 'https://pythondev.slack.com/files/ndevox/F4A137J0J/What_to_do_next_on_your_Python_journey'  # noqa
    await slack.send(response)
