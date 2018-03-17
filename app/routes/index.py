from app import app
from flask import Flask, render_template, request, url_for, send_from_directory

@app.route('/')
def root():
    return app.send_static_file('pages/mainPage/views/index.html')