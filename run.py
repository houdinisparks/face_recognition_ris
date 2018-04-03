from app.load import create_app

app = create_app()

# We only need this for local development.
if __name__ == '__main__':
    print("initiating the web app...")
    app.run(debug=True)