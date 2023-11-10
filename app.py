# Importez les modules nécessaires
from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# Configuration de la base de données (SQLite pour cet exemple)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


# Modèle de données pour un utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)


# Modèle de données pour un ingrédient
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


# Modèle de données pour une recette
class Recette(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredient_ids = db.Column(db.String(200))  # Une chaîne JSON pour stocker les IDs des ingrédients


# Modèle de données pour un menu
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    entry_id = db.Column(db.Integer, nullable=False)
    main_dish_id = db.Column(db.Integer, nullable=False)
    dessert_id = db.Column(db.Integer, nullable=False)


# Créez les tables dans la base de données
with app.app_context():
    db.create_all()


# Endpoint pour créer un nouvel utilisateur
@app.route('/users/', methods=['POST'])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Utilisateur créé avec succès'}), 201
    else:
        return jsonify({'message': 'Données JSON incorrectes'}), 400


# Endpoint pour récupérer la liste de tous les utilisateurs
@app.route('/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username, 'password': user.password} for user in users]
    return jsonify(user_list)


# Endpoint pour supprimer un utilisateur de la liste des utilisateurs
@app.route('/users/', methods=['DELETE'])
def delete_user():
    username = request.form.get('username')
    users = User.query.filter_by(username=username)
    if username:
        for username in users:
            db.session.delete(username)
            db.session.commit()
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 201
    else:
        return jsonify({'message': 'Donnée JSON incorrectes'}), 400


# Endpoint pour créer un nouvel ingrédient
@app.route('/ingredients/', methods=['POST'])
def create_ingredient():
    name = request.form.get('name')
    if name:
        new_ingredient = Ingredient(name=name)
        db.session.add(new_ingredient)
        db.session.commit()
        return jsonify({'message': 'Ingrédient créé avec succès'}), 201
    else:
        return jsonify({'message': 'Données JSON incorrectes'}), 400


# Endpoint pour récupérer la liste de tous les ingrédients
@app.route('/ingredients/', methods=['GET'])
def get_ingredients():
    ingredients = Ingredient.query.all()
    ingredient_list = [{'id': ingredient.id, 'name': ingredient.name} for ingredient in ingredients]
    return jsonify(ingredient_list)


# Endpoint pour supprimer un ingrédient de la liste d'ingrédient
@app.route('/ingredients/', methods=['DELETE'])
def delete_user():
    name = request.form.get('name')
    ingredients = Ingredient.query.filter_by(name=name)
    if name:
        for name in ingredients:
            db.session.delete(name)
            db.session.commit()
        return jsonify({'message': 'Ingrédient supprimé avec succès'}), 201
    else:
        return jsonify({'message': 'Donnée JSON incorrectes'}), 400


# Endpoint pour créer une nouvelle recette
@app.route('/recette/', methods=['POST'])
def create_recette():
    name = request.form.get('name')
    if name:
        new_recette = Recette(name=name)
        db.session.add(new_recette)
        db.session.commit()
        return jsonify({'message': 'Recette créée avec succés'}), 201
    else:
        return jsonify({'message': 'Données JSON incorrectes'}), 400


# Endpoint pour récupérer la liste de toutes les recettes
@app.route('/recette/', methods=['GET'])
def get_recette():
    recette = Recette.query.all()
    recette_list = [{'id': recette.id, 'name': recette.name} for recette in recette]
    return jsonify(recette_list)


# Endpoint pour supprimer une recette de la liste de recette
@app.route('/recette/', methods=['DELETE'])
def delete_user():
    name = request.form.get('name')
    recettes = Recette.query.filter_by(name=name)
    if name:
        for name in recettes:
            db.session.delete(name)
            db.session.commit()
        return jsonify({'message': 'Recette supprimé avec succès'}), 201
    else:
        return jsonify({'message': 'Donnée JSON incorrectes'}), 400


# Endpoint pour créer un nouveau menu
@app.route('/menu/', methods=['POST'])
def create_menu():
    name = request.form.get('name')
    if name:
        new_menu = Menu(name=name)
        db.session.add(new_menu)
        db.session.commit()
        return jsonify({'message': 'Menu créé avec succés'}), 201
    else:
        return jsonify({'message': 'Données JSON incorrectes'}), 400


# Endpoint pour récupérer la liste de tous les menus
@app.route('/menu/', methods=['GET'])
def get_menu():
    menu = Menu.query.all()
    menu_list = [{'id': menu.id, 'name': menu.name} for menu in menu]
    return jsonify(menu_list)


# Endpoint pour supprimer un menu de la liste des menus
@app.route('/menu/', methods=['DELETE'])
def delete_user():
    name = request.form.get('name')
    menus = Menu.query.filter_by(name=name)
    if name:
        for name in menus:
            db.session.delete(name)
            db.session.commit()
        return jsonify({'message': 'Menu supprimé avec succès'}), 201
    else:
        return jsonify({'message': 'Donnée JSON incorrectes'}), 400



@app.route('/')
def base():
    return redirect(url_for("home"))


@app.route("/home/")
def home():
    return "home page"


if __name__ == "__main__":
    app.run(debug=True)
