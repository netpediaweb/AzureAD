from ldap3 import Server, Connection, NTLM, ALL, MODIFY_REPLACE

import config

import logging


# Establish and return connection to Active Directory

def connect_ad():

    server = Server(config.AD_SERVER, get_info=ALL)

    conn = Connection(

        server,

        user=config.AD_ADMIN,

        password=config.AD_PASSWORD,

        authentication=NTLM

    )

    if not conn.bind():

        raise Exception("❌ Failed to bind to Active Directory")

    return conn


# Format password for AD (UTF-16-LE enclosed in quotes)

def format_password(password):

    return ('"' + password + '"').encode('utf-16-le')


# Create a user in Active Directory

def create_ad_user(first_name, last_name, ou_dn, group_dn, username, password):

    display_name = f"{first_name} {last_name}"

    user_dn = f"CN={display_name},{ou_dn}"

    upn = f"{username}@{config.AD_DOMAIN}"


    conn = connect_ad()


    attributes = {

        'givenName': first_name,

        'sn': last_name,

        'displayName': display_name,

        'userPrincipalName': upn,

        'sAMAccountName': username,

        'objectClass': ['top', 'person', 'organizationalPerson', 'user']

    }


    logging.info(f"🔧 Creating AD user: {user_dn}")

    conn.add(user_dn, attributes=attributes)


    # Set password and enable account

    conn.modify(user_dn, {'unicodePwd': [(MODIFY_REPLACE, [format_password(password)])]})

    conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})  # Enable account

    conn.extend.microsoft.unlock_account(user_dn)


    # Add user to group (if applicable)

    if group_dn and "=" in group_dn:

        logging.info(f"➕ Adding user to group: {group_dn}")

        conn.modify(group_dn, {'member': [(MODIFY_REPLACE, [user_dn])]})


    logging.info(f"✅ AD user created: {user_dn}")

    conn.unbind()


# Enable an existing AD user account

def enable_ad_user(user_dn, password):

    conn = connect_ad()

    conn.modify(user_dn, {'unicodePwd': [(MODIFY_REPLACE, [format_password(password)])]})

    conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})  # Enable account

    conn.extend.microsoft.unlock_account(user_dn)

    logging.info(f"✅ Account enabled: {user_dn}")

    conn.unbind()


# Fetch all Organizational Units

def fetch_ous():

    conn = connect_ad()

    conn.search(

        search_base=config.AD_BASE_DN,

        search_filter="(objectClass=organizationalUnit)",

        attributes=["distinguishedName"]

    )

    ous = [

        entry["attributes"]["distinguishedName"]

        for entry in conn.response

        if "attributes" in entry and "distinguishedName" in entry["attributes"]

    ]

    conn.unbind()

    return ous


# Fetch all groups

def fetch_groups():

    conn = connect_ad()

    conn.search(

        search_base=config.AD_BASE_DN,

        search_filter="(objectClass=group)",

        attributes=["distinguishedName"]

    )

    groups = [

        entry["attributes"]["distinguishedName"]

        for entry in conn.response

        if "attributes" in entry and "distinguishedName" in entry["attributes"]

    ]

    conn.unbind()

    return groups


# Search user in AD by sAMAccountName

def search_user_by_sam(sam_name):

    conn = connect_ad()

    search_filter = f"(sAMAccountName={sam_name})"

    conn.search(

        search_base=config.AD_BASE_DN,

        search_filter=search_filter,

        attributes=["distinguishedName"]

    )

    if conn.entries:

        user_dn = conn.entries[0].entry_dn

        logging.info(f"🔎 Found user: {user_dn}")

        conn.unbind()

        return user_dn

    else:

        logging.warning("❌ User not found")

        conn.unbind()

        return None

