
from pywell.entry_points import run_from_cli
from pywell.notify_slack import notify_slack
import requests

from get_pending_accounts import get_pending_accounts
from filter_emails_by_membership import filter_emails_by_membership


DESCRIPTION = 'Post a report on pending accounts from Mobilize.'

ARG_DEFINITIONS = {
    'DB_HOST': 'Database host IP or hostname',
    'DB_PORT': 'Database port number',
    'DB_USER': 'Database user',
    'DB_PASS': 'Database password',
    'DB_NAME': 'Database name',
    'MOBILIZE_API_KEY': 'API key for mobilize.io',
    'MOBILIZE_API_SECRET': 'API secret for mobilize.io',
    'MOBILIZE_API_ROOT': 'Root URL for mobilize.io API',
    'MOBILIZE_DEFAULT_GROUP_ID': 'The first group members request to join',
    'SLACK_WEBHOOK': 'Web hook URL for Slack.',
    'SLACK_CHANNEL': 'Slack channel to send to.',
    'VERBOSE': 'Give verbose output if set'
}

REQUIRED_ARGS = [
    'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASS', 'DB_NAME',
    'MOBILIZE_API_KEY', 'MOBILIZE_API_SECRET', 'MOBILIZE_API_ROOT',
    'MOBILIZE_DEFAULT_GROUP_ID', 'SLACK_WEBHOOK', 'SLACK_CHANNEL'
]


def post_report(args) -> list:
    accounts = get_pending_accounts(args)
    args.EMAILS = ','.join([account.get('email', '') for account in accounts])
    approved_emails = filter_emails_by_membership(args)
    approved_accounts = [
        account for account in accounts
        if account.get('email', '') in approved_emails
    ]
    declined_accounts = [
        account for account in accounts
        if account.get('email', '') not in approved_emails
    ]
    if len(approved_accounts):
        args.SLACK_MESSAGE_TEXT = "The following pending Mobilize accounts "
        args.SLACK_MESSAGE_TEXT += "should be *approved* "
        args.SLACK_MESSAGE_TEXT += "(subscribed to MoveOn's email list):\n"
        args.SLACK_MESSAGE_TEXT += "\n".join([
            "• %s (%s)" % (
                account.get('name', '[NO NAME]'),
                account.get('email', '[NO EMAIL]')
            )
            for account in approved_accounts
        ])
        notify_slack(args)
    if len(declined_accounts):
        args.SLACK_MESSAGE_TEXT = "The following pending Mobilize accounts "
        args.SLACK_MESSAGE_TEXT += "should be *declined* "
        args.SLACK_MESSAGE_TEXT += "(not subscribed to MoveOn's email list):\n"
        args.SLACK_MESSAGE_TEXT += "\n".join([
            "• %s (%s)" % (
                account.get('name', '[NO NAME]'),
                account.get('email', '[NO EMAIL]')
            )
            for account in declined_accounts
        ])
        notify_slack(args)
    elif len(approved_accounts) == 0:
        args.SLACK_MESSAGE_TEXT = "There are currently no pending "
        args.SLACK_MESSAGE_TEXT += "Mobilize accounts."
        notify_slack(args)
    if args.VERBOSE:
        import pprint
        pprint.PrettyPrinter(indent=2).pprint({'approved': approved_accounts})
        pprint.PrettyPrinter(indent=2).pprint({'declined': declined_accounts})

    return "%s approved, %s declined" % (
        len(approved_accounts),
        len(declined_accounts)
    )


if __name__ == '__main__':
    run_from_cli(post_report, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
