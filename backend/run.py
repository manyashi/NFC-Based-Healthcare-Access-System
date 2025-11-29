from app import create_app

app = create_app()

if __name__ == '__main__':
    # SSL context='adhoc' allows HTTPS locally for development
    app.run(debug=True, ssl_context='adhoc', port=5000)