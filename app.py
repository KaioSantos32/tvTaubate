from flask import Flask, render_template, request, redirect, session, flash, url_for
import pymongo
from pymongo import MongoClient
from passlib.hash import sha256_crypt

app = Flask(__name__, template_folder='templates', static_folder='assets')

app.secret_key='secretkeyonlyIKnow'


class User:
    def __init__(self,id,username, password):
        self.id = id
        self.username = username
        self.password = password

# Criando conexao com o banco de dados


cluster = MongoClient("mongodb://root1:root123@cluster0-shard-00-00.yrzqf.mongodb.net:27017,cluster0-shard-00-01.yrzqf.mongodb.net:27017,cluster0-shard-00-02.yrzqf.mongodb.net:27017/tvTaubate?ssl=true&replicaSet=atlas-b8b56u-shard-0&authSource=admin&retryWrites=true&w=majority")
#cluster = MongoClient("localhost", 27017)

db=cluster.tvTaubate
collection = db.usuarios



# Fim conexao com banco de dados


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar')
def registrar():
    return render_template('cadastro.html')


@app.route('/cria_cadastro', methods=['POST','GET'])
def cria_cadastro():

    id = request.form['useremail']
    username = request.form['username']
    # para encriptar se usa sha256_crypt.hash(request.form['password'])
    #o metodo sha256_crypt.encrypt(request.form['password']) sera abandonado em versoes futuras, deve-se usar .hash
    password = sha256_crypt.hash(request.form['password'])
    cadastro = {"_id": f"{id}", "username": f"{username}","password": f"{password}"}
    try:
        # Tenta cadastrar no banco
        collection.insert_one(cadastro)
        return redirect(url_for("login"))
    except pymongo.errors.DuplicateKeyError:
        # Caso o _id ja exi
        # sta, ele retorna esse erro acima
        # deverá ser tratado posteriormente com mensagem de "erro, Email ja cadastrado"
        # com javascript (ou alguma opção mais adequada)
        return redirect(url_for("registrar"))        
    

# LOGIN AREA
@app.route("/login", methods=['POST', 'GET'])
def login():
    return render_template('login.html')
   

@app.route('/autenticar', methods=['POST', ])
def autenticar():

    id = request.form['id']
    password = request.form['password']

    # Busco o perfil do usuario com base na entrada de id que ele colocou
    # '_id' é meu indice, nao pode se repetir
    resultado = collection.find({"_id": f"{id}"})
    
    for i in resultado:
        dbPass = i['password']
        dbAcc = i['_id']

        # Verifica se id existe no BD e se a senha criptografada é a mesma que o usuario
        # digitou

        accVerify = dbAcc == id

        # para verificar conta se usa sha256_crypt.verify([senha digitada],[senha armazenada])
        passVerify= sha256_crypt.verify(password,dbPass)

        if accVerify and passVerify:
            session['username'] = i['username']
            
            return redirect(url_for('perfil', nome = session['username']))
    else:
        return redirect('/login')
    

@app.route('/perfil/<nome>')
def perfil(nome):    
    if session["username"] == None:
        return redirect('/login')
    else:
        return render_template('perfil.html', nome=session['username'])

@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')

@app.route('/esqueci_senha')
def esqueci_senha():
    return render_template('fpassword.html')

@app.route("/modifica_senha", methods=['POST',])
def modifica_senha():
    return redirect('/login')

@app.route("/descobrir")
def descobrir():
    return render_template("descobrir.html")

@app.route("/sobre-nos")
def sobre_nos():
    return render_template("sobre_nos.html")

if __name__ == "__main__":
    app.run(debug=True)
