
class Agent:
    def __init__(self, startegy):
        if(startegy == 'accu_match'):
            from task_executor.accu_match.accumatch_agent import AccuMatchAgent
        elif(startegy == 'LLM'):
            from task_executor.LLM.LLM_agent import LLMAgent

    def set_task(self, app, task):
        self.agent.set_task(app, task)