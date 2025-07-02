from app import create_app

app = create_app('config.production.Config')


if __name__ == "__main__":
    app.run(debug=True)

    #might be able to remove
    