from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

def soma(a, b):
    return a + b

class Soma(Resource):
    def post(self):
        data = request.get_json()
        resultado = soma(data['a'], data['b'])
        return {'resultado': resultado}

api.add_resource(Soma, '/soma')

if __name__ == '__main__':
    app.run(debug=True)
