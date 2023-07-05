from flask import Blueprint, request
from flask.json import jsonify
from src.database import Comment, db
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required

from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

comments = Blueprint('comments', __name__, url_prefix='/api/v1/comments')


@comments.route('/', methods=['POST', 'GET'])
@jwt_required()
def get_or_create_comments():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        body = request.get_json().get('body', '')

        comment = Comment(body=body, user_id=current_user)
        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'id': comment.id,
            'body': comment.body,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at
        }), HTTP_201_CREATED
    else:
        comments = Comment.query.filter_by(user_id=current_user)
        data = []

        for comment in comments:
            data.append({
                'body': comment.body,
                'id': comment.id,
                'created_at': comment.created_at,
                'updated_at': comment.updated_at
            })
        return jsonify({
            'data': data
        }), HTTP_200_OK


@comments.get('/<int:id>')
@jwt_required()
def get_single_comment(id):
    current_user = get_jwt_identity()
    comment = Comment.query.filter_by(user_id=current_user, id=id).first()
    if not comment:
        return jsonify({
            'message': 'Comment not found'
        }), HTTP_404_NOT_FOUND

    return jsonify({
        'id': comment.id,
        'body': comment.body,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at
    }), HTTP_200_OK


@comments.delete('/<int:id>')
@jwt_required()
def delete_comment(id):
    current_user = get_jwt_identity()
    comment = Comment.query.filter_by(user_id=current_user, id=id).first()
    if not comment:
        return jsonify({
            'message': 'Comment not found'
        }), HTTP_404_NOT_FOUND

    db.session.delete(comment)
    db.session.commit()

    return jsonify({

    }), HTTP_204_NO_CONTENT
 