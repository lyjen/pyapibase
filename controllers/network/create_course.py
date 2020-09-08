"""Create Course"""
import time

from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.sha_security import ShaSecurity

class CreateCourse(Common):
    """Class for CreateCourse"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateCourse class"""
        self.postgres = PostgreSQL()
        self.sha_security = ShaSecurity()
        super(CreateCourse, self).__init__()

    def create_course(self):
        """
        This API is for Creating Course
        ---
        tags:
          - Course
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
            description: Create Course
            required: true
            schema:
              id: Create Course
              properties:
                course_name:
                    type: string
                subject:
                    type: string
                description:
                    type: string
                requirements:
                    type: string
                status:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Create Course
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.insert_course(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Course successfully created!"
        data['status'] = "ok"

        return self.return_data(data)

    def insert_course(self, query_json):
        """Insert Course"""

        query_json['course_id'] = self.sha_security.generate_token(False)
        query_json['created_on'] = time.time()

        if self.postgres.insert('course', query_json, 'course_id'):
            return 1

        return 0
