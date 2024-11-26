import os

from flask import Flask, abort, render_template, redirect, url_for, flash, request
# from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from forms import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('flask_key')


#database
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Items(db.Model):
    __tablename__ = "Items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("company.id"))
    company = relationship("Company", back_populates="items")


class Company(db.Model):
    __tablename__ = "company"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)

    items = relationship("Items", back_populates="company")
    users = relationship("User", back_populates="company")


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("company.id"))
    company = relationship("Company", back_populates="users")

with app.app_context():
    db.create_all()


@app.route("/",methods=['POST','GET'])
def login():
    if request.method=="POST":
        print("hii")
        print(f"request {request.form.get('Email')}")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/register",methods=['POST','GET'])
def register():
    if request.method=="POST":
        company_name = request.form.get('Company')
        company = Company.query.filter_by(name=company_name).first()

        # If the company does not exist, handle the error or create it
        if not company:
            flash("Company not found. Please select a valid company.", "error")
            return redirect(url_for("register"))

        data = User(
            username=request.form.get('Username'),
            email=request.form.get('Email'),
            password=request.form.get('Password'),
            company=company,
        )
        db.session.add(data)
        db.session.commit()
        print(data)
        print("hii")
        print(f"request {request.form.get('Email')}")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/home",methods=['POST','GET'])
def home():
    result = db.session.execute(db.select(Items))
    posts = result.scalars().all()

    return render_template("home.html", items_list=posts)

@app.route("/add-company",methods=['POST','GET'])
def company_adder():
    # com = Company(
    #     name="abhi"
    # )
    # db.session.add(com)
    # db.session.commit()
    return render_template("company_adder.html")

@app.route("/add-items",methods=['POST','GET'])
def item_adder():
    if request.method == "POST":
        company = Company.query.filter_by(name="abhi").first()
        data = Items(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            price=request.form.get('price'),
            quantity=request.form.get('quantity'),
            company=company,
        )
        db.session.add(data)
        db.session.commit()
        print("daasas")
        return redirect(url_for("home"))
    return render_template("edit_item.html")

# @app.route("/edit-item",methods=['POST','GET'])
# def item_editer():
#     return render_template("edit_item.html")
""""
company = Company.query.filter_by(name="abhi").first()
    data = Items(
        title="bed",
        subtitle="furniture",
        price=100,
        quantity=2,
        company=company,
    )
    db.session.add(data)
    db.session.commit()
"""
if __name__ == "__main__":
    app.run(debug=True, port=5002)