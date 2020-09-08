"""Customer"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class Customer(Common):
    """Class for Customer"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Customer class"""
        self.postgres = PostgreSQL()
        super(Customer, self).__init__()

    # LOGIN FUNCTION
    def customer(self):
        """
        This API is for Getting all Customer
        ---
        tags:
          - Customer
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
          - name: limit
            in: query
            description: Limit
            required: true
            type: integer
          - name: page
            in: query
            description: Page
            required: true
            type: integer
        responses:
          500:
            description: Error
          200:
            description: Customer Information
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        page = int(request.args.get('page'))
        limit = int(request.args.get('limit'))

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        datas = self.get_customers(page, limit)
        datas['status'] = 'ok'

        return self.return_data(datas)


    def get_customers(self, page, limit):
        """Return Customers"""

        offset = int((page - 1) * limit)

        sql_str = "SELECT * FROM account a"
        sql_str += " LEFT JOIN account_role ar ON a.id = ar.account_id"
        sql_str += " LEFT JOIN role r ON r.role_id = ar.role_id"
        sql_str += " WHERE r.role_name='customer'"

        # COUNT
        count_str = "SELECT COUNT(*) FROM ({0}) as accounts".format(sql_str)
        count = self.postgres.query_fetch_one(count_str)

        #LIMIT
        sql_str += " LIMIT {0} OFFSET {1}".format(limit, offset)
        accounts = self.postgres.query_fetch_all(sql_str)

        # CHECK CustomerNAME
        if accounts:

            for account in accounts:
                if "no_username" in account['username']:
                    account['username'] = ""

                # REMOVE PASSWORD
                self.remove_key(account, "password")

        total_rows = count['count']
        total_page = int((total_rows + limit - 1) / limit)
        data = {}
        data['rows'] = accounts
        data['total_rows'] = total_rows
        data['total_page'] = total_page
        data['limit'] = limit
        data['page'] = page

        return data
