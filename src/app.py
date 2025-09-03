
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from celery import Celery, Task
from celery.result import AsyncResult

def create_celery_app(app: Flask) -> Celery:
    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.import_name)
    celery_app.Task = ContextTask
    celery_app.config_from_object(app.config["CELERY"])
    app.extensions["celery"] = celery_app
    return celery_app

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.getenv('SECRET_KEY', 'demo-secret-key'),
    CELERY={
        'broker_url': os.getenv('BROKER', 'redis://localhost:6379/0'),
        'result_backend': os.getenv('BACKEND', 'redis://localhost:6379/0'),
        'task_ignore_result': False,
        'task_track_started': True,
        'result_expires': 3600,
    }
)

celery = create_celery_app(app)
recent_tasks = []

@app.route("/")
def hello_world():
    message = "Welcome to the Flask + Celery + Redis + Flower Demo! 🎉"
    
    task_results = []
    for task_info in recent_tasks[-10:]:
        result = AsyncResult(task_info['id'], app=celery)
        task_results.append({
            'id': task_info['id'][:8] + '...',
            'name': task_info['name'],
            'status': result.status,
            'result': result.result if result.successful() else None
        })
    
    return render_template('home.html', message=message, tasks=task_results)

@app.route("/submit_division", methods=['POST'])
def submit_division():
    try:
        dividend = float(request.form['dividend'])
        divisor = float(request.form['divisor'])
        
        if divisor == 0:
            flash('Division by zero is not allowed!', 'error')
            return redirect(url_for('hello_world'))
        
        task = divide.delay(dividend, divisor)
        recent_tasks.append({
            'id': task.id,
            'name': f'Division: {dividend} ÷ {divisor}'
        })
        
        flash(f'Division task submitted! Task ID: {task.id[:8]}...', 'success')
    except (ValueError, KeyError):
        flash('Invalid input for division task', 'error')
    
    return redirect(url_for('hello_world'))

@app.route("/submit_text_task", methods=['POST'])
def submit_text_task():
    try:
        text = request.form['text'].strip()
        repeat = int(request.form['repeat'])
        
        if not text:
            flash('Text cannot be empty!', 'error')
            return redirect(url_for('hello_world'))
        
        if repeat <= 0 or repeat > 10:
            flash('Repeat count must be between 1 and 10!', 'error')
            return redirect(url_for('hello_world'))
        
        task = process_text.delay(text, repeat)
        recent_tasks.append({
            'id': task.id,
            'name': f'Text Processing: "{text}" x{repeat}'
        })
        
        flash(f'Text processing task submitted! Task ID: {task.id[:8]}...', 'success')
    except (ValueError, KeyError):
        flash('Invalid input for text processing task', 'error')
    
    return redirect(url_for('hello_world'))

from tasks import register_tasks
divide, process_text = register_tasks(celery)