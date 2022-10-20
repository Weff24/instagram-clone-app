from flask import Response, request
from flask_restful import Resource
from models import LikePost, Post, db
import json
from views import get_authorized_user_ids
import flask_jwt_extended

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "like_post" based on the data posted in the body 
        body = request.get_json()
        print(body)

        if type(body.get('post_id')) != int:
            return Response(json.dumps({'message': 'Invalid post (post_id must be an integer)'}), mimetype="application/json", status=400)

        post = Post.query.get(body.get('post_id'))
        if not post:
            return Response(json.dumps({'message': 'Invalid post (post does not exist)'}), mimetype="application/json", status=404)
        
        if post.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Invalid post'}), mimetype="application/json", status=404)

        if LikePost.query.filter(LikePost.user_id == self.current_user.id).filter(LikePost.post_id == body.get('post_id')).all():
            return Response(json.dumps({'message': 'Invalid post (LikePost already exists)'}), mimetype="application/json", status=400)

        new_likepost = LikePost(
            user_id = self.current_user.id,
            post_id = body.get('post_id')
        )
        db.session.add(new_likepost)
        db.session.commit()

        new_likepost_json = new_likepost.to_dict()
        return Response(json.dumps(new_likepost_json), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "like_post" where "id"=id
        print(id)

        likepost = LikePost.query.get(id)
        if not likepost:
            return Response(json.dumps({'message': 'Invalid delete (like does not exist)'}), mimetype="application/json", status=404)
        elif likepost.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid delete'}), mimetype="application/json", status=404)

        LikePost.query.filter_by(id=id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Like id={0} successfully deleted'.format(id)}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/likes', 
        '/api/posts/likes/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/likes/<int:id>', 
        '/api/posts/likes/<int:id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
