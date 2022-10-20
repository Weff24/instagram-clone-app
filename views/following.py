from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json
import flask_jwt_extended

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # return all of the "following" records that the current user is following
        followings = Following.query.filter(Following.user_id == self.current_user.id).all()
        followings_json = [following.to_dict_following() for following in followings]
        return Response(json.dumps(followings_json), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "following" record based on the data posted in the body 
        body = request.get_json()
        print(body)

        if not body or not body.get('user_id'):
            return Response(json.dumps({'message': 'Invalid post (user_id is required)'}), mimetype="application/json", status=400)
        
        if type(body.get('user_id')) != int:
            return Response(json.dumps({'message': 'Invalid post (user_id must be an integer)'}), mimetype="application/json", status=400)

        user = User.query.get(body.get('user_id'))
        if not user:
            return Response(json.dumps({'message': 'Invalid post (user_id does not exist)'}), mimetype="application/json", status=404)

        if Following.query.filter(Following.user_id == self.current_user.id).filter(Following.following_id == body.get('user_id')).all():
            return Response(json.dumps({'message': 'Invalid post (already following user)'}), mimetype="application/json", status=400)

        new_following = Following(
            user_id = self.current_user.id,
            following_id = body.get('user_id')
        )
        db.session.add(new_following)
        db.session.commit()
        
        new_following_json = new_following.to_dict_following()
        return Response(json.dumps(new_following_json), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "following" record where "id"=id
        print(id)

        following = Following.query.get(id)
        if not following:
            return Response(json.dumps({'message': 'Invalid delete (following id does not exist)'}), mimetype="application/json", status=404)
        elif following.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid delete'}), mimetype="application/json", status=404)

        Following.query.filter_by(id=id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Following id={0} was successfully deleted'.format(id)}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
