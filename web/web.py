from flask import Flask, Response, request
from flask_limiter import Limiter
from flask_caching import Cache
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time
import functools

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["1 per 1 seconds"])
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
requests_total = Counter('requests_total', 'Total number of requests', ['endpoint'])
blocked_requests = Counter('blocked_requests_total', 'Total number of blocked requests', ['ip'])
method_duration = Histogram('method_duration_seconds', 'Time spent processing a method', ['endpoint'])

def timed_endpoint(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        method_duration.labels(endpoint=func.__name__).observe(duration)
        return result
    return wrapper


@app.before_request
def log_request():
    ip = request.remote_addr
    requests_total.labels(endpoint=request.path, ip=ip).inc()

@app.route('/')
@limiter.limit("1 per 2 seconds")
@cache.cached(timeout=15)
@timed_endpoint
def home():
    requests_total.labels(endpoint='home').inc()
    i = 0
    while i <= 1000000:
        i+=1
    return f'Welcome! {i}<br><p><br> <iframe src="http://localhost:3000/d-solo/0b63ced7-d62c-4f27-8047-28bb97d2b8c3/new-dashboard?orgId=1&timezone=browser&panelId=1&__feature.dashboardSceneSolo" width="850" height="400" frameborder="0"></iframe></p>'

@app.route('/about')
@timed_endpoint
@limiter.limit("1 per 2 seconds")
@cache.cached(timeout=60)
def about():
    requests_total.labels(endpoint='about').inc()
    time.sleep(0.5)
    return "About us"

@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

@app.errorhandler(429)
def ratelimit_handler(e):
    ip = request.remote_addr
    blocked_requests.labels(ip=ip).inc() 
    return "Too Many Requests.", 429

if __name__ == '__main__':
    app.run(debug=True)