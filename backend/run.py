from app import create_app

app = create_app()

if __name__ == '__main__':
    # Para produção, use um servidor WSGI como Gunicorn:
    # gunicorn --bind 0.0.0.0:8000 "run:app"
    app.run(host='0.0.0.0', port=5500, debug=True)