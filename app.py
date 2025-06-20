from flask import Flask, render_template, request, redirect, url_for, flash

from terminate_utils.ad import disable_ad_user

from terminate_utils.azure import disable_azure_user, remove_user_from_all_groups, get_azure_user_id_by_upn

import config


app = Flask(__name__)

app.secret_key = "your-secret-key"


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

