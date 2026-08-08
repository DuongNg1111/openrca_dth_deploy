import json

from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.trace_agent import TraceAgent


class TestContext:

    def __init__(
        self,
        investigation_id,
        service,
        incident_time
    ):
        self.investigation_id = investigation_id
        self.service = service
        self.incident_time = incident_time



if __name__ == "__main__":


    context = TestContext(
        investigation_id=68,
        service="frontend-0",
        incident_time="2022-03-20 10:13:12"
    )


    print("\n================================")
    print("TEST CONTEXT")
    print("================================")

    print(
        context.__dict__
    )


    # ==========================
    # METRIC
    # ==========================

    print("\n\n[1/3] Testing Metric Agent...")


    metric_agent = MetricAgent()


    metric_result = metric_agent.analyze(
        context
    )


    print("\nMETRIC RESULT")
    print(
        json.dumps(
            metric_result,
            indent=2,
            default=str
        )
    )



    # ==========================
    # LOG
    # ==========================

    print("\n\n[2/3] Testing Log Agent...")


    log_agent = LogAgent()


    log_result = log_agent.analyze(
        context
    )


    print("\nLOG RESULT")

    print(
        json.dumps(
            log_result,
            indent=2,
            default=str
        )
    )



    # ==========================
    # TRACE
    # ==========================


    print("\n\n[3/3] Testing Trace Agent...")


    trace_agent = TraceAgent()


    trace_result = trace_agent.analyze(
        context
    )


    print("\nTRACE RESULT")


    print(
        json.dumps(
            trace_result,
            indent=2,
            default=str
        )
    )



    print("\n================================")
    print("AGENT TEST COMPLETED")
    print("================================")