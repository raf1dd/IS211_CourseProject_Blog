"""
Script: app.py
IS 211 Course Project - Option 2: Blogging Application.
"""

from datetime import datetime
from functools import wraps
import sqlite3
from flask import Flask, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "is211-blog-project-secret-key"
DATABASE = "blog.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


@app.route("/")
def index():
    db = get_db()
    posts = db.execute(
        """
        SELECT id, title, author, category, content, published_at
        FROM posts
        WHERE is_published = 1
        ORDER BY published_at DESC, id DESC
        """
    ).fetchall()
    return render_template("index.html", posts=posts, active_category=None)


@app.route("/post/<int:post_id>")
def view_post(post_id):
    db = get_db()
    post = db.execute(
        """
        SELECT id, title, author, category, content, published_at, is_published
        FROM posts
        WHERE id = ?
        """,
        (post_id,),
    ).fetchone()
    if post is None or (not post["is_published"] and not session.get("logged_in")):
        return redirect(url_for("index"))
    return render_template("post.html", post=post)


@app.route("/category/<category_name>")
def view_category(category_name):
    db = get_db()
    posts = db.execute(
        """
        SELECT id, title, author, category, content, published_at
        FROM posts
        WHERE is_published = 1 AND category = ?
        ORDER BY published_at DESC, id DESC
        """,
        (category_name,),
    ).fetchall()
    return render_template("index.html", posts=posts, active_category=category_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT id, username, password FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        if user is not None:
            session.clear()
            session["logged_in"] = True
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    posts = db.execute(
        """
        SELECT id, title, author, category, published_at, is_published
        FROM posts
        ORDER BY published_at DESC, id DESC
        """
    ).fetchall()
    return render_template("dashboard.html", posts=posts)


@app.route("/post/add", methods=["GET", "POST"])
@login_required
def add_post():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip() or "General"
        content = request.form.get("content", "").strip()
        is_published = 1 if request.form.get("is_published") == "1" else 0
        author = session.get("username", "admin")
        published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not title or not content:
            error = "Title and content are required."
            return render_template(
                "post_form.html",
                mode="Add",
                error=error,
                post={"title": title, "category": category, "content": content, "is_published": is_published},
            )

        db = get_db()
        db.execute(
            """
            INSERT INTO posts (title, author, category, content, published_at, is_published)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, author, category, content, published_at, is_published),
        )
        db.commit()
        return redirect(url_for("dashboard"))

    return render_template(
        "post_form.html",
        mode="Add",
        error=error,
        post={"title": "", "category": "General", "content": "", "is_published": 1},
    )


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip() or "General"
        content = request.form.get("content", "").strip()
        is_published = 1 if request.form.get("is_published") == "1" else 0

        if not title or not content:
            error = "Title and content are required."
            return render_template(
                "post_form.html",
                mode="Edit",
                error=error,
                post={"id": post_id, "title": title, "category": category, "content": content, "is_published": is_published},
            )

        db.execute(
            """
            UPDATE posts
            SET title = ?, category = ?, content = ?, is_published = ?
            WHERE id = ?
            """,
            (title, category, content, is_published, post_id),
        )
        db.commit()
        return redirect(url_for("dashboard"))

    return render_template("post_form.html", mode="Edit", error=error, post=post)


@app.route("/post/<int:post_id>/toggle", methods=["POST"])
@login_required
def toggle_publish(post_id):
    db = get_db()
    post = db.execute("SELECT is_published FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is not None:
        new_status = 0 if post["is_published"] else 1
        db.execute("UPDATE posts SET is_published = ? WHERE id = ?", (new_status, post_id))
        db.commit()
    return redirect(url_for("dashboard"))


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    db = get_db()
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
