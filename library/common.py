# pylint: disable=no-self-use, too-many-arguments, too-many-branches, too-many-public-methods, bare-except, unidiomatic-typecheck, no-member, anomalous-backslash-in-string
"""Common"""
import time
from datetime import datetime, timedelta
import re
import simplejson
import dateutil.relativedelta

from flask import jsonify
from library.postgresql_queries import PostgreSQL
from library.log import Log

class Common():
    """Class for Common"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Common class"""
        self.log = Log()
        self.epoch_default = 26763
        # INITIALIZE DATABASE INFO
        self.postgres = PostgreSQL()

    # RETURN DATA
    def return_data(self, data):
        """Return Data"""
        # RETURN
        return jsonify(
            data
        )

    # REMOVE KEY
    def remove_key(self, data, item):
        """Remove Key"""

        # CHECK DATA
        if item in data:

            # REMOVE DATA
            del data[item]

        # RETURN
        return data

    # VALIDATE TOKEN
    def validate_token(self, token, user_id):
        return 1
        """Validate Token"""
        # import datetime
        # import dateutil.relativedelta

        # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
        if not token:
            return 0

        # SET COLUMN FOR RETURN
        columns = ['username', 'update_on']

        # CHECK IF TOKEN EXISTS
        user_data = self.get_user_info(columns, "account", user_id, token)

        data = {}
        data['update_on'] = time.time() #datetime.fromtimestamp(time.time())

        condition = []
        temp_con = {}

        temp_con['col'] = 'id'
        temp_con['val'] = user_id
        temp_con['con'] = "="
        condition.append(temp_con)

        self.postgres = PostgreSQL()

        # self.postgres.update('account', data, condition)

        # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
        if user_data:

            dt1 = datetime.fromtimestamp(user_data['update_on'])
            dt2 = datetime.fromtimestamp(time.time())
            dateutil.relativedelta.relativedelta(dt2, dt1)

            rd1 = dateutil.relativedelta.relativedelta(dt2, dt1)
            # print(rd1.years, rd1.months, rd1.days, rd1.hours, rd1.minutes, rd1.seconds)

            if rd1.years or rd1.months or rd1.days or rd1.hours:

                return 0

            if rd1.minutes > 30:

                return 0

        else:

            return 0

        self.postgres.update('account', data, condition)

        # RETURN
        return 1

    # COUNT DATA
    def count_data(self, datas, column, item):
        """Return Data Count"""

        # INITIALIZE
        count = 0

        # LOOP DATAS
        for data in datas:

            # CHECK OF DATA
            if data[column] == item:

                # INCREASE COUNT
                count += 1

        # RETURN
        return count

    def set_return(self, datas):
        """Set Return"""
        ret_data = {}
        ret_data['data'] = []
        for data in datas:
            ret_data['data'].append(data['value'])

        return ret_data

    def check_request_json(self, query_json, important_keys):
        """Check Request Json"""
        query_json = simplejson.loads(simplejson.dumps(query_json))

        for imp_key in important_keys.keys():

            if type(query_json.get(imp_key)):

                if type(query_json[imp_key]) != type(important_keys[imp_key]):

                    return 0

            else:

                return 0

        return 1

    def limits(self, rows, limit, page):
        """Limits"""
        skip = int((page - 1) * limit)

        limit = skip + limit

        return rows[skip:limit]

    def param_filter(self, temp_datas, params, checklist):
        """Parameter Filter"""
        if not params:

            return temp_datas

        param_datas = []
        param_datas = temp_datas

        output = []

        i = 0

        for param in params:
            key = checklist[i]

            i += 1

            for data in param_datas:

                if self.filter_checker(str(param), str(data[key])):

                    output.append(data)

        return output

    def filter_checker(self, pattern, value):
        """Check Filter"""
        if '*' in pattern:
            pattern = pattern.replace('.', r'\.')
            if pattern == "*":
                pattern = "."

            if not pattern[0] == "*" and pattern != ".":
                pattern = "^" + str(pattern)

            if pattern[-1] == "*":
                pattern = pattern[:-1] + '+'

            if not pattern[-1] == "+" and pattern != ".":
                pattern = str(pattern) + '$'

            if pattern[0] == "*":
                pattern = '.?' + pattern[1:]

            pattern = pattern.replace('*', '.+')

            # print("pattern: ", pattern)

            try:

                if not re.findall(pattern, value, re.IGNORECASE):

                    return 0

            except:

                return 0

        else:

            if not value == pattern:

                return 0

        return 1

    def isfloat(self, data):
        """Check if float"""
        try:
            if data == "infinity":
                return False

            float(data)
        except ValueError:
            return False
        else:
            return True

    def isint(self, data):
        """Check if Integer"""
        try:
            if data == "infinity":
                return False

            tmp_data1 = float(data)
            tmp_data2 = int(tmp_data1)
        except ValueError:
            return False
        else:
            return tmp_data1 == tmp_data2

    def file_replace(self, filename):
        """ File Naming """

        file_name = filename.split(".")[0]

        if "_" in file_name:

            suffix = file_name.split("_")[-1]

            if suffix.isdigit():
                new_name = filename.replace(suffix, str(int(suffix) + 1))
            else:
                new_name = filename.replace(suffix, str(suffix+"_1"))
        else:
            new_name = filename.replace(file_name, str(file_name+"_1"))

        return new_name

    def format_filter(self, datas):
        """ Return Filter in Format """

        tmp = []

        for data in datas:

            tmp.append({
                "label": data,
                "value": data
            })

        return tmp

    def days_update(self, timestamp, count=0, add=False):
        """Days Update"""
        try:

            named_tuple = time.localtime(int(timestamp))

            # GET YEAR MONTH DAY
            year = int(time.strftime("%Y", named_tuple))
            month = int(time.strftime("%m", named_tuple))
            day = int(time.strftime("%d", named_tuple))

            # Date in tuple
            date_tuple = (year, month, day, 0, 0, 0, 0, 0, 0)

            local_time = time.mktime(date_tuple)
            orig = datetime.fromtimestamp(local_time)

            if add:

                new = orig + timedelta(days=count)

            else:

                new = orig - timedelta(days=count)

            return new.timestamp()

        except:

            return 0
