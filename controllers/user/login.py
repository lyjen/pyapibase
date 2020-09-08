# pylint: disable=no-self-use
"""Login"""
# import logging
import time
import requests
import json
from flask import request
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.sha_security import ShaSecurity
from library.emailer import Email
from templates.login import LoginEmail

class Login(Common, ShaSecurity):
    """Class for Login"""

    def __init__(self):
        """The Constructor for Login class"""
        self.postgres = PostgreSQL()
        super(Login, self).__init__()

    # LOGIN FUNCTION
    def login(self):
        """
        This API is use for login
        ---
        tags:
          - User
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: query
            in: body
            description: Login
            required: true
            schema:
              id: Login
              properties:
                email:
                    type: string
                password:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: User Information
        """

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # INSTANTIATE VARIABLES
        json_return = {}
        # account_table = "account"

        # GET REQUEST PARAMS
        email = query_json["email"]
        password = query_json["password"]

        # CHECK IF USER EXIST
        user_data = self.get_user_data(email)

        # CHECK USERNAME
        if user_data:
            if "no_username" in user_data['username']:
                user_data['username'] = ""

        if not user_data:

            json_return["alert"] = "Invalid Username or Password!"
            json_return['status'] = 'Failed'
            # logging.warning("Email does not exists, email: %s " % email)

            # RETURN
            return self.return_data(json_return)

        # CHECK IF USER STATUS IS ACTIVE
        if not self.check_user_status(user_data):

            json_return["alert"] = "User is deactivated!"
            json_return['status'] = 'Failed'
            # logging.warning("User is deactivated, email: %s " % email)

            # RETURN
            return self.return_data(json_return)

        # CHECK PASSWORD
        if not self.check_password(password, user_data):

            json_return["alert"] = "Invalid Username or Password!"
            json_return['status'] = 'Failed'
            # logging.warning("Invalid Username or Password")

            # CLOSE DB CONNECTION
            # self.postgres.close_connection()

            # RETURN
            return self.return_data(json_return)

        # UPDATE TOKEN
        # user_data = self.update_token(user_data)

        # UPDATE PASSWORD
        user_data = self.remove_key(user_data, "password")
        user_data = self.remove_key(user_data, "created_on")
        user_data = self.remove_key(user_data, "last_login")
        user_data = self.remove_key(user_data, "reset_token")
        user_data = self.remove_key(user_data, "reset_token_date")

        user_info = {}
        user_info['account_id'] = user_data['id']
        user_info['remote_addr'] = request.remote_addr
        user_info['platform'] = request.user_agent.platform
        user_info['browser'] = request.user_agent.browser
        user_info['version'] = request.user_agent.version
        user_info['language'] = request.user_agent.language
        user_info['string'] = request.user_agent.string

        # GET TOKENS
        account_token = self.get_tokens(user_info)

        user_data['token'] = account_token['token']
        user_data['token_expire_date'] = account_token['token_expire_date']
        user_data['refresh_token'] = account_token['refresh_token']
        user_data['refresh_token_expire_date'] = account_token['refresh_token_expire_date']

        # CHECK IF NEW DEVICE
        if self.check_device_log(user_info):
            # SEND LOGIN EMAIL
            self.login_email(user_data['email'], user_info)

        # RETURN
        return self.return_data(user_data)

    def check_device_log(self, data):
        """ Check login history """

        log = {}
        log['remote_addr'] = data['remote_addr']
        log['platform'] = data['platform']
        log['browser'] = data['browser']
        log['version'] = data['version']
        log['date'] = time.time()
        log_details = []
        log_details.append(log)
        account_id = data['account_id']

        sql_str = "SELECT * FROM account_login_history"
        sql_str += " WHERE account_id='{0}'".format(account_id)
        result = self.postgres.query_fetch_one(sql_str)

        if result:
            remote_address = [res['remote_addr'] for res in result['login_details']]
            platform = [res['platform'] for res in result['login_details']]
            browser = [res['browser'] for res in result['login_details']]

            # CHECK REMOTE ADDRESS
            if data['remote_addr'] in remote_address:
                if data['platform'] in platform and data['browser'] in browser:
                    return 0

                self.update_login_history(result, log_details)

            else:
                self.update_login_history(result, log_details)
    
        else:
            # ADD LOG
            tmp = {}
            tmp['account_id'] = account_id
            tmp['login_details'] = json.dumps(log_details)
            tmp['update_on'] = time.time()
            self.postgres.insert('account_login_history', tmp, 'account_id')

        return 1

    def update_login_history(self, result, log_details):
        """ Update Login History """

        # UPDATE
        account_id = result['account_id']
        conditions = []

        conditions.append({
        "col": "account_id",
        "con": "=",
        "val": account_id
        })

        result['login_details'] = json.dumps(result['login_details'] + log_details)
        result['update_on'] = time.time()
        result = self.remove_key(result, "account_id")
        self.postgres.update('account_login_history', result, conditions)

        return 1

    # GET USER INFO
    def get_user_data(self, email):
        """Return User Information"""

        # CREATE SQL QUERY
        sql_str = "SELECT * FROM account_master"
        sql_str += " WHERE email='{0}' OR username='{0}'".format(email)

        # GET USER INFO
        user_data = self.postgres.query_fetch_one(sql_str)

        # CHECK IF USER EXIST
        if not user_data:

            # RETURN
            return 0

        # RETURN
        return user_data

    # CHECK USER STATUS
    def check_user_status(self, user_data):
        """Check User Status"""

        # CHECK IF STATUS IS TRUE OR 1
        if user_data["status"]:

            # RETURN
            return 1

        # RETURN
        return 0

    # CHECK PASSWORD
    def check_password(self, password, user_data):
        """Check User Password"""

        # CHECK PASSWORD
        if password == user_data["password"]:

            # RETURN
            return 1

        # RETURN
        return 0

    def get_tokens(self, user_info):
        """ RETURN USER INFO """

        # DELETE EXISTING TOKEN

        conditions = []

        conditions.append({
            "col": "account_id",
            "con": "=",
            "val": user_info['account_id']
            })

        conditions.append({
            "col": "remote_addr",
            "con": "=",
            "val": user_info['remote_addr']
            })

        conditions.append({
            "col": "platform",
            "con": "=",
            "val": user_info['platform']
            })

        conditions.append({
            "col": "browser",
            "con": "=",
            "val": user_info['browser']
            })

        conditions.append({
            "col": "version",
            "con": "=",
            "val": user_info['version']
            })

        self.postgres.delete('account_token', conditions)

        refresh_token_expire_date = int(time.time()) + 86400 # ADD 1 DAY IN CURRENT TIME
        token_expire_date = int(time.time()) + 3600 # ADD 1 HOUR IN CURRENT TIME

        # INSERT NEW TOKENS
        data = {}
        data['account_id'] = user_info['account_id']
        data['token'] = self.generate_token(False)
        data['token_expire_date'] = token_expire_date
        data['refresh_token'] = self.generate_token(False)
        data['refresh_token_expire_date'] = refresh_token_expire_date
        data['remote_addr'] = user_info['remote_addr']
        data['platform'] = user_info['platform']
        data['browser'] = user_info['browser']
        data['version'] = user_info['version']
        data['language'] = user_info['language']
        data['string'] = user_info['string']
        data['update_on'] = time.time()
        data['created_on'] = time.time()

        self.postgres.insert('account_token', data)

        return data

    def login_email(self, email, user_data):
        """Send Confirmation"""

  
        ip_address = user_data['remote_addr']
        new_location = requests.get("https://geolocation-db.com/json/"+ip_address+"&position=true").json()

        state = "Unknown"
        location = "Unknown"

        if new_location['state'] != "Not found" and new_location['state']:

            state = new_location['state'].replace("Province of ", "")

        if new_location['country_name'] and new_location['country_name'] != "Not found":

            location = "{0}, {1}".format(state, new_location['country_name'])

        data = {}
        date = time.strftime('%B %d, %Y %H:%M:%S %p UTC')

        data['login_time'] = date
        data['location'] = location
        data['ip'] = ip_address
        data['device'] = "{0}/{1}".format(user_data['platform'], user_data['browser'])

        emailer = Email()
        email_temp = LoginEmail()

        message = email_temp.message_temp(data)
        subject = "New login to NMI"
        emailer.send_email(email, message, subject)
