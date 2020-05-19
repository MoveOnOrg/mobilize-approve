import psycopg2
import psycopg2.extras
from pywell.entry_points import run_from_cli


DESCRIPTION = 'Filter a list of emails down to only those currently subscribed.'

ARG_DEFINITIONS = {
    'DB_HOST': 'Database host IP or hostname',
    'DB_PORT': 'Database port number',
    'DB_USER': 'Database user',
    'DB_PASS': 'Database password',
    'DB_NAME': 'Database name',
    'EMAILS': 'Comma-separated list of email addresses'
}

REQUIRED_ARGS = [
    'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASS', 'DB_NAME', 'EMAILS'
]


def filter_emails_by_membership(args) -> list:
    database = psycopg2.connect(
        host=args.DB_HOST,
        port=args.DB_PORT,
        user=args.DB_USER,
        password=args.DB_PASS,
        database=args.DB_NAME
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
