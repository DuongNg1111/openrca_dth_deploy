from src.process_module.agents.base_agent import BaseAgent


class TraceAgent(BaseAgent):


    def __init__(self):

        super().__init__(
            "Trace Agent"
        )


    def analyze(self, context):


        traces = context.traces


        result = {

            "agent": self.name,

            "service": context.service,

            "trace_tables": list(traces.keys()),

            "evidence": [],

            "summary": None

        }


        # TODO:
        # Analyze trace spans


        result["summary"] = (
            "Trace analysis pending"
        )


        return result