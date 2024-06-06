from llm_utils.database import write_to_db
from abc import abstractmethod

class WorkflowHandler():
    def __init__(self):
        self.total_cost = 0.0
    
    @abstractmethod
    def process(self):
        raise NotImplementedError
    
    def _update_total_cost(self, response_meta):
        self.total_cost += response_meta.total_cost
    
    def log_to_database(self, app_config, content_to_log, start, finish, background_tasks, label=""):
        try: 
            background_tasks.add_task(
                write_to_db,
                app_config,
                content_to_log,
                start,
                finish,
                self.total_cost,
                label
            )
        except KeyError:
            # TODO add warning or log?
            pass