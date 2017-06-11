from sirbot.slack.message import Attachment


def add_to_slack(slack):
    slack.add_command('/admin', func=share_admin, public=False)


async def share_admin(command, slack, facades):

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
