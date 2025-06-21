import ldap3

import config


def disable_ad_user(username):

    server = ldap3.Server(config.AD_SERVER)

    conn = ldap3.Connection(
        server,
        user=config.AD_ADMIN,
        password=config.AD_PASSWORD,
        auto_bind=True,
    )

    

    search_base = config.AD_BASE_DN

    search_filter = f"(sAMAccountName={username})"

    

    conn.search(search_base, search_filter, attributes=["distinguishedName"])

    if not conn.entries:

        raise Exception("User not found in Active Directory")

    

    dn = conn.entries[0].entry_dn

    conn.modify(dn, {'userAccountControl': [(ldap3.MODIFY_REPLACE, [514])]})

    if not conn.result['result'] == 0:

        raise Exception("Failed to disable AD user")

