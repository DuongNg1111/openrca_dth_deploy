from src.agents.base_agent import BaseAgent



class MetricAgent(BaseAgent):


    def __init__(self):

        super().__init__(
            "Metric Agent"
        )



    def analyze(self, context):


        metrics = context.metrics


        result = {

            "agent": self.name,

            "service": context.service,

            "evidence": [],

            "summary": None

        }


        # TODO:
        # detect anomaly


        result["summary"] = (
            "Metric analysis pending"
        )


        return result