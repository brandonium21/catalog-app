import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask_googlelogin import GoogleLogin
from flask import (Flask, render_template, Blueprint, request, url_for,
                  redirect, session, jsonify)
from flask_login import (UserMixin, login_required, login_user, logout_user,
                        current_user, LoginManager)


app = Flask(__name__)
app.config.from_object('config.development')
db = SQLAlchemy(app)
googlelogin = GoogleLogin(app)


def create_db():
    print('Creating Database...')
    db.create_all()
    print('Done!')


@googlelogin.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # User authentication information
    google_id = db.Column(db.String(500), nullable=False, server_default='')
    name = db.Column(db.String(255), nullable=False, server_default='')
    avatar = db.Column(db.String(500), nullable=False, server_default='')

    def __init__(self, google_id, name, avatar):
            self.google_id = google_id
            self.name = name
            self.avatar = avatar

    def __repr__(self):
        return '<User %r>' % self.name


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.String(500))
    category = db.Column(db.UnicodeText(120))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))

    def __init__(self, title, description, category, user_id):
            self.title = title
            self.description = description
            self.category = category
            self.user_id = user_id

    def __repr__(self):
        return '<Item %r>' % self.title

    def to_json(self):
        return dict(title=str(self.title),
                    description=str(self.description),
                    category=str(self.category))


# Show all Items
@app.route('/', methods=['GET'])
def home():
    items = Item.query.all()
    categories = ['Soccer', 'Basketball', 'Baseball', 'Football', 'Hockey']
    return render_template('pages/home.html', items=items,
                          categories=categories,
                          login=googlelogin.login_url(approval_prompt='force'))


# Show Filtered Items
@app.route('/<filter>', methods=['GET'])
def home_filter(filter=None):
    filter_c = filter.encode('utf8')
    print filter
    items = Item.query.all()
    categories = ['Soccer', 'Basketball', 'Baseball', 'Football', 'Hockey']
    return render_template('pages/home.html', items=items,
                          categories=categories,
                          login=googlelogin.login_url(approval_prompt='force'),
                          filter=filter_c)


# Delete Item
@app.route('/delete/<item>', methods=['GET'])
@login_required
def delete(item):
    item_object = Item.query.filter_by(id=item).first()
    if current_user.id == item_object.user_id:
        db.session.delete(item_object)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('unauthorized.html')


# Edit Item
@app.route('/edit', methods=['POST'])
@login_required
def edit():
    if request.method == 'POST':
        item = request.form['item_id']
        item_object = Item.query.filter_by(id=item).first()
        if current_user.id == item_object.user_id:
            item_object.title = request.form['title']
            item_object.description = request.form['description']
            item_object.category = request.form['category']
            db.session.commit()
            loc = item + '-info'
            return redirect(url_for('home', _anchor=loc))
        return render_template('unauthorized.html')


# Add Item
@app.route('/add', methods=['POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        item = Item(title=title, description=description,
                    category=category, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('home'))


# Filter Items
@app.route('/filterb/<filter_by>', methods=['GET'])
def filter(filter_by):
    return redirect(url_for('home_filter', filter=filter_by))


# Show Item database as json
@app.route('/json')
def show_json():
    list_items = []
    items = Item.query.all()
    for item in items:
        print item.to_json()
        list_items.append(item.to_json())
    return json.dumps(list_items)


# logout
@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return render_template('pages/logout.html')


# login and/or create user
@app.route('/oauth2callback')
@googlelogin.oauth2callback
def create_or_update_user(token, userinfo, **params):
    user = User.query.filter_by(google_id=userinfo['id']).first()
    print 'blaj'
    print userinfo['id']
    if user:
        user.name = userinfo['name']
        user.avatar = userinfo['picture']
    else:
        user = User(google_id=userinfo['id'],
                    name=userinfo['name'],
                    avatar=userinfo['picture'])
    db.session.add(user)
    db.session.commit()
    user1 = User.query.filter_by(google_id=userinfo['id']).first()
    print user1
    login_user(user1)
    return redirect(url_for('home'))


if __name__ == '__main__':
    create_db()
    app.run()
