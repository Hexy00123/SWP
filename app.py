from flask import Flask, request, jsonify, make_response, send_file, render_template
import os
import json
import io

app = Flask(__name__)


@app.route('/', methods=['GET'])
def api_page():
    """
    API endpoint that returns the API page.

    Returns:
        str: The API page message.
    """
    return "API page"


if __name__ == '__main__':
    from routes import users, admins, locations, rating, comments

    app.register_blueprint(admins.admins_blueprint)
    app.register_blueprint(users.users_blueprint)
    app.register_blueprint(locations.locations_blueprint)
    app.register_blueprint(rating.rating_blueprint)
    app.register_blueprint(comments.comment_blueprint)

    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
