import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class Storage:
    def __init__(self, file_path):
        self.file_path = file_path
        self.events = []
    
    def log_event(self, event):
        self.events.append({'timestamp': datetime.now().isoformat(), 'event': event})
        try:
            with open(self.file_path, 'a') as f:
                f.write(str(self.events[-1]) + '\n')
        except Exception as e:
            _LOGGER.error('Error writing log: %s', e)
