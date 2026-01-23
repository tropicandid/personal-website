from app import init_app

flask_app = init_app()
if __name__ == "__main__":
    flask_app.run(debug=False)

