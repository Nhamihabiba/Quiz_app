from flask import Flask ,render_template,url_for , request , g ,redirect , session
from database import connect_to_database, getdatabase
from werkzeug.security import generate_password_hash, check_password_hash #Cette fonction est utilisée pour générer un hash sécurisé à partir d'un mot de passe fourni. Lorsqu'un utilisateur crée un nouveau mot de passe, il est recommandé de le passer à cette fonction pour le hasher avant de le stocker dans une base de données ou un autre système de stockage
import os
# Cette fonction est utilisée pour vérifier si un mot de passe fourni correspond à un hash de mot de passe donné
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Définir une clé secrète pour les sessions

@app.route("/")
def index():
    user = get_current_user()
    db = getdatabase()

    # Récupérer toutes les questions
    question_cursor = db.execute("SELECT questions.id, questions.question_text, askers.name AS asker_name, teachers.name AS teacher_name FROM questions JOIN users AS askers ON askers.id = questions.asked_by_id JOIN users AS teachers ON teachers.id = questions.teacher_id")
    question_result = question_cursor.fetchall()
    
    # Passer les questions récupérées au template
    return render_template('home.html', user=user, question_result=question_result)

@app.route('/login', methods=["POST", "GET"])
def login():
    user = get_current_user()
    error = None
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password'] 
        db = getdatabase()
        fetchedperson_cursor = db.execute("SELECT * FROM users WHERE name = ?", [name])
        personfromdatabase = fetchedperson_cursor.fetchone()
        
        if personfromdatabase:
            if check_password_hash(personfromdatabase['password'], password):
                session['user'] = personfromdatabase['name']
                return redirect(url_for('index'))
            else:
                error = "Username or password did not match. Try again."
        else:
            error = "Username or password did not match. Try again."
   
    return render_template("login.html", user=user, error=error)


@app.route('/register', methods=["POST","GET"])
def register():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = getdatabase()
        name = request.form['name']
        password = request.form['password']

        user_fetcing_cursor = db.execute("select * from users where name = ?" , [name])
        existing_user = user_fetcing_cursor.fetchone()

        if existing_user:
            error = "Username already taken, please choose a different username."
            return render_template("register.html" , error = error)
        
        hashed_password = generate_password_hash(password)  # Utilisez la variable de mot de passe réelle
        db.execute("INSERT INTO users (name, password, teacher, admin) VALUES (?, ?, ?, ?)",
           [name, hashed_password, 0, 0])  # Utilisez le mot de passe haché
        db.commit()
        session['user'] = name
        return redirect(url_for('index'))
    return render_template("register.html" , user = user)


@app.teardown_appcontext #C'est un décorateur qui enregistre la fonction suivante pour être exécutée lorsque le contexte de l'application Flask est déchargé.
def close_database(error):
    if hasattr(g,'quizapp_db'):
        g.quizapp_db.close()

def get_current_user():#qui est utilisée pour récupérer les informations de l'utilisateur actuellement connecté à partir de la session
    user_result = None
    if 'user' in session:
        user = session['user']
        db = getdatabase()
        user_cursor = db.execute("select * from users where name = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route('/promote/<int:id>', methods=["POST", "GET"])
def promote(id):
    user = get_current_user()
    if request.method == "POST":
        db = getdatabase()
        db.execute("UPDATE users SET teacher = 1 WHERE id = ?", [id])
        db.commit()
        return redirect(url_for('allusers'))
    return redirect(url_for('allusers'))


@app.route('/allusers' ,methods=["POST" ,"GET"])
def allusers():
    user = get_current_user()
    db = getdatabase()
    user_cursor = db.execute("select * from users")
    allusers = user_cursor.fetchall()
    return render_template("allusers.html" , user=user , allusers=allusers)

@app.route('/askquestion' , methods= ["POST" , "GET"])
def askquestion():
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))
    db = getdatabase()
    if request.method == "POST":
        question = request.form['question_text']
        teacher = request.form['teacher']
        db.execute("insert into questions (question_text,asked_by_id , teacher_id) values ( ?,?,?)" , [question,user['id'], teacher])
        db.commit()
        return redirect(url_for('index'))


    teacher_cursor = db.execute("select * from users where teacher = 1")
    allteachers = teacher_cursor.fetchall()
    return render_template("askquestion.html" , user = user ,allteachers = allteachers )



@app.route('/ansewerquestion/<question_id>', methods=["POST", "GET"])
def ansewerquestion(question_id):
    user = get_current_user()
    db = getdatabase()

    if request.method == "POST":
        db.execute("UPDATE questions SET answer_text = ? WHERE id = ?", [request.form['answer_text'], question_id])
        db.commit()
        return redirect("unansweredquestions")

    question_cursor = db.execute("SELECT id, question_text FROM questions WHERE id = ?", [question_id])
    question = question_cursor.fetchone()
    return render_template("ansewerquestion.html", user=user, question=question)





@app.route('/unansweredquestions')
def unansweredquestions():
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))
    db = getdatabase()
    question_cursor = db.execute('SELECT questions.id, questions.question_text, users.name FROM questions JOIN users ON users.id = questions.asked_by_id WHERE questions.answer_text IS NULL AND questions.teacher_id = ?', [user['id']])
    allquestions = question_cursor.fetchall()
    return render_template("unansweredquestions.html", user=user, allquestions=allquestions)



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True) #Rechargement automatique du code ,Affichage des erreurs détaillées 