"""Delete Course"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteCourse(Common):
    """Class for DeleteCourse"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteCourse class"""
        self.postgresql_query = PostgreSQL()
        super(DeleteCourse, self).__init__()

    def delete_course(self):
        """
        This API is for Deleting Course
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
            description: Course IDs
            required: true
            schema:
              id: Delete Courses
              properties:
                course_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Course
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        course_ids = query_json["course_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_courses(course_ids):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Course successfully deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_courses(self, course_ids):
        """Delete Courses"""

        conditions = []

        conditions.append({
            "col": "course_id",
            "con": "in",
            "val": course_ids
            })

        if self.postgresql_query.delete('course', conditions):
            return 1

        return 0
