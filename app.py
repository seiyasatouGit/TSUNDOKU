# SQ lite3をインポートする
from contextlib import redirect_stderr
from pydoc import pager
import sqlite3
from tkinter import E
from turtle import title
from flask import Flask, render_template, request, redirect, session
app = Flask(__name__)

# セッションを保護するためのシークレットキー
app.secret_key = "sunabaco"

# ========ログインページ==========
@app.route("/", methods=["GET"])
def login_get():
    if "user_id" in session:
        return redirect("/book")
    else:
        return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    name = request.form.get("name")
    password = request.form.get("password")

    conn = sqlite3.connect("test_db.db")
    c = conn.cursor()
    c.execute("select id from user where name = ? and password = ?",(name, password))
    conn.commit()
    user_id = c.fetchone()
    c.close()

    if user_id is None:
        return render_template("login.html")
    else:
        # ログインが成功した時にセッションを発行する
        session["user_id"] = user_id
        return redirect("/book")  

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/book")



# ========新規ユーザー登録==========

# セッション続いてる場合の記述
@app.route("/regist", methods=["GET"])
def regist_get():
    if "user_id" in session:
    #regist.htmlを返す
        return redirect("/book")
    else:
        return render_template("regist.html") 

# 新規ユーザー登録（nameとpaaaword）の記述
@app.route("/regist", methods=["POST"])
def regist_post():
    name = request.form.get("name")
    password = request.form.get("password")
# DBに接続
    conn = sqlite3.connect("test_db.db")
    # DBを操作できるようにする
    c = conn.cursor()
    #SQL文を実行
    c.execute("insert into user values(null, ?, ?)",(name, password))
    #DBを上書き保存
    conn.commit()
    c.execute("select id from user where name = ? and password = ?",(name, password))
    user_id = c.fetchone()  
    # DBの接続を終了する
    c.close()
    session["user_id"] = user_id
    return redirect("/add")





# ==============入力する====================

# 本の入力ページを取得するためのルーティング
@app.route("/add", methods=["GET"])
def add_get():
    if "user_id" in session:
        return render_template("add.html")
    else:
        return redirect("/") 

# 入力した本の情報をDBに追加するためのルーティング

@app.route("/add", methods=["POST"])
def add_post():
    if "user_id" in session:
        user_id = session["user_id"][0] 
        # 入力フォームから値を取得する
        title = request.form.get("title")
        print(title)
        page = request.form.get("page")
        print(page)
        time = request.form.get("time")
        print(time)
        page = int(page)
        time = int(time)
        day = page // time
        print("**************")
        print(day)
       
        # データベースに接続する
        conn = sqlite3.connect("test_db.db")
        # データベースを操作できるようにする
        c = conn.cursor()
        # SQLを実行してCREATEする
        c.execute("insert into book values (null, ?, ?, ?, ?, ?)", (user_id, title, page, time, day))
      
        # データベースの変更を保存する
        conn.commit()
        # データベースの接続を終了する
        c.close() 
        return redirect("/book")
    else:
        return redirect("/login")  



# ======== MYページ ==========

@app.route("/book")
def book_list():
    if "user_id" in session:
        # セッションからIDを取ってくる
        user_id = session["user_id"][0]
        conn = sqlite3.connect("test_db.db")
        c = conn.cursor()
        # ログインユーザーの名前を取得
        c.execute("select name from user where id = ?", (user_id,))
        user_name = c.fetchone()[0]
        # タスク一覧をREADする
        c.execute("select id, title, page, time, day from book where user_id = ?", (user_id,))
        # 括弧の中にどんどん格納していく
        book_list = []
        # for 変数 in 配列
        #Fetchallで録ってきた内容をタプル型リストに格納する
        for row in c.fetchall():
            print("----------------------")
            print(row)
            print("----------------------")
            book_list.append({"id": row[0], "title": row[1], "page": row[2], "time": row[3], "day": row[4]})    
        c.close()
        return render_template("book.html", book_list=book_list, user_name = user_name)
    else:
        return redirect("/")



# ========  result 計算結果のみ返す ==========

@app.route("/add2")
def add2(): 
    return render_template("add2.html")

@app.route("/calc", methods=["POST"])
def calc():
    title = request.form.get("title") 
    page = request.form.get("page") 
    time = request.form.get("time")
    page = int(page) 
    time = int(time)
    day = page // time
    return render_template("result.html", title = title, page = page, time = time, day = day)



#======= 登録内容を編集 =================


@app.route("/edit/<int:id>")
def edit(id):
    if "user_id" in session:
        conn = sqlite3.connect("test_db.db")
        c = conn.cursor()
        c.execute("select id, title, page, time from book where id = ?" , (id,))
        book_info = c.fetchone()
        c.close() 
        if book_info is not None:   
            print(book_info)
        else :
            return "まだ本が登録されていません"

        item = {"id": id, "title": book_info[1], "page": book_info[2], "time": book_info[3]}
        return render_template("edit.html" , book_info = item)
        
    else:
        return redirect("/login")  


@app.route("/edit", methods=["POST"])
def update_book():
    if "user_id" in session:
        #編集対象のIDを取得
        book_id = request.form.get("id")
        book_id = int(book_id)
        #編集された内容
        title = request.form.get("title")
        page = request.form.get("page")
        time = request.form.get("time")
        # データベースに接続する
        conn = sqlite3.connect("test_db.db")
        # データベースを操作できるようにする
        c = conn.cursor()
        c.execute("update book set title = ?, page = ?, time = ? where id = ?",(title, page, time, book_id))
        conn.commit()
        # データベースの接続を終了する
        c.close()  
        return redirect("/book")
    else:
        return redirect("/login")   













#======= 登録内容を削除 =================

@app.route("/del/<int:id>")
def del_task(id):
    if "user_id" in session:
        # DBに接続
        conn = sqlite3.connect("test_db.db")
        # DBを操作できるようにする
        c = conn.cursor()
        #SQL文を実行
        c.execute("delete from book where id = ?",(id,))
        #DBを上書き保存
        conn.commit()
        # DBの接続を終了する
        c.close()  
        return redirect("/book")
    else:
        return redirect("/login")  

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

## おまじない
if __name__ == "__main__":
    app.run(debug=False)