from src.process_module.agents.log_agent import LogAgent
from src.process_module.agents.metric_agent import MetricAgent
from src.process_module.agents.trace_agent import TraceAgent
from src.process_module.agents.reasoning_agent import ReasoningAgent



def test_agents(context):


    log_result = LogAgent().analyze(
        context
    )


    metric_result = MetricAgent().analyze(
        context
    )


    trace_result = TraceAgent().analyze(
        context
    )



    evidence = [

        log_result,

        metric_result,

        trace_result

    ]



    final = ReasoningAgent().analyze(
        evidence
    )


    print(final)