from flask import Flask, render_template, request, redirect, url_for, flash

from terminate_utils.ad import disable_ad_user
from terminate_utils.azure import (
    disable_azure_user,
    remove_user_from_all_groups,
    get_azure_user_id_by_upn,
)

from ldap_utils import create_ad_user, fetch_ous, fetch_groups
from azure_utils import (
    create_azure_user,
    assign_license,
    add_user_to_group,
    get_license_skus,
)

import secrets

import config


app = Flask(__name__)

app.secret_key = "your-secret-key"


@app.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        ad_ou = request.form.get("ad_ou")
        ad_group = request.form.get("ad_group")
        azure_enabled = request.form.get("azure_enabled") == "on"
        password = secrets.token_urlsafe(12)

        try:
            create_ad_user(first_name, last_name, ad_ou, ad_group, username, password)

            if azure_enabled:
                upn = f"{username}@{config.AZURE_DOMAIN}"
                azure_user_id = create_azure_user(f"{first_name} {last_name}", username, password, upn)

                for sku_id in request.form.getlist("azure_skus"):
                    assign_license(azure_user_id, sku_id)

                location = request.form.get("azure_location")
                group_id = config.GROUP_CHOICES.get(location)
                if group_id:
                    add_user_to_group(azure_user_id, group_id)

            flash(f"✅ User {username} created. Temp password: {password}", "success")
        except Exception as e:
            flash(f"❌ User creation failed: {str(e)}", "danger")

        return redirect(url_for("create"))

    ous_raw = fetch_ous()
    groups = fetch_groups()
    ous = [{"dn": dn, "label": dn.split(',')[0].split('=')[1]} for dn in ous_raw]
    azure_skus = get_license_skus()

    return render_template("form.html", ous=ous, groups=groups, azure_skus=azure_skus)


@app.route("/terminate", methods=["GET", "POST"])

def terminate():

    if request.method == "POST":

        username = request.form.get("username")

        upn = f"{username}@{config.AZURE_DOMAIN}"


        try:

            disable_ad_user(username)

            azure_user_id = get_azure_user_id_by_upn(upn)

            if azure_user_id:

                disable_azure_user(azure_user_id)

                remove_user_from_all_groups(azure_user_id)

            flash("🧯 Termination completed successfully", "success")

        except Exception as e:

            flash(f"❌ Termination failed: {str(e)}", "danger")


        return redirect(url_for("terminate"))


    return render_template("terminate.html")


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5003, debug=True)

