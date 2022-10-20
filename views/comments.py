from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from views import get_authorized_user_ids
import flask_jwt_extended

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "Comment" based on the data posted in the body 
        body = request.get_json()
        print(body)

        if not body or not body.get('post_id') or not body.get('text'):
            return Response(json.dumps({'message': 'Invalid post (post_id and text required)'}), mimetype="application/json", status=400)

        if type(body.get('post_id')) != int:
            return Response(json.dumps({'message': 'Invalid post (post_id must be an integer)'}), mimetype="application/json", status=400)
        
        post = Post.query.get(body.get('post_id'))
        if not post:
            return Response(json.dumps({'message': 'Invalid post (post does not exist)'}), mimetype="application/json", status=404)
        
        if post.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Invalid post (unable to comment on post)'}), mimetype="application/json", status=404)

        new_comment = Comment(
            text = body.get('text'),
            user_id = self.current_user.id,
            post_id = body.get('post_id')
        )
        db.session.add(new_comment)
        db.session.commit()

        new_comment_json = new_comment.to_dict()
        return Response(json.dumps(new_comment_json), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "Comment" record where "id"=id
        print(id)

        comment = Comment.query.get(id)
        if not comment:
            return Response(json.dumps({'message': 'Invalid delete (comment does not exist)'}), mimetype="application/json", status=404)
        elif comment.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid delete'}), mimetype="application/json", status=404)


        Comment.query.filter_by(id=id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Comment id={0} successfully deleted'.format(id)}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
