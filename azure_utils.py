import requests

from msal import ConfidentialClientApplication

import config

import logging


GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def get_graph_token():

    app = ConfidentialClientApplication(

        client_id=config.AZURE_CLIENT_ID,

        authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",

        client_credential=config.AZURE_CLIENT_SECRET

    )

    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in token:

        return token['access_token']

    else:

        raise Exception(f"Azure token error: {token.get('error_description')}")


def create_azure_user(display_name, username, password, upn):

    token = get_graph_token()

    headers = {

        "Authorization": f"Bearer {token}",

        "Content-Type": "application/json"

    }

    body = {

        "accountEnabled": True,

        "displayName": display_name,

        "mailNickname": username,

        "userPrincipalName": upn,

        "usageLocation": "CA",  # Required for license assignment

        "passwordProfile": {

            "forceChangePasswordNextSignIn": True,

            "password": password

        }

    }

    res = requests.post(f"{GRAPH_BASE_URL}/users", headers=headers, json=body)

    if res.status_code == 201:

        logging.info(f"✅ Created Azure user: {upn}")

        return res.json()["id"]

    else:

        logging.error(f"❌ Azure user creation failed: {res.text}")

        raise Exception(f"Azure user creation failed: {res.text}")


def assign_license(user_id, sku_id):

    token = get_graph_token()

    headers = {

        "Authorization": f"Bearer {token}",

        "Content-Type": "application/json"

    }

    payload = {

        "addLicenses": [{"skuId": sku_id}],

        "removeLicenses": []

    }

    res = requests.post(f"{GRAPH_BASE_URL}/users/{user_id}/assignLicense", headers=headers, json=payload)

    if res.status_code in [200, 204]:

        logging.info(f"✅ License {sku_id} assigned to user {user_id}")

        return True

    else:

        logging.error(f"❌ License assignment failed: {res.text}")

        raise Exception(f"Azure license assignment failed: {res.text}")


def add_user_to_group(user_id, group_id):

    token = get_graph_token()

    headers = {

        "Authorization": f"Bearer {token}",

        "Content-Type": "application/json"

    }

    endpoint = f"{GRAPH_BASE_URL}/groups/{group_id}/members/$ref"

    payload = {

        "@odata.id": f"{GRAPH_BASE_URL}/directoryObjects/{user_id}"

    }

    res = requests.post(endpoint, headers=headers, json=payload)

    if res.status_code in [200, 204]:

        logging.info(f"✅ User {user_id} added to group {group_id}")

        return True

    else:

        logging.error(f"❌ Adding user to group failed: {res.text}")

        raise Exception(f"Adding user to group failed: {res.text}")


def get_license_skus():

    token = get_graph_token()

    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(f"{GRAPH_BASE_URL}/subscribedSkus", headers=headers)

    if res.status_code == 200:

        data = res.json().get("value", [])

        return [

            {

                "id": sku["skuId"],

                "name": sku.get("skuPartNumber", sku.get("id")),

                "available": sku["prepaidUnits"].get("enabled", 0) - sku["consumedUnits"]

            }

            for sku in data

            if sku.get("prepaidUnits", {}).get("enabled", 0) > 0

        ]

    else:

        logging.error(f"❌ Failed to fetch license SKUs: {res.text}")

        raise Exception(f"Failed to fetch license SKUs: {res.text}")

