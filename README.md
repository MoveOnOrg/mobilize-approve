# Mobilize Approval

These scripts pull current pending accounts in Mobilize and post a Slack report of which accounts should be approved based on our approval criteria, which is currently email list subscription. At some point Mobilize will hopefully allow approval via API, and then we can replace the report with auto-approval.

You can run this locally from a command line with only the requirements in `requirements.txt`. If you want to run tests and/or deploy the script to Lambda, you'll need the additional requirements in `dev_requirements.txt`.
