from waitress import serve
import auth.login_api as login_api

if __name__ == '__main__':
    print('[waitress] Starting on 0.0.0.0:5000')
    serve(login_api.app, host='0.0.0.0', port=5000)
