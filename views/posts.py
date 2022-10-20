from flask import Response, request
from flask_restful import Resource
from models import Post, db
from views import get_authorized_user_ids
import flask_jwt_extended

import json

def get_path():
    return request.host_url + 'api/posts/'

class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    @flask_jwt_extended.jwt_required()
    def get(self):
        # get posts created by one of these users:
        # print(get_authorized_user_ids(self.current_user))
        args = request.args
        limit = args.get('limit')
        if not limit:
            limit = 20
        elif not limit.isdigit() or int(limit) > 50:
            return Response(json.dumps({'message': 'Invalid limit'}), mimetype="application/json", status=400)
        authorized_ids = get_authorized_user_ids(self.current_user)
        posts = Post.query.filter(Post.user_id.in_(authorized_ids)).limit(limit).all()
        posts_json = [post.to_dict(user=self.current_user) for post in posts]
        return Response(json.dumps(posts_json), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new post based on the data posted in the body 
        body = request.get_json()
        print(body)
        if not body or not body.get('image_url'):
            return Response(json.dumps({'message': 'Invalid post (image_url is required)'}), mimetype="application/json", status=400)
        new_post = Post(
            image_url = body.get('image_url'),
            user_id = self.current_user.id,
            caption = body.get('caption'),
            alt_text = body.get('alt_text')
        )
        db.session.add(new_post)
        db.session.commit()
        new_post_json = new_post.to_dict()
        return Response(json.dumps(new_post_json), mimetype="application/json", status=201)
        
class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        
    @flask_jwt_extended.jwt_required()
    def patch(self, id):
        # update post based on the data posted in the body 
        body = request.get_json()
        print(body)
        post = Post.query.get(id)
        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid patch/update'}), mimetype="application/json", status=404)
        post.image_url = body.get('image_url') or post.image_url
        post.caption = body.get('caption') or post.caption
        post.alt_text = body.get('alt_text') or post.alt_text
        db.session.commit()

        post_json = post.to_dict()
        return Response(json.dumps(post_json), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete post where "id"=id
        post = Post.query.get(id)
        if not post:
            return Response(json.dumps({'message': 'Invalid delete (post does not exist)'}), mimetype="application/json", status=404)
        elif post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid delete (not your post)'}), mimetype="application/json", status=404)
            
        Post.query.filter_by(id=id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Post id={0} was successfully deleted'.format(id)}), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def get(self, id):
        # get the post based on the id
        post = Post.query.get(id)
        if not post:    # or not can_view_post(id, self.current_user):
            return Response(json.dumps({'message': 'Invalid get (id={0} is invalid)'.format(id)}), mimetype="application/json", status=404)
        elif post.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Invalid get (id={0} is invalid)'.format(id)}), mimetype="application/json", status=404)
        post_json = post.to_dict(user=self.current_user)
        return Response(json.dumps(post_json), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        PostListEndpoint, 
        '/api/posts', '/api/posts/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
    api.add_resource(
        PostDetailEndpoint, 
        '/api/posts/<int:id>', '/api/posts/<int:id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )