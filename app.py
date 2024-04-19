from flask import Flask, jsonify, request, session
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
api = Api(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_member_only = db.Column(db.Boolean, default=False)

db.create_all()

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return jsonify({'user_id': user.id, 'username': user.username}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return jsonify({'user_id': user.id, 'username': user.username}), 200
        else:
            return '', 401

class MemberOnlyIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            articles = Article.query.filter_by(is_member_only=True).all()
            articles_data = [{'id': article.id, 'title': article.title, 'content': article.content} for article in articles]
            return jsonify(articles_data), 200
        else:
            return jsonify({'message': 'Unauthorized access'}), 401

class MemberOnlyArticle(Resource):
    def get(self, id):
        user_id = session.get('user_id')
        if user_id:
            article = Article.query.filter_by(id=id, is_member_only=True).first()
            if article:
                return jsonify({'id': article.id, 'title': article.title, 'content': article.content}), 200
            else:
                return jsonify({'message': 'Article not found'}), 404
        else:
            return jsonify({'message': 'Unauthorized access'}), 401

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(MemberOnlyIndex, '/member_only_index')
api.add_resource(MemberOnlyArticle, '/member_only_article/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
