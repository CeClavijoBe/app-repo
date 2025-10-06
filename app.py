from flask import Flask
from prometheus_client import Counter, Gauge, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time

app = Flask(__name__)

# Métricas de Prometheus
request_counter = Counter('my_requests_total', 'Total number of requests received', ['endpoint', 'method'])
request_duration = Histogram('request_duration_seconds', 'Request duration in seconds', ['endpoint'])
active_requests = Gauge('active_requests', 'Number of active requests')

@app.route('/')
def hello():
    start_time = time.time()
    active_requests.inc()
    
    request_counter.labels(endpoint='/', method='GET').inc()
    
    response = "Hello, World! This is my Flask app with Prometheus metrics!"
    
    duration = time.time() - start_time
    request_duration.labels(endpoint='/').observe(duration)
    active_requests.dec()
    
    return response

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

@app.route('/ready')
def ready():
    return {"status": "ready"}, 200

# Montar el endpoint de métricas de Prometheus
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)