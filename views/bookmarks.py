from flask import Response, request
from flask_restful import Resource
from models import Bookmark, Post, db
import json
from views import get_authorized_user_ids
import flask_jwt_extended

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # get all bookmarks owned by the current user
        bookmarks = Bookmark.query.filter(Bookmark.user_id == self.current_user.id).all()
        bookmarks_json = [bookmark.to_dict() for bookmark in bookmarks]
        return Response(json.dumps(bookmarks_json), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()
        print(body)
        
        if not body or not body.get('post_id'):
            return Response(json.dumps({'message': 'Invalid post (post_id is required)'}), mimetype="application/json", status=400)

        if type(body.get('post_id')) == str and not body.get('post_id').isdigit():
            return Response(json.dumps({'message': 'Invalid post (post_id must be an integer)'}), mimetype="application/json", status=400)

        post = Post.query.get(body.get('post_id'))
        if not post:
            return Response(json.dumps({'message': 'Invalid post (post does not exist)'}), mimetype="application/json", status=404)

        if post.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Invalid post (unable to bookmark)'}), mimetype="application/json", status=404)

        if Bookmark.query.filter(Bookmark.user_id == self.current_user.id).filter(Bookmark.post_id == body.get('post_id')).all():
            return Response(json.dumps({'message': 'Invalid post (already bookmarked this post)'}), mimetype="application/json", status=400)

        new_bookmark = Bookmark(
            user_id = self.current_user.id,
            post_id = body.get('post_id')
        )
        db.session.add(new_bookmark)
        db.session.commit()

        new_bookmark_json = new_bookmark.to_dict()
        return Response(json.dumps(new_bookmark_json), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "bookmark" record where "id"=id
        print(id)

        bookmark = Bookmark.query.get(id)
        if not bookmark:
            return Response(json.dumps({'message': 'Invalid delete (bookmark id does not exist)'}), mimetype="application/json", status=404)
        elif bookmark.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Invalid delete'}), mimetype="application/json", status=404)

        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Bookmark id={0} successfully deleted'.format(id)}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<int:id>', 
        '/api/bookmarks/<int:id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
