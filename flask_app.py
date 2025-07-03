from app import create_app

app = create_app('config.ProductionConfig')

if __name__ == "__main__":
    app.run(debug=False)  # Disable debug mode for production