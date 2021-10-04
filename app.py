import uuid
import os
import json
import logging

from flask import (
    Flask,
    redirect,
    request,
    render_template,
    url_for,
    session
)

import shopify
import helpers
from gmail import (
    setup_account,
    create_draft,
    create_message,
    send_message,
    MESSAGE
)
from shopify_client import ShopifyStoreClient

from dotenv import load_dotenv

load_dotenv()
WEBHOOK_APP_UNINSTALL_URL = os.environ.get('WEBHOOK_APP_UNINSTALL_URL')
print('webhook', WEBHOOK_APP_UNINSTALL_URL)


app = Flask(__name__)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


API_VERSION = "2020-10"
ACCESS_TOKEN = None
NONCE = None
# Defaults to offline access mode if left blank or omitted. https://shopify.dev/concepts/about-apis/authentication#api-access-modes
ACCESS_MODE = []  
# https://shopify.dev/docs/admin-api/access-scopes
SCOPES = [
    'write_script_tags',
    'write_customers',
    'write_products',
    'write_orders',
    'read_products',
    'read_orders',
    'read_customers'
]  


@app.route('/logout')
def shopify_app_logout():
    return redirect(url_for('app_launched'))


@app.route('/')
def root_path():
    return redirect(url_for('app_launched'))


@app.route("/send_email")
def send_email():
    """Function to send email to the recipient.
    """
    global ACCESS_TOKEN, NONCE

    shop = session.get("shop")
    product_count = session.get("product_count")
    product_title_1 = session.get("product_title_1")
    product_title_2 = session.get("product_title_2")
    product_title_3 = session.get("product_title_3")

    message_text = MESSAGE.format(
        customer="YJ",
        shop=shop,
        product_count=product_count,
        product_title_1=product_title_1,
        product_title_2=product_title_2,
        product_title_3=product_title_3
    )

    message_body = create_message(
        sender="yueguoguo2048@gmail.com",
        to="fanmd104@gmail.com",
        subject="Greeting from FromAir",
        message_text=message_text
    )

    service = setup_account()
    send_message(service=service, user_id="me", message=message_body)

    NONCE = uuid.uuid4().hex
    redirect_url = helpers.generate_install_redirect_url(
        shop=shop,
        scopes=SCOPES,
        nonce=NONCE,
        access_mode=ACCESS_MODE
    )

    return redirect(redirect_url, code=302)


@app.route('/app_launched', methods=['GET'])
@helpers.verify_web_call
def app_launched():
    """Function to launch the app home page
    """
    shop = request.args.get('shop')
    global ACCESS_TOKEN, NONCE

    if ACCESS_TOKEN:
        with shopify.Session.temp(shop, API_VERSION, str(ACCESS_TOKEN)):
            products = shopify.Product.find(limit=3)

        session["shop"] = shop
        session["product_count"] =  len(products)
        session["product_title_1"] = products[0].title
        session["product_title_2"] = products[1].title
        session["product_title_3"] = products[2].title

        return render_template('products.html', products=products, token=str(ACCESS_TOKEN))

    # The NONCE is a single-use random value we send to Shopify so we know the next call from Shopify is valid (see #app_installed)
    #   https://en.wikipedia.org/wiki/Cryptographic_nonce
    NONCE = uuid.uuid4().hex
    redirect_url = helpers.generate_install_redirect_url(
        shop=shop,
        scopes=SCOPES,
        nonce=NONCE,
        access_mode=ACCESS_MODE
    )

    return redirect(redirect_url, code=302)


@app.route('/app_installed', methods=['GET'])
@helpers.verify_web_call
def app_installed():
    state = request.args.get('state')
    global NONCE, ACCESS_TOKEN

    # Shopify passes our NONCE, created in #app_launched, as the `state` parameter, we need to ensure it matches!
    if state != NONCE:
        return "Invalid `state` received", 400
    NONCE = None

    # Ok, NONCE matches, we can get rid of it now (a nonce, by definition, should only be used once)
    # Using the `code` received from Shopify we can now generate an access token that is specific to the specified `shop` with the
    #   ACCESS_MODE and SCOPES we asked for in #app_installed
    shop = request.args.get('shop')
    code = request.args.get('code')
    ACCESS_TOKEN = ShopifyStoreClient.authenticate(shop=shop, code=code)

    # We have an access token! Now let's register a webhook so Shopify will notify us if/when the app gets uninstalled
    # NOTE This webhook will call the #app_uninstalled function defined below
    shopify_client = ShopifyStoreClient(shop=shop, access_token=ACCESS_TOKEN)
    shopify_client.create_webook(address=WEBHOOK_APP_UNINSTALL_URL, topic="app/uninstalled")

    redirect_url = helpers.generate_post_install_redirect_url(shop=shop)
    return redirect(redirect_url, code=302)


@app.route('/app_uninstalled', methods=['POST'])
@helpers.verify_webhook_call
def app_uninstalled():
    # https://shopify.dev/docs/admin-api/rest/reference/events/webhook?api[version]=2020-04
    # Someone uninstalled your app, clean up anything you need to
    # NOTE the shop ACCESS_TOKEN is now void!
    global ACCESS_TOKEN
    ACCESS_TOKEN = None

    webhook_topic = request.headers.get('X-Shopify-Topic')
    webhook_payload = request.get_json()
    logging.error(f"webhook call received {webhook_topic}:\n{json.dumps(webhook_payload, indent=4)}")

    return "OK"


@app.route('/data_removal_request', methods=['POST'])
@helpers.verify_webhook_call
def data_removal_request():
    # https://shopify.dev/tutorials/add-gdpr-webhooks-to-your-app
    # Clear all personal information you may have stored about the specified shop
    return "OK"


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
