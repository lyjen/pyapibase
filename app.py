"""APP"""
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from library.log import Log

# USER CONTROLLER
from controllers.user import login
from controllers.user import reset_password
from controllers.user import authentication_key

# CUSTOMER CONTROLLER
from controllers.customer import customer

LOG = Log()

APP = Flask(__name__)

CORS(APP)
Swagger(APP)

# --------------------------------------------------------------
# USER
# --------------------------------------------------------------
LOGIN = login.Login()
RESET_PASSWORD = reset_password.ResetPassword()
AUTHENTICATION_KEY = authentication_key.AuthenticationKey()

# # USER ROUTE
APP.route('/user/login', methods=['POST'])(LOGIN.login)
APP.route('/user/reset/password', methods=['PUT'])(RESET_PASSWORD.reset_password)
APP.route('/user/authentication-key', methods=['PUT'])(AUTHENTICATION_KEY.authentication_key)

# --------------------------------------------------------------
# CUSTOMER
# --------------------------------------------------------------
CUSTOMER = customer.Customer()

# CUSTOMER ROUTE
APP.route('/customer/index', methods=['GET'])(CUSTOMER.customer)

if __name__ == '__main__':

    APP.run(host='0.0.0.0', port=8000)
