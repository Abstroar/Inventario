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
    if request.method == "POST":
        email = request.form.get('Email')
        password = request.form.get('Password')
        user = User.query.filter_by(email=email).first()
        if not user:
            print("User not found")
            return redirect(url_for("login"))
        if user.password != password:
            print("wrong password")
            return redirect(url_for("login"))
        return redirect(url_for("home"))
    return render_template("login.html")






@app.route("/register",methods=['POST','GET'])
def register():
    if request.method=="POST":
        company_name = request.form.get('Company')
        company = Company.query.filter_by(name=company_name).first()

        if not company:
            print("company does not exist ")
            return redirect(url_for("register"))
        email = request.form.get('Email')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("User already exists.")
            return redirect(url_for("login"))
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


@app.route("/edit-item/<int:item_id>", methods=['GET', 'POST'])
def edit_item(item_id):
    item = Items.query.get(item_id)
    if not item:
        print("Item not found!")
        return redirect(url_for("home"))

    if request.method == 'POST':
        item.title = request.form.get('title')
        item.subtitle = request.form.get('subtitle')
        item.price = request.form.get('price')
        item.quantity = request.form.get('quantity')

        db.session.commit()
        print("Item updated successfully!")
        return redirect(url_for("home"))

    return render_template("edit_x_item.html", item=item)


@app.route("/delete-item/<int:item_id>", methods=['GET'])
def delete_item(item_id):
    item = Items.query.get(item_id)
    if not item:
        print("Item not found!")
        return redirect(url_for("home"))

    db.session.delete(item)
    db.session.commit()
    print("Item deleted successfully!")
    return redirect(url_for("home"))


@app.route("/home",methods=['POST','GET'])
def home():
    result = db.session.execute(db.select(Items))
    posts = result.scalars().all()

    return render_template("home.html", items_list=posts)

@app.route("/add-company",methods=['POST','GET'])
def company_adder():
    if request.method == "POST":

        company_name = request.form.get('Company')

        existing_company = Company.query.filter_by(name=company_name).first()
        if existing_company:
            print("Company already exists. Please choose a different name.")
            return redirect(url_for("company_adder"))

        new_company = Company(name=company_name)


        db.session.add(new_company)
        db.session.commit()

        print(f"Company '{company_name}' added successfully!")
        return redirect(url_for("register"))

    return render_template("company_adder.html")

@app.route("/add-items",methods=['POST','GET'])
def item_adder():
    if request.method == "POST":
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        existing_item = Items.query.filter_by(title=title).first()
        if existing_item:
            print("An item with this title already exists")
            return redirect(url_for("item_adder"))

        company = Company.query.filter_by(
            name="abhi").first()
        data = Items(
            title=title,
            subtitle=subtitle,
            price=price,
            quantity=quantity,
            company=company,
        )
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit_item.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)