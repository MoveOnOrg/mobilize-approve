from pywell.entry_points import run_from_cli
import requests


DESCRIPTION = 'Get all pending accounts from Mobilize.'

ARG_DEFINITIONS = {
    'MOBILIZE_API_KEY': 'API key for mobilize.io',
    'MOBILIZE_API_SECRET': 'API secret for mobilize.io',
    'MOBILIZE_API_ROOT': 'Root URL for mobilize.io API',
    'MOBILIZE_DEFAULT_GROUP_ID': 'The first group members request to join',
    'VERBOSE': 'Give verbose output if set'
}

REQUIRED_ARGS = [
    'MOBILIZE_API_KEY', 'MOBILIZE_API_SECRET', 'MOBILIZE_API_ROOT',
    'MOBILIZE_DEFAULT_GROUP_ID'
]


def user_is_pending_for_group(user, group_id):
    return len([
        group for group in user.get('groups', [])
        if group.get('id', '') == group_id
        and group.get('status', '') == 'pending'
    ]) > 0


def get_pending_accounts(args) -> list:
    offset = 0
    count = 0
    done = False
    pending_accounts = []
    while not done:
        if args.VERBOSE:
            print('getting users at offset %s' % offset)
        response = requests.get(
            '%s%s' % (
                args.MOBILIZE_API_ROOT,
                'users?limit=20&offset=%s' % offset
            ),
            auth=requests.auth.HTTPBasicAuth(
                args.MOBILIZE_API_KEY,
                args.MOBILIZE_API_SECRET
            )
        )
        if args.VERBOSE:
            print('status: %s' % response.status_code)
        if response.status_code == 200:
            users = response.json()
            count += len(users)
            pending_accounts += [
                user for user in users
                if user_is_pending_for_group(user, args.MOBILIZE_DEFAULT_GROUP_ID)
            ]
            if len(users) < 20:
                done = True
            else:
                offset += 20
        else:
            done = True
    return pending_accounts


if __name__ == '__main__':
    run_from_cli(get_pending_accounts, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
