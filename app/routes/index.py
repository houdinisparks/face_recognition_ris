from flask import Blueprint


webpage_bp = Blueprint('webpage', __name__,static_folder="../static")


@webpage_bp.route('/')
def root():
    print("sending index.html")
    return webpage_bp.send_static_file('Spages/mainPage/views/index.html')