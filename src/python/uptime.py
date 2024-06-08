import time

class Uptime:
    def __init__(self):
        self.start_time = time.time()

    def get_uptime(self):
        current_time = time.time()
        uptime_seconds = current_time - self.start_time
        return self.format_uptime(uptime_seconds)
    
    def format_uptime(self, seconds):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        uptime_str = ''

        if days != 0:
            uptime_str += f"{days}d "
        elif hours != 0:
            uptime_str += f"{hours}h "
        elif minutes != 0:       
            uptime_str += f"{minutes}m "
        uptime_str += f"{seconds}s"
        
        return uptime_str