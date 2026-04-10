from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult

from models import SupportAction, SupportObservation, SupportState


class InboxPilotEnvClient(EnvClient[SupportAction, SupportObservation, SupportState]):

    def _step_payload(self, action: SupportAction) -> dict:
        return {
            "category": action.category,
            "priority": action.priority,
            "escalate": action.escalate,
            "request_more_info": action.request_more_info,
            "response_draft": action.response_draft,
            "resolution_status": action.resolution_status,
        }

    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})

        observation = SupportObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            ticket_id=obs_data.get("ticket_id", ""),
            customer_tier=obs_data.get("customer_tier", ""),
            subject=obs_data.get("subject", ""),
            email_body=obs_data.get("email_body", ""),
            previous_interactions=obs_data.get("previous_interactions", []),
            sentiment_hint=obs_data.get("sentiment_hint", "neutral"),
            sla_hours_remaining=obs_data.get("sla_hours_remaining", 0),
            allowed_actions=obs_data.get("allowed_actions", []),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> SupportState:
        return SupportState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            current_task_name=payload.get("current_task_name", ""),
            ticket_id=payload.get("ticket_id", ""),
            customer_tier=payload.get("customer_tier", ""),
            expected_category=payload.get("expected_category", ""),
            expected_priority=payload.get("expected_priority", ""),
            expected_escalate=payload.get("expected_escalate", False),
            expected_resolution_status=payload.get("expected_resolution_status", ""),
            last_reward=payload.get("last_reward", 0.0),
            completed=payload.get("completed", False),
        )