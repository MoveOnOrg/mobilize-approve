import pytest
from _pytest.monkeypatch import MonkeyPatch
from pywell import notify_slack

import post_report


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Test():
    monkeypatch = MonkeyPatch()
    slack_messages = []
    pending_accounts = []

    # Mock what Mobilize would return for pending accounts.
    def mock_get_pending_accounts(self, args):
        return self.pending_accounts

    # Mock the database call to check membership.
    def mock_filter_emails_by_membership(self, args):
        return [
            email for email in args.EMAILS.split(',')
            if email != 'nonmember@example.com'
        ]

    # Mock notifying Slack, record what would be sent.
    def mock_notify_slack(self, args):
        self.slack_messages.append(args.SLACK_MESSAGE_TEXT)

    def test_post_report(self):
        Test.monkeypatch.setattr("post_report.get_pending_accounts", self.mock_get_pending_accounts)
        Test.monkeypatch.setattr("post_report.filter_emails_by_membership", self.mock_filter_emails_by_membership)
        Test.monkeypatch.setattr("post_report.notify_slack", self.mock_notify_slack)
        # All the connection values are being mocked, but still required.
        args = {
            'DB_HOST': 'mock',
            'DB_PORT': 'mock',
            'DB_USER': 'mock',
            'DB_PASS': 'mock',
            'DB_NAME': 'mock',
            'MOBILIZE_API_KEY': 'mock',
            'MOBILIZE_API_SECRET': 'mock',
            'MOBILIZE_API_ROOT': 'mock',
            'MOBILIZE_DEFAULT_GROUP_ID': 'mock',
            'SLACK_WEBHOOK': 'mock',
            'SLACK_CHANNEL': 'mock'
        }
        args = Struct(**args)
        post_report.post_report(args)
        assert self.slack_messages == ['There are currently no pending Mobilize accounts.']
        self.slack_messages = []
        self.pending_accounts = [
            {'name': 'decline account', 'email': 'nonmember@example.com'},
            {'name': 'approve account', 'email': 'member@example.com'}
        ]
        post_report.post_report(args)
        assert self.slack_messages == [
            "The following pending Mobilize accounts should be *approved* (subscribed to MoveOn's email list):\n\u2022 approve account (member@example.com)",
            "The following pending Mobilize accounts should be *declined* (not subscribed to MoveOn's email list):\n\u2022 decline account (nonmember@example.com)"
        ]
