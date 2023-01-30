from pywell.entry_points import run_from_cli, run_from_lambda
from pywell.notify_slack import notify_slack
from pywell.secrets_manager import get_secret
import requests

from get_pending_accounts import get_pending_accounts
from filter_emails_by_membership import filter_emails_by_membership


DESCRIPTION = 'Post a report on pending accounts from Mobilize.'

ARG_DEFINITIONS = {
    'VERBOSE': 'Give verbose output if set'
}

REQUIRED_ARGS = []


def account_description(account):
    return "• %s (%s)" % (
        account.get('name', '[NO NAME]'),
        account.get('email', '[NO EMAIL]')
    )

def post_report(args) -> list:
    script_settings = get_secret('mobilize-approve')
    args.SLACK_WEBHOOK = script_settings['SLACK_WEBHOOK']
    args.SLACK_CHANNEL = script_settings['SLACK_CHANNEL']
    accounts = get_pending_accounts(args, script_settings)
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
        account_descriptions = [
            account_description(account) for account in approved_accounts
        ]
        args.SLACK_MESSAGE_TEXT = "The following pending Mobilize accounts "\
                                  "should be *approved* (subscribed to "\
                                  "MoveOn's email list):\n"\
                                  + "\n".join(account_descriptions)
        notify_slack(args)
    if len(declined_accounts):
        account_descriptions = [
            account_description(account) for account in declined_accounts
        ]
        args.SLACK_MESSAGE_TEXT = "The following pending Mobilize accounts "\
                                  "should be *declined* (not subscribed to "\
                                  "MoveOn's email list):\n"\
                                  + "\n".join(account_descriptions)
        notify_slack(args)
    elif len(approved_accounts) == 0:
        args.SLACK_MESSAGE_TEXT = "There are currently no pending Mobilize "\
                                  "accounts."
        notify_slack(args)
    if hasattr(args, 'VERBOSE') and args.VERBOSE:
        import pprint
        pprint.PrettyPrinter(indent=2).pprint({'approved': approved_accounts})
        pprint.PrettyPrinter(indent=2).pprint({'declined': declined_accounts})

    return "%s approved, %s declined" % (
        len(approved_accounts),
        len(declined_accounts)
    )


def aws_lambda(event, context) -> str:
     return run_from_lambda(
         post_report, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS, event
     )


if __name__ == '__main__':
    run_from_cli(post_report, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
