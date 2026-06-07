from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Bonjour tout le monde"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        return redirect(url_for("home", username=name))
    return render_template("formulaire.html")


@app.route("/home/<username>")
def home(username):
    return render_template("name.html", username=username)


if __name__ == "__main__":
    print("running flask")
    app.run(debug=True)
