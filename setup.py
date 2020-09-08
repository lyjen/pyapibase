# pylint: disable=too-many-locals, line-too-long, too-many-statements, too-many-function-args, too-many-branches, too-many-instance-attributes, attribute-defined-outside-init, too-many-lines
"""Set Up"""
from __future__ import print_function
import os
import json
import csv
import time
import pathlib
from random import randrange
from configparser import ConfigParser

from library.config_parser import config_section_parser
from library.postgresql_queries import PostgreSQL
from library.sha_security import ShaSecurity
from library.log import Log

class Setup():
    """Class for Setup"""

    def __init__(self):
        """The constructor for Setup class"""
        self.sha_security = ShaSecurity()
        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()
        # CONFIG FILE
        self.config.read("config/config.cfg")
        self.log = Log()

    def main(self):
        """Main"""
        # time.sleep(30) # Don't Delete this is for Docker
        self.create_database()
        self.create_tables()
        self.create_default_entries()
        self.create_index()

    def create_database(self):
        """Create Database"""
        self.dbname = config_section_parser(self.config, "POSTGRES")['db_name']
        self.postgres.connection(True)
        self.postgres.create_database(self.dbname)
        self.postgres.close_connection()

    def create_tables(self):
        """Create Tables"""

        # OPEN CONNECTION
        self.postgres.connection()

        # ACCOUNT TABLE
        query_str = "CREATE TABLE account (id VARCHAR (1000) PRIMARY KEY,"
        query_str += " username VARCHAR (50) UNIQUE NOT NULL, password VARCHAR (355) NOT NULL,"
        query_str += " email VARCHAR (355) UNIQUE NOT NULL, first_name VARCHAR (1000),"
        query_str += " last_name VARCHAR (1000), address VARCHAR (1000), reset_token VARCHAR (355),"
        query_str += " status BOOLEAN DEFAULT true, reset_token_date BIGINT,"
        query_str += " created_on BIGINT NOT NULL, update_on BIGINT, last_login BIGINT)"

        print("Create table: account")
        if self.postgres.exec_query(query_str):
            self.log.info("Account table successfully created!")

        # ACCOUNT TOKEN TABLE
        query_str = "CREATE TABLE account_token ("
        query_str += " account_id VARCHAR (1000) REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " token VARCHAR (1000) NOT NULL,"
        query_str += " token_expire_date BIGINT NOT NULL,"
        query_str += " refresh_token VARCHAR (1000) NOT NULL,"
        query_str += " refresh_token_expire_date BIGINT NOT NULL,"
        query_str += " remote_addr VARCHAR (1000),"
        query_str += " platform VARCHAR (1000),"
        query_str += " browser VARCHAR (1000),"
        query_str += " version VARCHAR (1000),"
        query_str += " language VARCHAR (1000),"
        query_str += " string VARCHAR (1000),"
        query_str += " update_on BIGINT,"
        query_str += " created_on BIGINT NOT NULL,"
        query_str += " CONSTRAINT account_token_pkey PRIMARY KEY (account_id, token))"

        print("Create table: account_token")
        if self.postgres.exec_query(query_str):
            self.log.info("Account role table successfully created!")

        # ROLE TABLE
        query_str = "CREATE TABLE role (role_id VARCHAR (1000) PRIMARY KEY,"
        query_str += " role_name VARCHAR (355) UNIQUE NOT NULL,"
        query_str += " default_value BOOLEAN,"
        query_str += " role_details VARCHAR (1000),"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: role")
        if self.postgres.exec_query(query_str):
            self.log.info("Role table successfully created!")

        # PERMISSION TABLE
        query_str = "CREATE TABLE permission (permission_id VARCHAR (1000) PRIMARY KEY,"
        query_str += " permission_name VARCHAR (355) UNIQUE NOT NULL,"
        query_str += " permission_details VARCHAR (1000),"
        query_str += " default_value BOOLEAN,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: permission")
        if self.postgres.exec_query(query_str):
            self.log.info("Permission table successfully created!")

        # ROLE PERMISSION TABLE
        query_str = "CREATE TABLE role_permission ("
        query_str += " role_id VARCHAR (1000) REFERENCES role (role_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " permission_id VARCHAR (1000) REFERENCES permission (permission_id) ON UPDATE CASCADE,"
        query_str += " CONSTRAINT role_permission_pkey PRIMARY KEY (role_id, permission_id))"

        print("Create table: role_permission")
        if self.postgres.exec_query(query_str):
            self.log.info("Role permission table successfully created!")

        # ACCOUNT ROLE TABLE
        query_str = "CREATE TABLE account_role ("
        query_str += " account_id VARCHAR (1000) REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " role_id VARCHAR (1000) REFERENCES role (role_id) ON UPDATE CASCADE,"
        query_str += " CONSTRAINT account_role_pkey PRIMARY KEY (account_id, role_id))"

        print("Create table: account_role")
        if self.postgres.exec_query(query_str):
            self.log.info("Account role table successfully created!")

        # ACCOUNT LOGIN HISTORY TABLE
        query_str = "CREATE TABLE account_login_history ("
        query_str += " account_id VARCHAR (1000) REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " login_details jsonb, update_on BIGINT)"

        print("Create table: account_login_history")
        if self.postgres.exec_query(query_str):
            self.log.info("Account login history table successfully created!")

        # CREATE VIEW FOR USER
        query_str = """CREATE VIEW account_master AS
        SELECT a.id, a.username, a.email, a.password, a.status, a.first_name, a.last_name,
        a.address,(SELECT array_to_json(array_agg(role_perm))
        FROM (SELECT r.role_id, r.role_name, r.role_details, 
        (SELECT array_to_json(array_agg(p)) FROM permission p 
        INNER JOIN role_permission rp ON rp.permission_id = p.permission_id 
        WHERE rp.role_id = r.role_id) AS permissions FROM role r
        INNER JOIN account_role ar ON ar.role_id = r.role_id
        WHERE ar.account_id = a.id) AS role_perm) AS roles, a.created_on FROM account a"""

        print("Create table: account_master")
        if self.postgres.exec_query(query_str):
            self.log.info("Account Master view table successfully created!")

        # CLOSE CONNECTION
        self.postgres.close_connection()

    def create_default_entries(self):
        """Create Default Entries"""

        # +++++++++++++++++++++++++++ PERMISSION +++++++++++++++++++++++++++ #
        data = {}
        data['permission_id'] = self.sha_security.generate_token(False)
        data['permission_name'] = config_section_parser(self.config, "PERMISSION")['permission_name']
        data['permission_details'] = config_section_parser(self.config, "PERMISSION")['permission_details']
        data['default_value'] = True
        data['created_on'] = time.time()


        print("Create default permission: ", data['permission_name'])
        permission_id = self.postgres.insert('permission', data, 'permission_id')

        if permission_id:

            self.log.info("Default Permission successfully created!")

        else:

            sql_str = "SELECT * FROM permission WHERE permission_name='" + data['permission_name'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            permission_id = res['permission_id']

        for dta in range(1, 2):

            data1 = {}
            data1['permission_id'] = self.sha_security.generate_token(False)
            data1['permission_name'] = config_section_parser(self.config, "PERMISSION")['permission_name' + str(dta)]
            data1['permission_details'] = config_section_parser(self.config, "PERMISSION")['permission_details' + str(dta)]
            data1['default_value'] = True
            data1['created_on'] = time.time()

            print("Create default permission: ", data1['permission_name'])
            self.postgres.insert('permission', data1, 'permission_id')

        permission_name1 = config_section_parser(self.config, "PERMISSION")['permission_name1']
        sql_str = "SELECT * FROM permission WHERE permission_name='{0}'".format(permission_name1)
        res = self.postgres.query_fetch_one(sql_str)
        permission_id1 = res['permission_id']

        # --------------------------- PERMISSION --------------------------- #

        # +++++++++++++++++++++++++++ ROLE +++++++++++++++++++++++++++ #
        data = {}
        data['role_id'] = self.sha_security.generate_token(False)
        data['role_name'] = config_section_parser(self.config, "ROLE")['role_name']
        data['role_details'] = config_section_parser(self.config, "ROLE")['role_details']
        data['default_value'] = True
        data['created_on'] = time.time()

        data1 = {}
        data1['role_id'] = self.sha_security.generate_token(False)
        data1['role_name'] = config_section_parser(self.config, "ROLE")['role_name1']
        data1['role_details'] = config_section_parser(self.config, "ROLE")['role_details1']
        data1['default_value'] = True
        data1['created_on'] = time.time()

        role_id = self.postgres.insert('role', data, 'role_id')
        customer_role_id = self.postgres.insert('role', data1, 'role_id')


        if role_id:
            print("Default Role successfully created!")
        else:
            self.postgres.connection()

            sql_str = "SELECT * FROM role WHERE role_name='" + data['role_name'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            role_id = res['role_id']

            self.postgres.close_connection()

        if customer_role_id:
            print("Default Role successfully created!")
        else:
            self.postgres.connection()

            sql_str = "SELECT * FROM role WHERE role_name='" + data1['role_name'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            customer_role_id = res['role_id']

            self.postgres.close_connection()

        # --------------------------- ROLE --------------------------- #

        # +++++++++++++++++++++++++++ ADMIN ACCOUNT +++++++++++++++++++++++++++ #
        data = {}
        data['id'] = self.sha_security.generate_token(False)
        data['username'] = config_section_parser(self.config, "ADMIN1")['username']
        data['password'] = config_section_parser(self.config, "ADMIN1")['password']
        data['email'] = config_section_parser(self.config, "ADMIN1")['email']
        data['first_name'] = config_section_parser(self.config, "ADMIN1")['first_name']
        data['last_name'] = config_section_parser(self.config, "ADMIN1")['last_name']
        data['address'] = config_section_parser(self.config, "ADMIN1")['address']
        data['status'] = bool(config_section_parser(self.config, "ADMIN1")['status'])
        # data['token'] = self.sha_security.generate_token(False)
        data['created_on'] = time.time()
        data['update_on'] = time.time()

        print("Create default user: ", data['username'])
        account_id1 = self.postgres.insert('account', data, 'id')
        if account_id1:
            self.log.info("Default user successfully created!")
        else:

            sql_str = "SELECT id FROM account WHERE username='" + data['username'] + "'"

            res = self.postgres.query_fetch_one(sql_str)
            account_id1 = res['id']
        # --------------------------- ADMIN ACCOUNT --------------------------- #

        # +++++++++++++++++++++++++++ CUSTOMER ACCOUNT +++++++++++++++++++++++++++ #
        data = {}
        data['id'] = self.sha_security.generate_token(False)
        data['username'] = config_section_parser(self.config, "CUSTOMER1")['username']
        data['password'] = config_section_parser(self.config, "CUSTOMER1")['password']
        data['email'] = config_section_parser(self.config, "CUSTOMER1")['email']
        data['first_name'] = config_section_parser(self.config, "CUSTOMER1")['first_name']
        data['last_name'] = config_section_parser(self.config, "CUSTOMER1")['last_name']
        data['address'] = config_section_parser(self.config, "CUSTOMER1")['address']
        data['status'] = bool(config_section_parser(self.config, "CUSTOMER1")['status'])
        # data['token'] = self.sha_security.generate_token(False)
        data['created_on'] = time.time()
        data['update_on'] = time.time()

        print("Create default user: ", data['username'])
        customer1_id = self.postgres.insert('account', data, 'id')
        if customer1_id:
            self.log.info("Default user successfully created!")
        else:

            sql_str = "SELECT id FROM account WHERE username='" + data['username'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            customer1_id = res['id']
        # --------------------------- CUSTOMER ACCOUNT --------------------------- #

        # +++++++++++++++++++++++++++ ACCOUNT ROLE +++++++++++++++++++++++++++ #
        temp = {}
        temp['account_id'] = account_id1
        temp['role_id'] = role_id
        self.postgres.insert('account_role', temp)

        temp = {}
        temp['account_id'] = customer1_id
        temp['role_id'] = customer_role_id
        self.postgres.insert('account_role', temp)
        # --------------------------- ACCOUNT ROLE --------------------------- #

        # +++++++++++++++++++++++++++ ROLE PERMISSION +++++++++++++++++++++++++++ #
        temp = {}
        temp['role_id'] = role_id
        temp['permission_id'] = permission_id
        self.postgres.insert('role_permission', temp)

        temp = {}
        temp['role_id'] = customer_role_id
        temp['permission_id'] = permission_id1
        self.postgres.insert('role_permission', temp)
        # --------------------------- ROLE PERMISSION --------------------------- #

    def create_index(self):
        """ CREATE INDEXING """

        pass

if __name__ == '__main__':

    # INIT CONFIG
    CONFIG = ConfigParser()
    # CONFIG FILE
    CONFIG.read("config/config.cfg")

    SERVER_TYPE = config_section_parser(CONFIG, "SERVER")['server_type']

    if SERVER_TYPE != 'production':
        SETUP = Setup()
        SETUP.main()

    else:

        print("YOU'RE TRYING TO UPDATE LIVE SERVER!!!")
