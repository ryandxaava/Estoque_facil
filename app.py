from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from functools import wraps
app=Flask(__name__); app.secret_key=os.environ.get("SECRET_KEY","troque-esta-chave")
DB=os.path.join(os.path.dirname(__file__),"estoque.db")
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 with db() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,name TEXT NOT NULL,sku TEXT UNIQUE,quantity INTEGER NOT NULL DEFAULT 0,min_quantity INTEGER NOT NULL DEFAULT 0);
  CREATE TABLE IF NOT EXISTS movements(id INTEGER PRIMARY KEY,product_id INTEGER,user_id INTEGER,kind TEXT,quantity INTEGER,note TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(product_id) REFERENCES products(id),FOREIGN KEY(user_id) REFERENCES users(id));""")
  if not c.execute("SELECT id FROM users LIMIT 1").fetchone(): c.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",("admin",generate_password_hash("admin123")))
def required(f):
 @wraps(f)
 def w(*a,**k):
  if "user_id" not in session:return redirect(url_for("login"))
  return f(*a,**k)
 return w
@app.route("/login",methods=["GET","POST"])
def login():
 if request.method=="POST":
  with db() as c:u=c.execute("SELECT * FROM users WHERE username=?",(request.form.get("username",""),)).fetchone()
  if u and check_password_hash(u["password_hash"],request.form.get("password","")):
   session.clear();session["user_id"]=u["id"];session["username"]=u["username"];return redirect(url_for("index"))
  flash("Usuário ou senha incorretos.")
 return render_template("login.html")
@app.route("/logout")
def logout():session.clear();return redirect(url_for("login"))
@app.route("/")
@required
def index():
 with db() as c:
  ps=c.execute("SELECT * FROM products ORDER BY name").fetchall()
  total=c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
  low=c.execute("SELECT COUNT(*) FROM products WHERE quantity<=min_quantity").fetchone()[0]
  ms=c.execute("SELECT m.*,p.name product_name FROM movements m JOIN products p ON p.id=m.product_id ORDER BY m.id DESC LIMIT 8").fetchall()
 return render_template("index.html",products=ps,total=total,low=low,movements=ms)
@app.route("/products",methods=["GET","POST"])
@required
def products():
 if request.method=="POST":
  try:
   name=request.form["name"].strip();sku=request.form.get("sku","").strip() or None;q=int(request.form["quantity"]);mn=int(request.form["min_quantity"])
   if not name or q<0 or mn<0:raise ValueError()
   with db() as c:c.execute("INSERT INTO products(name,sku,quantity,min_quantity) VALUES(?,?,?,?)",(name,sku,q,mn))
   flash("Produto cadastrado.")
  except (ValueError,sqlite3.IntegrityError):flash("Dados inválidos ou SKU já cadastrado.")
  return redirect(url_for("products"))
 with db() as c:ps=c.execute("SELECT * FROM products ORDER BY name").fetchall()
 return render_template("products.html",products=ps)
@app.route("/movement",methods=["GET","POST"])
@required
def movement():
 with db() as c:ps=c.execute("SELECT * FROM products ORDER BY name").fetchall()
 if request.method=="POST":
  try:
   pid=int(request.form["product_id"]);q=int(request.form["quantity"]);kind=request.form["kind"];note=request.form.get("note","")
   if q<=0 or kind not in ("entrada","saida"):raise ValueError()
   with db() as c:
    p=c.execute("SELECT quantity FROM products WHERE id=?",(pid,)).fetchone()
    if not p:raise ValueError()
    nq=p["quantity"]+q if kind=="entrada" else p["quantity"]-q
    if nq<0:flash("Estoque insuficiente.");return redirect(url_for("movement"))
    c.execute("UPDATE products SET quantity=? WHERE id=?",(nq,pid))
    c.execute("INSERT INTO movements(product_id,user_id,kind,quantity,note) VALUES(?,?,?,?,?)",(pid,session["user_id"],kind,q,note))
   flash("Movimentação registrada.")
  except (ValueError,KeyError):flash("Dados inválidos.")
  return redirect(url_for("movement"))
 return render_template("movement.html",products=ps)
@app.route("/history")
@required
def history():
 with db() as c:ms=c.execute("SELECT m.*,p.name product_name,u.username FROM movements m JOIN products p ON p.id=m.product_id JOIN users u ON u.id=m.user_id ORDER BY m.id DESC").fetchall()
 return render_template("history.html",movements=ms)
if __name__=="__main__":init_db();app.run(debug=True)
