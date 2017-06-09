from sirbot.slack.message import Attachment


def add_to_slack(slack):
    slack.add_command('/pypi', pypi_search, public=True)


async def pypi_search(command, slack, facades):
    response = command.response()
    pypi = facades.get('pypi')
    results = await pypi.search(command.text)

    if not command.text:
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
                title_link='{}/{}'.format(pypi.ROOT_URL, results[3]['name'])
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
        response.text = "<@{}> Searched PyPi for `{}`".format(command.frm.id,
                                                              command.text)
    else:
        response.text = "Could not find anything on PyPi matching" \
                        " `{0}`".format(command.text)

    await slack.send(response)
