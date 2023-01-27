
# Mobilize Approval

These scripts pull current pending accounts in Mobilize and post a Slack report of which accounts should be approved based on our approval criteria, which is currently email list subscription. At some point Mobilize will hopefully allow approval via API, and then we can replace the report with auto-approval.

You can run this locally from a command line with only the requirements in `requirements.txt`. If you want to run tests and/or deploy the script to Lambda, you'll need the additional requirements in `dev_requirements.txt`.

## Secrets Manager

The database connection details should be saved and called from a Secrets Manager record called `redshift-admin`, and the following settings are stored and called from `mobilize-approve`:

    MOBILIZE_API_KEY: 'API key for mobilize.io'
    MOBILIZE_API_SECRET: 'API secret for mobilize.io'
    MOBILIZE_API_ROOT: 'Root URL for mobilize.io API'
    MOBILIZE_DEFAULT_GROUP_ID: 'The first group members request to join'
    SLACK_WEBHOOK: 'Web hook URL for Slack.'
    SLACK_CHANNEL: 'Slack channel to send to.'
