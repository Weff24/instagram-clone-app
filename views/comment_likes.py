from flask import Response, request
from flask_restful import Resource
from models import LikeComment, Comment, db
import json
from views import get_authorized_user_ids

class CommentLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "like_comment" based on the data posted in the body 
        body = request.get_json()
        print(body)

        if type(body.get('comment_id')) != int:
            return Response(json.dumps({'message': 'Invalid post (comment_id must be an integer)'}), mimetype="application/json", status=400)

        comment = Comment.query.get(body.get('comment_id'))
        if not comment:
            return Response(json.dumps({'message': 'Invalid post (comment does not exist)'}), mimetype="application/json", status=404)
        
        # if comment.user_id not in get_authorized_user_ids(self.current_user):
        #     return Response(json.dumps({'message': 'Invalid post'}), mimetype="application/json", status=404)

        if LikeComment.query.filter(LikeComment.user_id == self.current_user.id).filter(LikeComment.comment_id == body.get('comment_id')).all():
            return Response(json.dumps({'message': 'Invalid post (LikeComment already exists)'}), mimetype="application/json", status=400)

        new_likecomment = LikeComment(
            user_id = self.current_user.id,
            comment_id = body.get('comment_id')
        )
        db.session.add(new_likecomment)
        db.session.commit()

        new_likecomment_json = new_likecomment.to_dict()
        return Response(json.dumps(new_likecomment_json), mimetype="application/json", status=201)

class CommentLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "like_comment" where "id"=id
        print(id)

        likecomment = LikeComment.query.get(id)
        if not likecomment:
            return Response(json.dumps({'message': 'Invalid delete (like does not exist)'}), mimetype="application/json", status=404)
        elif likecomment.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid delete'}), mimetype="application/json", status=404)

        LikeComment.query.filter_by(id=id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Like id={0} successfully deleted'.format(id)}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        CommentLikesListEndpoint, 
        '/api/comments/likes', 
        '/api/comments/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        CommentLikesDetailEndpoint, 
        '/api/comments/likes/<int:id>', 
        '/api/comments/likes/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
