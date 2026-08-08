import json

from src.process_module.agents.base_agent import BaseAgent
from src.llm.gemini_client import GeminiClient

class ReasoningAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            "Reasoning Agent"
        )

        self.llm = GeminiClient()


    def calculate_confidence(
        self,
        metric_result,
        log_result,
        trace_result
    ):

        score = 0
        total = 3


        if metric_result.get(
            "anomalies"
        ):
            score += 1


        if log_result.get(
            "errors"
        ):
            score += 1


        if trace_result.get(
            "traces"
        ):
            score += 1


        return round(
            score / total,
            2
        )


    def check_evidence(
        self,
        metric_result,
        log_result,
        trace_result
    ):

        missing = []


        if not metric_result.get(
            "anomalies"
        ):
            missing.append(
                "metrics"
            )


        if not log_result.get(
            "errors"
        ):
            missing.append(
                "logs"
            )


        if not trace_result.get(
            "traces"
        ):
            missing.append(
                "traces"
            )


        return missing



    def analyze(
        self,
        context,
        metric_result,
        log_result,
        trace_result
    ):


        missing = self.check_evidence(
            metric_result,
            log_result,
            trace_result
        )


        confidence = self.calculate_confidence(
            metric_result,
            log_result,
            trace_result
        )


        if len(missing) == 3:

            return {

                "component": context.service,

                "reason":
                "Insufficient evidence",

                "confidence":0,

                "reasoning":
                "No telemetry evidence available"

            }



        prompt = f"""

You are an expert SRE.

Analyze this incident.

SERVICE:
{context.service}


METRICS:
{json.dumps(metric_result)}


LOGS:
{json.dumps(log_result)}


TRACES:
{json.dumps(trace_result)}


Return ONLY JSON:

{{
"reason":"",
"reasoning":"",
"recommendation":""
}}

"""


        try:

            response = self.llm.generate(
                prompt
            )


            result = json.loads(
                response
            )


            result.update({

                "component":
                context.service,


                "confidence":
                confidence,


                "occurrence_time":
                context.incident_time,


                "metrics":
                metric_result,


                "logs":
                log_result,


                "traces":
                trace_result

            })


            return result



        except Exception as e:


            return {

    "component": metric_result.get(
        "service",
        "unknown"
    ),

    "reason": "LLM Error",

    "confidence": 0,

    "reasoning": str(e),

    "metrics": metric_result,

    "logs": log_result,

    "traces": trace_result

}