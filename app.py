# Importez les modules nécessaires
from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de la base de données (SQLite pour cet exemple)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


# Modèle de données pour un utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)


# Modèle de données pour un ingrédient
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


# Modèle de données pour une recette
class Recette(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Entrée, Plat, Dessert
    ingredient = db.relationship('Ingredient', secondary='recette_ingredient', back_populates='recette')


# Modèle de données pour un menu
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    main_dish_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    dessert_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)


# Modèle de données pour la relation many-to-many entre Recette et Ingredient
recette_ingredient = db.Table('recette_ingredient',
                              db.Column('recette_id', db.Integer, db.ForeignKey('recette.id'), primary_key=True),
                              db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
                              db.Column('quantity', db.Float, nullable=False))


# Modèle pour la table Step
class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    recette_name = db.Column(db.String(100), db.ForeignKey('recette.name'), nullable=False)


# Modèle pour la table RecetteFavorite
class RecetteFavorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), db.ForeignKey('user.name'), nullable=False)
    recette_name = db.Column(db.String(100), db.ForeignKey('recette.name'), nullable=False)


# Créez les tables dans la base de données
with app.app_context():
    db.create_all()


# Endpoint pour créer un nouvel utilisateur
@app.route('/users/', methods=['POST'])
def create_user():
    username = request.form.get('username')
    if username:
        new_user = User(username=username)
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
def get_all_ingredients():
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
    type = request.form.get('type')
    ingredients_data = request.form.get('ingredients')  # Supposons que les données des ingrédients soient fournies
    # sous forme de chaîne JSON

    if name and type and ingredients_data:
        # Convertissez la chaîne JSON en une liste de dictionnaires
        ingredients_list = json.loads(ingredients_data)

        # Créez une nouvelle recette
        new_recette = Recette(name=name, type=type)

        # Ajoutez les ingrédients à la recette
        for ingredient_data in ingredients_list:
            ingredient_name = ingredient_data.get('name')
            quantity = ingredient_data.get('quantity')

            if ingredient_name and quantity:
                # Recherchez l'ingrédient existant ou créez-le s'il n'existe pas encore
                ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name)
                    db.session.add(ingredient)

                new_recette.ingredients.append(ingredient, {'quantity': quantity})

        # Ajoutez la recette à la base de données
        db.session.add(new_recette)
        db.session.commit()
        return jsonify({'message': 'Recette créée avec succés'}), 201
    else:
        return jsonify({'message': 'Données JSON incorrectes'}), 400


# Endpoint pour récupérer la liste de toutes les recettes
@app.route('/recette/', methods=['GET'])
def get_all_recette():
    recette = Recette.query.all()
    recette_list = [{'id': recette.id, 'type': recette.type, 'name': recette.name} for recette in recette]
    return jsonify(recette_list)


# Endpoint pour lister les étapes de conception d'une recette
@app.route('/recette/<str:recette_name>/steps/', methods=['GET'])
def get_recette_steps(recette_name):
    recette = Recette.query.get(recette_name)
    if recette:
        steps = Step.query.filter_by(recette_name=recette_name).all()
        steps_list = [{'step_id': step.id, 'description': step.description} for step in steps]
        return jsonify({'recette_name': recette.name, 'steps': steps_list})
    else:
        return jsonify({'message': 'Recette inexistante'}), 404


# Endpoint pour marquer/démarquer des recettes comme étant ses préférées
@app.route('/users/<str:user_name>/recette_favorite/', methods=['POST', 'DELETE'])
def manage_recette_favorite(user_name):
    user = User.query.get(user_name)
    if not user:
        return jsonify({'message': 'Utilisateur inconnu'}), 404

    recette_name = request.form.get('recette_name')

    if not recette_name:
        return jsonify({'message': 'Nom de la recette requis'}), 400

    recette = Recette.query.get(recette_name)
    if not recette:
        return jsonify({'message': 'Recette inexistante'}), 404

    if request.method == 'POST':
        # Ajouter la recette à la liste des recettes préférées de l'utilisateur
        recette_favorite = RecetteFavorite(user_name=user.name, recette_name=recette.name)
        db.session.add(recette_favorite)
        db.session.commit()
        return jsonify({'message': 'Recette ajoutée aux favories avec succès'}), 201
    elif request.method == 'DELETE':
        # Retirer la recette de la liste des recettes préférées de l'utilisateur
        recette_favorite = RecetteFavorite.query.filter_by(user_name=user.name, recette_name=recette.name).first()
        if recette_favorite:
            db.session.delete(recette_favorite)
            db.session.commit()
            return jsonify({'message': 'Recette supprimée des favories avec succès'}), 200
        else:
            return jsonify({'message': 'Recette inexistante dans favories'}), 404


# Endpoint pour dresser la liste de ses recettes préférées
@app.route('/users/<str:user_name>/recette_favorite/', methods=['GET'])
def get_recette_favorite(user_name):
    user = User.query.get(user_name)
    if not user:
        return jsonify({'message': 'Utilisateur inconnu'}), 404

    recette_favorite = (
        db.session.query(Recette)
        .join(RecetteFavorite, Recette.name == Recette.recette_name)
        .filter(RecetteFavorite.user_name == user.name)
        .all())

    if recette_favorite:
        recette_favorite_list = [{'recette_id': recette.id, 'name': recette.name, 'type': recette.type}
                                 for recette in recette_favorite]
        return jsonify({'user_name': user.name, 'recette_favorite': recette_favorite_list})
    else:
        return jsonify({'user_name': user.name, 'recette_favorite': []})


# Endpoint pour supprimer une recette de la liste de recette
@app.route('/recette/', methods=['DELETE'])
def delete_user():
    name = request.form.get('name')
    recette = Recette.query.filter_by(name=name)
    if name:
        for name in recette:
            db.session.delete(name)
            db.session.commit()
        return jsonify({'message': 'Recette supprimé avec succès'}), 201
    else:
        return jsonify({'message': 'Donnée JSON incorrectes'}), 400


# Endpoint pour créer un nouveau menu
@app.route('/menu/', methods=['POST'])
def create_menu():
    name = request.form.get('name')
    entry = request.form.get('entry')
    main_dish = request.form.get('main_dish')
    dessert = request.form.get('dessert')
    if name and entry and main_dish and dessert:
        new_menu = Menu(name=name, entry=entry, main_dish=main_dish, dessert=dessert)
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


if __name__ == "__main__":
    app.run(debug=True)
