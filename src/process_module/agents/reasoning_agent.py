from __future__ import annotations

import json

from google.genai import types

from src.process_module.agents.base_agent import BaseAgent


class ReasoningAgent(BaseAgent):

    def __init__(self, config=None):
        super().__init__("Reasoning Agent", config=config)

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        context,
        evidence_df
    ) -> dict:

        """
        Reasoning Agent

        Input:
            - investigation context
            - evidence_records loaded from PostgreSQL

        Output:
            - root cause
            - confidence
            - explanation
            - supporting evidence

        The agent reasons ONLY from evidence_records.
        """

        # =====================================================
        # 1. GET CONTEXT
        # =====================================================

        investigation_id = getattr(
            context,
            "investigation_id",
            None
        )

        service = getattr(
            context,
            "service",
            "unknown"
        )

        incident_time = getattr(
            context,
            "incident_time",
            ""
        )

        incident_description = getattr(
            context,
            "incident_description",
            ""
        )

        # =====================================================
        # 2. VALIDATE EVIDENCE
        # =====================================================

        if evidence_df is None:

            return {
                "agent": "Reasoning Agent",
                "root_cause": "Insufficient evidence",
                "confidence": 0.0,
                "explanation": (
                    "No evidence was provided "
                    "to the Reasoning Agent."
                ),
                "supporting_evidence": []
            }

        if evidence_df.empty:

            return {
                "agent": "Reasoning Agent",
                "root_cause": "Insufficient evidence",
                "confidence": 0.0,
                "explanation": (
                    "No evidence was found in "
                    "evidence_records."
                ),
                "supporting_evidence": []
            }

        # =====================================================
        # 3. CONVERT DATABASE EVIDENCE TO JSON
        # =====================================================

        evidence = evidence_df.to_dict(
            orient="records"
        )

        # =====================================================
        # 4. NORMALIZE EVIDENCE
        # =====================================================

        metric_evidence = [
            item
            for item in evidence
            if item.get("evidence_type") == "metric"
        ]

        log_evidence = [
            item
            for item in evidence
            if item.get("evidence_type") == "log"
        ]

        trace_evidence = [
            item
            for item in evidence
            if item.get("evidence_type") == "trace"
        ]

        # =====================================================
        # 5. EVIDENCE SUMMARY
        # =====================================================

        evidence_types = sorted(
            list(
                set(
                    item.get("evidence_type")
                    for item in evidence
                    if item.get("evidence_type")
                )
            )
        )

        evidence_summary = {
            "metric_count": len(metric_evidence),
            "log_count": len(log_evidence),
            "trace_count": len(trace_evidence),
            "total_count": len(evidence),
            "available_types": evidence_types
        }

        # =====================================================
        # 6. BUILD TARGET-SERVICE EVIDENCE
        # =====================================================

        target_metric_evidence = [
            item
            for item in metric_evidence
            if item.get("service") == service
        ]

        target_log_evidence = [
            item
            for item in log_evidence
            if item.get("service") == service
        ]

        target_trace_evidence = [
            item
            for item in trace_evidence
            if item.get("service") == service
        ]

        target_evidence_summary = {
            "metric_count": len(target_metric_evidence),
            "log_count": len(target_log_evidence),
            "trace_count": len(target_trace_evidence)
        }

        # =====================================================
        # 7. PREPARE GEMINI PROMPT
        # =====================================================

        prompt = f"""
You are an SRE Root Cause Analysis Reasoning Agent.

Your task is to determine the MOST LIKELY root cause
of an incident using ONLY the supplied evidence.

====================================================
INCIDENT CONTEXT
====================================================

Investigation ID:
{investigation_id}

Target Service:
{service}

Incident Time:
{incident_time}

Incident Description:
{incident_description}


====================================================
EVIDENCE SUMMARY
====================================================

{json.dumps(
    evidence_summary,
    indent=2,
    default=str
)}

Evidence directly belonging to target service:

{json.dumps(
    target_evidence_summary,
    indent=2,
    default=str
)}


====================================================
METRIC EVIDENCE
====================================================

{json.dumps(
    metric_evidence,
    indent=2,
    default=str
)}


====================================================
LOG EVIDENCE
====================================================

{json.dumps(
    log_evidence,
    indent=2,
    default=str
)}


====================================================
TRACE EVIDENCE
====================================================

{json.dumps(
    trace_evidence,
    indent=2,
    default=str
)}


====================================================
REASONING RULES
====================================================

1. Use ONLY the supplied evidence.

2. Do NOT invent:
   - services
   - errors
   - timestamps
   - metric values
   - trace relationships
   - dependencies
   - infrastructure failures

3. Evidence does NOT need to contain all three types.

4. Metric + trace evidence CAN be sufficient
   to determine a likely root cause when they
   support the same failure pattern.

5. Metric evidence can establish:
   - abnormal latency
   - abnormal request duration
   - deviation from baseline
   - performance degradation

6. Trace evidence can establish:
   - abnormal latency
   - affected operation
   - affected service
   - dependency relationships
   - request path

7. Log evidence is useful but NOT mandatory.

8. If multiple evidence types independently
   support the SAME service or failure pattern,
   increase confidence.

9. Prefer evidence belonging directly to the
   target service.

10. Evidence from another service may only be used
    when the supplied evidence explicitly shows
    a dependency or relationship to the target service.

11. Do NOT reject an RCA simply because logs
    are unavailable.

12. If metric and trace evidence show a consistent
    latency/performance degradation pattern,
    identify the most likely technical root cause
    supported by those observations.

13. If only metric evidence exists, a likely
    performance-related root cause may still be
    returned, but confidence should be moderate
    or low.

14. If evidence is genuinely contradictory,
    explicitly state that it is conflicting.

15. If evidence is genuinely insufficient to
    determine any reasonable root cause,
    return:
    "Insufficient evidence"

16. Confidence MUST be between 0 and 100.

17. Confidence must reflect evidence strength:

    - 0-20:
      almost no useful evidence

    - 21-40:
      weak evidence

    - 41-60:
      moderate evidence

    - 61-80:
      strong evidence

    - 81-100:
      very strong evidence with multiple
      independent evidence types supporting
      the same conclusion

18. Do NOT claim certainty unless the evidence
    strongly supports it.

19. The explanation MUST explicitly explain:
    - what anomaly was observed
    - which evidence supports it
    - how the evidence relates to the target service
    - why the proposed root cause is the most likely

20. supporting_evidence MUST contain actual
    evidence records from the supplied data.

21. Do NOT return empty supporting_evidence when
    useful evidence exists.

22. Return ONLY valid JSON.


====================================================
IMPORTANT INTERPRETATION
====================================================

For example, if the target service has:

- multiple metric anomalies showing request latency
  significantly above baseline

AND

- trace anomalies showing the same service or
  directly related operation has significantly
  elevated latency

then this should NOT automatically be classified
as "Insufficient evidence".

Instead, identify the most likely performance
failure supported by the evidence.

However, if trace evidence belongs to an unrelated
service and no supplied dependency connects it to
the target service, do NOT use that trace as proof
of the target service's root cause.


====================================================
REQUIRED OUTPUT FORMAT
====================================================

{{
    "agent": "Reasoning Agent",

    "root_cause": "",

    "confidence": 0.0,

    "explanation": "",

    "supporting_evidence": [
        {{
            "evidence_type": "",
            "service": "",
            "description": "",
            "score": 0.0
        }}
    ]
}}

"""

        # =====================================================
        # 8. CALL GEMINI
        # =====================================================

        try:

            response = self.client.models.generate_content(

                model=self.model_name,

                contents=prompt,

                config=types.GenerateContentConfig(

                    temperature=0.1,

                    response_mime_type="application/json"

                )
            )

            text = response.text.strip()

            print(
                "\n========== REASONING RESPONSE =========="
            )

            print(text)

            print(
                "========================================"
            )

            result = json.loads(text)

            # =================================================
            # 9. NORMALIZE RESULT
            # =================================================

            result.setdefault(
                "agent",
                "Reasoning Agent"
            )

            result.setdefault(
                "root_cause",
                "Insufficient evidence"
            )

            result.setdefault(
                "confidence",
                0.0
            )

            result.setdefault(
                "explanation",
                ""
            )

            result.setdefault(
                "supporting_evidence",
                []
            )

            # =================================================
            # 10. NORMALIZE CONFIDENCE
            # =================================================

            try:

                result["confidence"] = float(
                    result["confidence"]
                )

            except (
                TypeError,
                ValueError
            ):

                result["confidence"] = 0.0

            result["confidence"] = max(
                0.0,
                min(
                    100.0,
                    result["confidence"]
                )
            )

            # =================================================
            # 11. NORMALIZE SUPPORTING EVIDENCE
            # =================================================

            if not isinstance(
                result["supporting_evidence"],
                list
            ):

                result["supporting_evidence"] = []

            # If Gemini returned no supporting evidence
            # even though evidence exists, attach the
            # strongest available evidence records.

            if (
                not result["supporting_evidence"]
                and evidence
                and result["root_cause"]
                != "Insufficient evidence"
            ):

                strongest = sorted(
                    evidence,
                    key=lambda x: float(
                        x.get("score") or 0
                    ),
                    reverse=True
                )[:5]

                result["supporting_evidence"] = [

                    {
                        "evidence_type": item.get(
                            "evidence_type",
                            ""
                        ),

                        "service": item.get(
                            "service",
                            ""
                        ),

                        "description": item.get(
                            "description",
                            ""
                        ),

                        "score": float(
                            item.get("score") or 0
                        )
                    }

                    for item in strongest
                ]

            return result

        # =====================================================
        # 12. FALLBACK
        # =====================================================

        except Exception as e:

            return {
                "agent": "Reasoning Agent",

                "root_cause": (
                    "Reasoning analysis failed"
                ),

                "confidence": 0.0,

                "explanation": (
                    "Gemini reasoning failed: "
                    f"{str(e)}"
                ),

                "supporting_evidence": evidence[:10]
            }
