import psycopg2
import psycopg2.extras
from pywell.entry_points import run_from_cli
from pywell.secrets_manager import get_secret


DESCRIPTION = 'Filter a list of emails down to only those currently subscribed.'

ARG_DEFINITIONS = {
    'EMAILS': 'Comma-separated list of email addresses'
}

REQUIRED_ARGS = [
    'EMAILS'
]


def filter_emails_by_membership(args) -> list:
    db_settings = get_secret('redshift-admin')

    database = psycopg2.connect(
        host=db_settings['host'],
        port=db_settings['port'],
        user=db_settings['username'],
        password=db_settings['password'],
        database=db_settings['dbName']
    )
    database_cursor = database.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    membership_check_query = """
    SELECT email
    FROM ak_moveon.core_user
    WHERE email = ANY(%s)
    AND subscription_status = 'subscribed'
    """
    emails = args.EMAILS.split(',')
    database_cursor.execute(membership_check_query, (emails, ))
    return [item.get('email') for item in list(database_cursor.fetchall())]


if __name__ == '__main__':
    run_from_cli(filter_emails_by_membership, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
