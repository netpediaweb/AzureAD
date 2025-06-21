import requests

from msal import ConfidentialClientApplication

import config


def get_access_token():

    app = ConfidentialClientApplication(

        config.AZURE_CLIENT_ID,

        authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",

        client_credential=config.AZURE_CLIENT_SECRET

    )

    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    return token["access_token"]


def get_azure_user_id_by_upn(upn):

    token = get_access_token()

    headers = {"Authorization": f"Bearer {token}"}

    url = f"https://graph.microsoft.com/v1.0/users/{upn}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        return response.json()["id"]

    return None


def disable_azure_user(user_id):

    token = get_access_token()

    url = f"https://graph.microsoft.com/v1.0/users/{user_id}"

    headers = {

        "Authorization": f"Bearer {token}",

        "Content-Type": "application/json"

    }

    payload = {"accountEnabled": False}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code >= 300:

        raise Exception("Failed to disable Azure account")


def remove_user_from_all_groups(user_id):

    token = get_access_token()

    headers = {"Authorization": f"Bearer {token}"}

    group_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf"


    group_ids = []

    response = requests.get(group_url, headers=headers)

    if response.status_code == 200:

        for group in response.json().get("value", []):

            if group["@odata.type"] == "#microsoft.graph.group":

                group_ids.append(group["id"])


    for group_id in group_ids:

        del_url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/{user_id}/$ref"

        requests.delete(del_url, headers=headers)

