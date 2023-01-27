from pywell.entry_points import run_from_cli
from pywell.secrets_manager import get_secret
import requests


DESCRIPTION = 'Get all pending accounts from Mobilize.'

ARG_DEFINITIONS = {
    'VERBOSE': 'Give verbose output if set'
}

REQUIRED_ARGS = []


def user_is_pending_for_group(user, group_id):
    return len([
        group for group in user.get('groups', [])
        if group.get('id', '') == group_id
        and group.get('status', '') == 'pending'
    ]) > 0


def get_pending_accounts(args, script_settings={}) -> list:
    if not script_settings:
        script_settings = get_secret('mobilize-approve')
    offset = 0
    count = 0
    done = False
    pending_accounts = []
    while not done:
        if hasattr(args, 'VERBOSE') and args.VERBOSE:
            print('getting users at offset %s' % offset)
        response = requests.get(
            '%s%s' % (
                script_settings['MOBILIZE_API_ROOT'],
                'users?limit=20&offset=%s' % offset
            ),
            auth=requests.auth.HTTPBasicAuth(
                script_settings['MOBILIZE_API_KEY'],
                script_settings['MOBILIZE_API_SECRET']
            )
        )
        if hasattr(args, 'VERBOSE') and args.VERBOSE:
            print('status: %s' % response.status_code)
        if response.status_code == 200:
            mobilize_group_id = script_settings['MOBILIZE_DEFAULT_GROUP_ID']
            users = response.json()
            count += len(users)
            pending_accounts += [
                user for user in users
                if user_is_pending_for_group(user, mobilize_group_id)
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
