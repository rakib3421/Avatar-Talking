from flask import Flask, render_template

app = Flask(__name__)

app.run(debug=True,render_template('index.html'))