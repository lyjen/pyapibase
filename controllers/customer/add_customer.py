# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, too-many-locals, too-many-arguments, too-many-statements, too-many-instance-attributes
"""Invite"""
import string
import time
from flask import  request
from library.common import Common
from library.sha_security import ShaSecurity
from library.postgresql_queries import PostgreSQL
from library.emailer import Email
from templates.invitation import Invitation

class Invite(Common, ShaSecurity):
    """Class for Invite"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Invite class"""

        self.sha_security = ShaSecurity()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763

        super(Invite, self).__init__()

    # GET VESSEL FUNCTION
    def invitation(self):
        """
        This API is for Sending invitation
        ---
        tags:
          - User
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: userid
            in: header
            description: User ID
            required: true
            type: string
          - name: query
            in: body
            description: Invite
            required: true
            schema:
              id: Invite
              properties:
                first_name:
                    type: string
                last_name:
                    type: string
                middle_name:
                    type: string
                url:
                    type: string
                email:
                    type: string
                companies:
                    types: array
                    example: []
                roles:
                    types: array
                    example: []
                groups:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Sending invitation
        """
        # INIT DATA
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET REQUEST PARAMS
        email = query_json["email"]
        url = query_json["url"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # INIT IMPORTANT KEYS
        important_keys = {}
        important_keys['companies'] = []
        important_keys['roles'] = []
        important_keys['email'] = "string"
        important_keys['url'] = "string"

        # CHECK IMPORTANT KEYS IN REQUEST JSON
        if not self.check_request_json(query_json, important_keys):

            data["alert"] = "Invalid query, Missing parameter!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # CHECK INVITATION
        if self.check_invitation(email):
            data["alert"] = "Already invited!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        password = self.generate_password()

        # INSERT INVITATION
        account_id = self.insert_invitation(password, query_json)

        if not account_id:

            data = {}
            data['message'] = "Invalid email!"
            data['status'] = "Failed"

            return self.return_data(data)

        # SEND INVITATION
        self.send_invitation(email, password, url)

        data = {}
        data['message'] = "Invitation successfully sent!"
        data['status'] = "ok"

        return self.return_data(data)

    def check_invitation(self, email):
        """Check Invitation"""

        sql_str = "SELECT * FROM account WHERE "
        sql_str += " email = '" + email + "'"

        res = self.postgres.query_fetch_one(sql_str)

        if res:

            return res

        return 0

    def check_username(self, username):
        """Check Invitation"""

        sql_str = "SELECT * FROM account WHERE "
        sql_str += " username = '" + username + "'"

        res = self.postgres.query_fetch_one(sql_str)

        if res:

            return res

        return 0

    def insert_invitation(self, password, query_json):
        """Insert Invitation"""

        token = self.generate_token(True)

        companies = query_json['companies']
        roles = query_json['roles']
        groups = query_json['groups']

        data = query_json
        data = self.remove_key(data, "companies")
        data = self.remove_key(data, "roles")
        data = self.remove_key(data, "groups")

        username = "no_username_{0}".format(int(time.time()))
        if not self.check_username(username):
            username += self.random_str_generator(5)

        data['id'] = self.sha_security.generate_token(False)
        data['username'] = username
        data['token'] = token
        data['status'] = True
        data['state'] = False
        data['password'] = self.string_to_sha_plus(password)
        data['created_on'] = time.time()
        account_id = self.postgres.insert('account', data, 'id')

        if not account_id:
            return 0

        for company in companies:

            # ACCOUNT COMPANY
            temp = {}
            temp['account_id'] = account_id
            temp['company_id'] = company
            self.postgres.insert('account_company', temp)

        for role_id in roles:

            # ACCOUNT COMPANY
            temp = {}
            temp['account_id'] = account_id
            temp['role_id'] = role_id
            self.postgres.insert('account_role', temp)

        for group_id in groups:

            # ACCOUNT ESTABLISHMENT
            temp = {}
            temp['account_id'] = account_id
            temp['group_id'] = group_id
            temp['allow_access'] = True

            self.postgres.insert('account_groups', temp)

        return account_id

    def send_invitation(self, email, password, url):
        """Send Invitation"""

        email_temp = Invitation()
        emailer = Email()

        message = email_temp.invitation_temp(password, url)
        subject = "Invitation"
        emailer.send_email(email, message, subject)

        return 1

    def generate_password(self):
        """Generate Password"""

        char = string.ascii_uppercase
        char += string.ascii_lowercase
        char += string.digits

        return self.random_str_generator(8, char)
