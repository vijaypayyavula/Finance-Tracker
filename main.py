from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "2356d4f2"


mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vijay@2001'
app.config['MYSQL_DB'] = 'expensetracker'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


@app.route("/", methods=["POST", "GET"])
def login_page():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        usr = request.form["username"]
        session["user"] = usr
        pw = request.form["password"]
        sql = " SELECT * FROM users WHERE USERNAME = %s AND PASSWORD = %s "
        cur.execute(sql, (usr, pw))
        sqld = cur.fetchall()
        if len(sqld) != 0:
            return redirect(url_for('home_page'))
        return render_template("login.html")

    if "user" in session:
        return redirect(url_for('home_page'))
    return render_template("login.html")


@app.route("/home", methods=["POST", "GET"])
def home_page():
    if "user" in session:
        cur = mysql.connection.cursor()
        user = session["user"]
        cur.execute(" SELECT SUM(amount) AS balance FROM transactions WHERE username = %s ", [user])
        sql = cur.fetchall()
        balance = sql[0]['balance']
        if balance is None:
            balance = 0
        cur.execute(" SELECT SUM(amount) AS income FROM transactions WHERE username = %s AND amount>=0 ", [user])
        sql = cur.fetchall()
        income = sql[0]['income']
        if income is None:
            income = 0
        cur.execute(" SELECT SUM(amount) AS expense FROM transactions WHERE username = %s AND amount<0", [user])
        sql = cur.fetchall()
        expense = str(sql[0]['expense'])
        if expense == 'None':
            expense = '00'
        cur.execute(" SELECT description, amount FROM transactions WHERE username = %s ", [user])
        transact = cur.fetchall()
        print(expense)
        print(transact)
        return render_template("main.html", balance=balance, income=income, expense=expense[1:], transactions=transact)
    return redirect(url_for('login_page'))


@app.route("/user")
def test():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for('login_page'))


@app.route("/register", methods=["POST", "GET"])
def register_page():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        usrnm = request.form["username"]
        passw = request.form["password"]
        cur.execute(" INSERT INTO users VALUES(%s, %s, %s, %s) ", (name, email, usrnm, passw))
        mysql.connection.commit()
        return redirect(url_for('login_page'))
    return render_template("register.html")


@app.route("/add", methods=["POST", "GET"])
def add_transaction():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        des = request.form["description"]
        amt = request.form["amount"]
        user = session["user"]
        if (des == "") or (amt == ""):
            return redirect(url_for('add_transaction'))
        cur.execute(" INSERT INTO transactions VALUES(null, %s, %s, %s) ", (user, des, amt))
        mysql.connection.commit()
        return redirect(url_for('home_page'))
    if "user" in session:
        return render_template('add.html')
    return redirect(url_for('login_page'))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('login_page'))


if __name__ == "__main__":
    app.run(debug=True)
