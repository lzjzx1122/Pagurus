from flask import Flask, request, jsonify, Response
import time


node = Flask(__name__)


@node.route('/listen', methods=['POST'])
def listen():
	time.sleep(2)
	return Response(status=200)


@node.route('/load-info', methods=['GET'])
def load_info():
	load = {
		'0.0.0.0:5002':{
			'cpu': 34.45,
			'mem': 57.65,
			'net': 27.11
		}
	}
	time.sleep(2)
	return jsonify(load)


@node.route('/lender-info', methods=['GET'])
def lender_info():
	data = {
		'0.0.0.0:5002':[
			{
				'name': 'hello',
				'packages':{
					'p1': 1.0,
					'p2': 1.0,
				}
			}
		]
	}
	time.sleep(2)
	return jsonify(data)

if __name__ == '__main__':
	node.run(debug=True, host='0.0.0.0')
