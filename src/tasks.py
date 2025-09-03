import time
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def register_tasks(celery):
    @celery.task(bind=True)
    def divide(self, x, y):
        try:
            logger.info(f'Starting division task: {x} ÷ {y}')
            self.update_state(state='PROGRESS', meta={'current': 0, 'total': 5, 'status': 'Starting...'})
            
            for i in range(5):
                time.sleep(1)
                self.update_state(state='PROGRESS', meta={'current': i+1, 'total': 5, 'status': f'Processing... {i+1}/5'})
            
            if y == 0:
                raise ValueError("Division by zero")
                
            result = x / y
            logger.info(f'Division complete: {result}')
            return result
        except Exception as exc:
            logger.error(f'Division task failed: {exc}')
            self.update_state(state='FAILURE', meta={'error': str(exc)})
            raise

    @celery.task(bind=True)
    def process_text(self, text, repeat_count):
        try:
            logger.info(f'Starting text processing: "{text}" x{repeat_count}')
            self.update_state(state='PROGRESS', meta={'current': 0, 'total': repeat_count + 10, 'status': 'Initializing...'})
            
            time.sleep(2)
            self.update_state(state='PROGRESS', meta={'current': 2, 'total': repeat_count + 10, 'status': 'Processing text...'})
            
            processed = []
            for i in range(repeat_count):
                time.sleep(1)
                processed.append(f"{i+1}. {text.upper()}")
                self.update_state(
                    state='PROGRESS', 
                    meta={'current': i+3, 'total': repeat_count + 10, 'status': f'Processing item {i+1}/{repeat_count}'}
                )
            
            time.sleep(5)
            result = " | ".join(processed)
            logger.info(f'Text processing complete: {len(result)} characters')
            return result
        except Exception as exc:
            logger.error(f'Text processing task failed: {exc}')
            self.update_state(state='FAILURE', meta={'error': str(exc)})
            raise

    return divide, process_text