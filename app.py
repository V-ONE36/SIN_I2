# Importez les modules nécessaires
from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Crée une instance de l'application Flask.

# Configuration de la base de données (SQLite pour cet exemple)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Configure l'URI de la base de données. Dans cet exemple, SQLite est utilisé avec un fichier appelé "database.db".
# Cette configuration spécifie comment se connecter à la base de données.
db = SQLAlchemy(app)
# Crée une instance de SQLAlchemy, qui est une extension Flask pour la gestion des bases de données.
# L'instance de la base de données est associée à l'application Flask créée précédemment.


# Modèle de données pour un utilisateur
class User(db.Model):
    # Définition de la classe User qui représente la table des utilisateurs dans la base de données.
    id = db.Column(db.Integer, primary_key=True)
    # Colonne "id" de type entier (Integer) et clé primaire (primary_key=True).
    # Chaque utilisateur aura un identifiant unique.
    name = db.Column(db.String(80), unique=True, nullable=False)
    # Colonne "name" de type chaîne de caractères (String) d'une longueur maximale de 80 caractères.
    # La contrainte unique=True garantit que chaque nom d'utilisateur est unique dans la base de données.
    # La contrainte nullable=False indique que ce champ ne peut pas être vide.


# Modèle de données pour un ingrédient
class Ingredient(db.Model):
    # Définit un modèle de données pour un ingrédient dans la base de données.
    id = db.Column(db.Integer, primary_key=True)
    # 'id': Champ entier servant de clé primaire pour chaque ingrédient.
    name = db.Column(db.String(100), unique=True, nullable=False)
    # 'name': Champ de texte pour stocker le nom de l'ingrédient. Il doit être unique et non nullable.
    recettes = db.relationship('Recette', secondary='recette_ingredient', back_populates='ingredients')
    # 'recettes': Relation many-to-many avec le modèle 'Recette'. Cela est défini par la table
    # de liaison 'recette_ingredient'.
    # 'back_populates' assure que la relation est bidirectionnelle, permettant la navigation depuis 'Recette'.


# Modèle de données pour une recette
class Recette(db.Model):
    # Définit un modèle de données pour une recette dans la base de données.
    id = db.Column(db.Integer, primary_key=True)
    # 'id': Champ entier servant de clé primaire pour chaque recette.
    name = db.Column(db.String(100), nullable=False)
    # 'name': Champ de texte pour stocker le nom de la recette. Il est non nullable.
    type = db.Column(db.String(20), nullable=False)
    # 'type': Champ de texte pour spécifier le type de recette (Entrée, Plat, Dessert). Il est non nullable.
    ingredients = db.relationship('Ingredient', secondary='recette_ingredient', back_populates='recettes')
    # 'ingredients': Relation many-to-many avec le modèle 'Ingredient' à travers la table 'recette_ingredient'.
    # 'back_populates' assure que la relation est bidirectionnelle, permettant la navigation depuis 'Ingredient'.


# Modèle de données pour un menu
class Menu(db.Model):
    # Définit un modèle de données pour un menu dans la base de données.
    id = db.Column(db.Integer, primary_key=True)
    # 'id': Champ entier servant de clé primaire pour chaque menu.
    name = db.Column(db.String(100), nullable=False)
    # 'name': Champ de texte pour stocker le nom du menu. Il est non nullable.
    entry_id = db.Column(db.Integer, db.ForeignKey('recette.id'), nullable=False)
    main_dish_id = db.Column(db.Integer, db.ForeignKey('recette.id'), nullable=False)
    dessert_id = db.Column(db.Integer, db.ForeignKey('recette.id'), nullable=False)
    # - 'entry_id', 'main_dish_id', 'dessert_id': Champs entiers représentant les clés étrangères vers les recettes
    # correspondantes (entrée, plat principal, dessert).
    # Remarque : Les clés étrangères sont liées aux clés primaires de la table 'Recette'.


# Modèle de données pour la relation many-to-many entre Recette et Ingredient
recette_ingredient = db.Table('recette_ingredient',
                              # Définit une table de liaison many-to-many entre les tables 'Recette' et 'Ingredient'.
                              db.Column('recette_id', db.Integer, db.ForeignKey('recette.id'), primary_key=True),
                              # 'recette_id': Champ entier représentant la clé étrangère vers la table 'Recette'.
                              db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
                              # 'ingredient_id': Champ entier représentant la clé étrangère vers la table 'Ingredient'.
                              db.Column('quantity', db.Float, nullable=False),
                              db.relationship('Recette', back_populates='ingredients'),
                              db.relationship('Ingredient', back_populates='recettes')
                              )
# 'quantity': Champ float représentant la quantité de l'ingrédient dans la recette.
# 'primary_key=True': Indique que la combinaison des deux clés étrangères est la clé primaire de cette table de liaison.
# Remarque : Cette table est utilisée pour représenter la relation many-to-many entre les recettes et les ingrédients.
# Elle contient des informations supplémentaires comme la quantité d'un ingrédient dans une recette.


# Modèle pour la table Step
class Step(db.Model):
    # Modèle de données pour représenter les étapes d'une recette.
    id = db.Column(db.Integer, primary_key=True)
    # 'id': Champ entier servant de clé primaire pour la table des étapes.
    description = db.Column(db.Text, nullable=False)
    # 'description': Champ texte représentant la description d'une étape de recette.
    recette_name = db.Column(db.String(100), db.ForeignKey('recette.name'), nullable=False)
    # 'recette_name': Champ de texte servant de clé étrangère vers le nom d'une recette.
# Remarque : Le champ 'recette_name' est lié à la colonne 'name' dans la table 'Recette'.
# Cela établit une relation entre les étapes et les recettes, où chaque étape est associée à une recette spécifique.


# Modèle pour la table RecetteFavorite
class RecetteFavorite(db.Model):
    # Modèle de données pour représenter les recettes favorites d'un utilisateur.
    id = db.Column(db.Integer, primary_key=True)
    # 'id': Champ entier servant de clé primaire pour la table des recettes favorites.
    user_name = db.Column(db.String(80), db.ForeignKey('user.name'), nullable=False)
    # 'user_name': Champ de texte servant de clé étrangère vers le nom d'un utilisateur.
    recette_name = db.Column(db.String(100), db.ForeignKey('recette.name'), nullable=False)
    # 'recette_name': Champ de texte servant de clé étrangère vers le nom d'une recette.
# Remarque : Les champs 'user_name' et 'recette_name' sont liés aux colonnes 'name' dans les tables 'User' et 'Recette'
# respectivement.
# Cela établit une relation où chaque entrée dans la table des recettes favorites est associée à un utilisateur et
# une recette spécifiques.


# Cette portion de code crée toutes les tables définies dans les modèles de données
# (User, Ingredient, Recette, Menu, Step, RecetteFavorite)
# dans la base de données. Cela est réalisé en utilisant la méthode create_all()
# du SQLAlchemy instance (db) associée à l'application Flask.
with app.app_context():
    # 'with app.app_context()': Crée un contexte d'application Flask, nécessaire pour effectuer
    # des opérations liées à l'application, comme la création de tables dans la base de données.
    db.create_all()
    # 'db.create_all()': Cette méthode analyse tous les modèles de données (représentés par des classes) définis dans le
    # code et crée les tables correspondantes dans la base de données. Si les tables existent déjà,
    # cette opération n'a aucun effet.


# Endpoint pour créer un nouvel utilisateur
@app.route('/users/', methods=['POST'])
def create_user():
    username = request.form.get('username')
    # Récupère le nom d'utilisateur à partir des données du formulaire dans la requête
    if username:
        # Vérifie si le nom d'utilisateur est fourni
        new_user = User(name=username)
        # Crée une nouvelle instance de la classe User avec le nom d'utilisateur fourni
        db.session.add(new_user)
        # Ajoute le nouvel utilisateur à la session de la base de données
        db.session.commit()
        # Effectue la validation de la session en ajoutant l'utilisateur à la base de données
        return jsonify({'message': 'Utilisateur créé avec succès'}), 201
        # Retourne une réponse JSON indiquant que l'utilisateur a été créé avec succès,
        # avec le code de statut HTTP 201 (Created)
    else:
        return jsonify({'message': 'Données incorrectes'}), 400
    # Retourne une réponse JSON indiquant que les données fournies sont incorrectes,
    # avec le code de statut HTTP 400 (Bad Request)


# Endpoint pour récupérer la liste de tous les utilisateurs
@app.route('/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    # Récupère tous les utilisateurs de la base de données
    user_list = [{'id': user.id, 'username': user.name} for user in users]
    # Crée une liste de dictionnaires contenant l'ID et le nom d'utilisateur de chaque utilisateur
    return jsonify(user_list)
    # Retourne la liste des utilisateurs sous forme de réponse JSON


# Endpoint pour supprimer un utilisateur de la liste des utilisateurs
@app.route('/users/', methods=['DELETE'])
def delete_user():
    username = request.form.get('username')
    # Récupère le nom d'utilisateur à partir des données du formulaire de la requête DELETE
    if username:
        # Vérifie si le nom d'utilisateur est fourni
        user = User.query.filter_by(name=username).first()
        # Recherche l'utilisateur dans la base de données par le nom d'utilisateur
        if user:
            # Si l'utilisateur est trouvé, le supprime de la base de données
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Utilisateur supprimé avec succès'}), 201
        else:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404
            # Si l'utilisateur n'est pas trouvé, retourne une réponse indiquant
            # que l'utilisateur n'a pas été trouvé (code 404)
    else:
        return jsonify({'message': 'Données incorrectes'}), 400
        # Si le nom d'utilisateur n'est pas fourni dans la requête,
        # retourne une réponse indiquant des données incorrectes (code 400)


# Endpoint pour créer un nouvel ingrédient
@app.route('/ingredients/', methods=['POST'])
def create_ingredient():
    name = request.form.get('name')
    # Récupère le nom de l'ingrédient à partir des données du formulaire de la requête POST
    if name:
        # Vérifie si le nom de l'ingrédient est fourni
        new_ingredient = Ingredient(name=name)
        # Crée un nouvel objet Ingredient avec le nom fourni
        db.session.add(new_ingredient)
        # Ajoute le nouvel ingrédient à la session de base de données
        db.session.commit()
        # Valide les changements en effectuant un commit dans la base de données
        return jsonify({'message': 'Ingrédient créé avec succès'}), 201
        # Retourne une réponse JSON indiquant que l'ingrédient a été créé avec succès avec un code 201
    else:
        return jsonify({'message': 'Données incorrectes'}), 400
        # Si le nom de l'ingrédient n'est pas fourni dans la requête,
        # retourne une réponse indiquant des données incorrectes (code 400)


# Endpoint pour récupérer la liste de tous les ingrédients
@app.route('/ingredients/', methods=['GET'])
def get_all_ingredients():
    ingredients = Ingredient.query.all()
    # Récupère tous les objets Ingredient de la base de données
    ingredient_list = [{'id': ingredient.id, 'name': ingredient.name} for ingredient in ingredients]
    # Crée une liste de dictionnaires contenant l'id et le nom de chaque ingrédient
    return jsonify(ingredient_list)
    # Retourne une réponse JSON contenant la liste des ingrédients


# Endpoint pour supprimer un ingrédient de la liste d'ingrédient
@app.route('/ingredients/', methods=['DELETE'])
def delete_ingredient():
    name = request.form.get('name')
    # Récupère le nom de l'ingrédient à supprimer depuis la requête
    if name:
        # Vérifie si le nom de l'ingrédient est fourni
        ingredient = Ingredient.query.filter_by(name=name).first()
        # Recherche l'objet Ingredient dans la base de données avec le nom spécifié
        if ingredient:
            # Supprime l'objet Ingredient de la base de données
            db.session.delete(ingredient)
            db.session.commit()
            return jsonify({'message': 'Ingrédient supprimé avec succès'}), 201
        else:
            return jsonify({'message': 'Ingrédient non trouvé'}), 404
    else:
        return jsonify({'message': 'Données incorrectes'}), 400


# Endpoint pour créer une nouvelle recette
@app.route('/recettes/', methods=['POST'])
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
                    db.session.commit()

                new_recette.ingredients.append({'ingredient': ingredient, 'quantity': quantity})

        # Ajoutez la recette à la base de données
        db.session.add(new_recette)
        db.session.commit()
        return jsonify({'message': 'Recette créée avec succès'}), 201
    else:
        return jsonify({'message': 'Données incorrectes'}), 400


# Endpoint pour récupérer la liste de toutes les recettes
@app.route('/recettes/', methods=['GET'])
def get_all_recette():
    recettes = Recette.query.all()
    recette_list = [{'id': recette.id, 'type': recette.type, 'name': recette.name} for recette in recettes]
    return jsonify(recette_list)


# Endpoint pour créer une nouvelle étape pour une recette
@app.route('/recettes/<string:recette_name>/steps/', methods=['POST'])
def create_recette_step(recette_name):
    recette = Recette.query.filter_by(name=recette_name).first()
    # Recherche la recette dans la base de données avec le nom spécifié

    if recette:
        description = request.form.get('description')
        # Récupère la description de l'étape depuis la requête POST

        if description:
            new_step = Step(description=description, recette_name=recette_name)
            # Crée une nouvelle étape associée à la recette spécifiée

            db.session.add(new_step)
            db.session.commit()
            # Ajoute la nouvelle étape à la base de données

            return jsonify({'message': 'Étape ajoutée avec succès'}), 201
            # Retourne une réponse JSON indiquant que l'étape a été ajoutée avec succès
        else:
            return jsonify({'message': 'Description manquante'}), 400
            # Retourne une réponse JSON indiquant que la description de l'étape est manquante
    else:
        return jsonify({'message': 'Recette inexistante'}), 404
        # Retourne une réponse JSON indiquant que la recette n'a pas été trouvée


# Endpoint pour lister les étapes de conception d'une recette
@app.route('/recettes/<string:recette_name>/steps/', methods=['GET'])
def get_recette_steps(recette_name):
    recette = Recette.query.filter_by(name=recette_name).first()
    # Recherche la recette dans la base de données avec le nom spécifié
    if recette:
        steps = Step.query.filter_by(recette_name=recette_name).all()
        # Recherche toutes les étapes associées à la recette
        steps_list = [{'step_id': step.id, 'description': step.description} for step in steps]
        # Crée une liste de dictionnaires représentant les étapes
        return jsonify({'recette_name': recette.name, 'steps': steps_list}), 201
        # Retourne une réponse JSON contenant le nom de la recette et la liste des étapes
    else:
        # Retourne une réponse JSON indiquant que la recette n'a pas été trouvée
        return jsonify({'message': 'Recette inexistante'}), 404


# Endpoint pour marquer/démarquer des recettes comme étant ses préférées
@app.route('/users/<string:user_name>/recette_favorite/', methods=['POST', 'DELETE'])
def manage_recette_favorite(user_name):
    user = User.query.filter_by(name=user_name).first()
    # Recherche l'utilisateur dans la base de données avec le nom spécifié
    if not user:
        return jsonify({'message': 'Utilisateur inconnu'}), 404
        # Retourne une réponse JSON indiquant que l'utilisateur n'a pas été trouvée

    recette_name = request.form.get('recette_name')
    # Récupère le nom de la recette depuis la requête
    
    if not recette_name:
        return jsonify({'message': 'Nom de la recette requis'}), 400

    recette = Recette.query.filter_by(name=recette_name).first()
    # Recherche la recette dans la base de données avec le nom spécifié
    if not recette:
        return jsonify({'message': 'Recette inexistante'}), 404

    if request.method == 'POST':
        # Ajouter la recette à la liste des recettes préférées de l'utilisateur
        recette_favorite = RecetteFavorite(user_name=user.name, recette_name=recette.name)
        db.session.add(recette_favorite)
        db.session.commit()
        return jsonify({'message': 'Recette ajoutée aux favoris avec succès'}), 201
    elif request.method == 'DELETE':
        # Retirer la recette de la liste des recettes préférées de l'utilisateur
        recette_favorite = RecetteFavorite.query.filter_by(user_name=user.name, recette_name=recette.name).first()
        if recette_favorite:
            db.session.delete(recette_favorite)
            db.session.commit()
            return jsonify({'message': 'Recette supprimée des favoris avec succès'}), 200
        else:
            return jsonify({'message': 'Recette inexistante dans les favoris'}), 404


# Endpoint pour dresser la liste de ses recettes préférées
@app.route('/users/<string:user_name>/recette_favorite/', methods=['GET'])
def get_recette_favorite(user_name):
    user = User.query.filter_by(name=user_name).first()
    # Recherche l'utilisateur dans la base de données avec le nom spécifié
    if not user:
        return jsonify({'message': 'Utilisateur inconnu'}), 404
        # Retourne une réponse JSON indiquant que l'utilisateur n'a pas été trouvé

    recette_favorite = (
        db.session.query(Recette)
        .join(RecetteFavorite, Recette.name == RecetteFavorite.recette_name)
        .filter(RecetteFavorite.user_name == user.name)
        .all())
    # Recherche les recettes favorites de l'utilisateur en utilisant une jointure

    if recette_favorite:
        recette_favorite_list = [{'recette_id': recette.id, 'name': recette.name, 'type': recette.type}
                                 for recette in recette_favorite]
        # Crée une liste de dictionnaires représentant les recettes favorites de l'utilisateur
        return jsonify({'user_name': user.name, 'recette_favorite': recette_favorite_list})
        # Retourne une réponse JSON contenant le nom de l'utilisateur et la liste des recettes favorites
    else:
        return jsonify({'user_name': user.name, 'recette_favorite': []})
        # Retourne une réponse JSON indiquant que l'utilisateur n'a pas de recettes favorites


# Endpoint pour supprimer une recette de la liste de recette
@app.route('/recettes/', methods=['DELETE'])
def delete_recette():
    name = request.form.get('name')
    # Récupère le nom de la recette à supprimer à partir des données du formulaire
    if name:
        recette = Recette.query.filter_by(name=name).first()
        # Recherche la recette dans la base de données avec le nom spécifié
        if recette:
            # Supprime la recette de la base de données
            db.session.delete(recette)
            db.session.commit()
            return jsonify({'message': 'Recette supprimée avec succès'}), 201
            # Retourne une réponse JSON indiquant que la recette a été supprimée avec succès
        else:
            return jsonify({'message': 'Recette non trouvée'}), 404
            # Retourne une réponse JSON indiquant que la recette n'a pas été trouvée
    else:
        return jsonify({'message': 'Données incorrectes'}), 400
        # Retourne une réponse JSON indiquant que les données du formulaire sont incorrectes


# Endpoint pour créer un nouveau menu
@app.route('/menus/', methods=['POST'])
def create_menu():
    name = request.form.get('name')
    entry = request.form.get('entry')
    main_dish = request.form.get('main_dish')
    dessert = request.form.get('dessert')
    # Récupère les données du formulaire pour créer un nouveau menu
    if name and entry and main_dish and dessert:
        new_menu = Menu(name=name, entry=entry, main_dish=main_dish, dessert=dessert)
        # Crée un nouvel objet Menu avec les données du formulaire
        db.session.add(new_menu)
        db.session.commit()
        # Ajoute le nouveau menu à la base de données
        return jsonify({'message': 'Menu créé avec succès'}), 201
        # Retourne une réponse JSON indiquant que le menu a été créé avec succès
    else:
        return jsonify({'message': 'Données incorrectes'}), 400
        # Retourne une réponse JSON indiquant que les données du formulaire sont incorrectes


# Endpoint pour récupérer la liste de tous les menus
@app.route('/menus/', methods=['GET'])
def get_menu():
    menus = Menu.query.all()
    # Récupère tous les menus de la base de données
    menu_list = [{'id': menu.id, 'name': menu.name} for menu in menus]
    # Crée une liste de dictionnaires représentant chaque menu
    return jsonify(menu_list)
    # Retourne une réponse JSON contenant la liste des menus


# Endpoint pour supprimer un menu de la liste des menus
@app.route('/menus/', methods=['DELETE'])
def delete_menu():
    name = request.form.get('name')
    # Récupère le nom du menu à partir des données de la requête
    if name:
        # Vérifie si le nom du menu est fourni
        menu = Menu.query.filter_by(name=name).first()
        # Recherche le menu par son nom dans la base de données
        if menu:
            # Vérifie si le menu existe
            db.session.delete(menu)
            db.session.commit()
            # Supprime le menu de la base de données
            return jsonify({'message': 'Menu supprimé avec succès'}), 201
            # Retourne une réponse JSON indiquant que le menu a été supprimé avec succès
        else:
            return jsonify({'message': 'Menu non trouvé'}), 404
            # Retourne une réponse JSON indiquant que le menu n'a pas été trouvé
    else:
        return jsonify({'message': 'Données incorrectes'}), 400
        # Retourne une réponse JSON indiquant que les données fournies sont incorrectes


if __name__ == "__main__":
    app.run(debug=True)
