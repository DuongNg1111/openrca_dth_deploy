from src.process_module.agents.base_agent import BaseAgent


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

            "metric_tables": list(metrics.keys()),

            "evidence": [],

            "summary": None

        }


        # TODO:
        # Detect metric anomalies


        result["summary"] = (
            "Metric analysis pending"
        )


        return result