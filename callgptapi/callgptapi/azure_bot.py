import requests
import json
import logging
import parameters

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def send_message_to_teams(teams_activity, message):
    """The function of to send a message to Teams via Azure Bot service"""
    access_token = fetch_access_token()

    id = teams_activity["id"]
    recipient_id = teams_activity["recipient"]["id"]
    recipient_name = teams_activity["recipient"]["name"]
    conversatoin_id = teams_activity["conversation"]["id"]
    base_url = teams_activity["serviceUrl"]

    data = {
        "type": "message",
        "from": {"id": recipient_id, "name": recipient_name},
        "conversation": {"id": conversatoin_id},
        "recipient": {"id": recipient_id, "name": recipient_name},
        "text": message,
        "replyToId": id,
    }
    json_data = json.dumps(data)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/json",
    }

    url = f"{base_url}v3/conversations/{conversatoin_id}/activities/{id}"
    response = requests.post(url, data=json_data, headers=headers)
    logger.debug(response)


def fetch_access_token() -> dict:
    """Get access tokens to send a message to Teams"""
    tenant_id = parameters.get_parameter("/callgptapi/AZURE_TENANT_ID")
    params = {
        "grant_type": "client_credentials",
        "client_id": parameters.get_parameter("/callgptapi/AZURE_CLIENT_ID"),
        "client_secret": parameters.get_encrypted_parameter(
            "/callgptapi/AZURE_CLIENT_SECRET"
        ),
        "scope": "https://api.botframework.com/.default",
    }

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    response = requests.post(url, data=params)

    access_token = json.loads(response.text)["access_token"]
    return access_token
