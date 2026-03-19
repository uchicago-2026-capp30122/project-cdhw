from project_cdhw.dash_app.app_creation import create_app

# 1. Initialize the app at the top level
app = create_app()

# 2. Expose the Flask server for Gunicorn
server = app.server

# 3. Local development block
if __name__ == "__main__":
    # This only runs when you type 'python app.py' locally
    app.run(debug=True, port=8080)
