"""Update Course"""
import time

from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.sha_security import ShaSecurity

class UpdateCourse(Common):
    """Class for UpdateCourse"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateCourse class"""
        self.postgres = PostgreSQL()
        self.sha_security = ShaSecurity()
        super(UpdateCourse, self).__init__()

    def update_course(self):
        """
        This API is for Updating Course
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
            description: Update Course
            required: true
            schema:
              id: Update Course
              properties:
                course_id:
                    type: string
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
            description: Update Course
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

        if not self.edit_course(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Course successfully updated!"
        data['status'] = "ok"

        return self.return_data(data)

    def edit_course(self, query_json):
        """Update Course"""

        query_json['update_on'] = time.time()

        conditions = []

        conditions.append({
            "col": "course_id",
            "con": "=",
            "val": query_json['course_id']
            })

        data = self.remove_key(query_json, "course_id")

        if self.postgres.update('course', data, conditions):
            return 1

        return 0
