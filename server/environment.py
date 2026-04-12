import os
import json
import uuid
from typing import List

from openenv.core.env_server import Environment

from models import SupportAction, SupportObservation, SupportState


class InboxPilotEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    # Shared memory across requests/instances on the same running app
    _shared_task: dict | None = None
    _shared_task_name: str = "easy"
    _shared_done: bool = False
    _shared_state: SupportState = SupportState()

    def __init__(self, tasks_dir: str | None = None):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.tasks_dir = tasks_dir or os.path.join(base_dir, "tasks")
        self._state = InboxPilotEnvironment._shared_state
        self._current_task = InboxPilotEnvironment._shared_task
        self._done = InboxPilotEnvironment._shared_done

    def _sync_shared(self) -> None:
        InboxPilotEnvironment._shared_task = self._current_task
        InboxPilotEnvironment._shared_done = self._done
        InboxPilotEnvironment._shared_state = self._state

    def _load_task(self, task_name: str) -> dict:
        path = os.path.join(self.tasks_dir, f"{task_name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Task file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _allowed_actions(self) -> List[str]:
        return [
            "classify_category",
            "assign_priority",
            "decide_escalation",
            "draft_response",
            "set_resolution_status",
        ]

    def _response_score(self, response_text: str, keywords: list[str]) -> float:
        if not keywords:
            return 0.0
        text = response_text.lower()
        matched = sum(1 for word in keywords if word.lower() in text)
        return round((matched / len(keywords)) * 0.25, 3)

    def reset(
        self,
        seed=None,
        episode_id=None,
        task_name: str = "easy",
        **kwargs,
    ) -> SupportObservation:
        self._current_task = self._load_task(task_name)
        self._done = False
        InboxPilotEnvironment._shared_task_name = task_name

        expected = self._current_task["expected_action"]

        self._state = SupportState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task_name=task_name,
            ticket_id=self._current_task["task_id"],
            customer_tier=self._current_task["customer_tier"],
            expected_category=expected["category"],
            expected_priority=expected["priority"],
            expected_escalate=expected["escalate"],
            expected_resolution_status=expected["resolution_status"],
            last_reward=0.0,
            completed=False,
        )
        self._sync_shared()

        return SupportObservation(
            done=False,
            reward=None,
            ticket_id=self._current_task["task_id"],
            customer_tier=self._current_task["customer_tier"],
            subject=self._current_task["subject"],
            email_body=self._current_task["email_body"],
            previous_interactions=self._current_task.get("previous_interactions", []),
            sentiment_hint=self._current_task["sentiment_hint"],
            sla_hours_remaining=self._current_task["sla_hours_remaining"],
            allowed_actions=self._allowed_actions(),
        )

    def step(
        self,
        action: SupportAction | dict,
        timeout_s=None,
        **kwargs,
    ) -> SupportObservation:
        # Reload shared state for stateless Swagger/API requests
        self._current_task = InboxPilotEnvironment._shared_task
        self._done = InboxPilotEnvironment._shared_done
        self._state = InboxPilotEnvironment._shared_state

        if self._current_task is None:
            task_name = InboxPilotEnvironment._shared_task_name
            self._current_task = self._load_task(task_name)
            expected = self._current_task["expected_action"]
            self._state = SupportState(
                episode_id=str(uuid.uuid4()),
                step_count=0,
                current_task_name=task_name,
                ticket_id=self._current_task["task_id"],
                customer_tier=self._current_task["customer_tier"],
                expected_category=expected["category"],
                expected_priority=expected["priority"],
                expected_escalate=expected["escalate"],
                expected_resolution_status=expected["resolution_status"],
                last_reward=0.0,
                completed=False,
            )
            self._done = False

        if self._done:
            raise ValueError("Task already completed. Call reset() for a new task.")

        if isinstance(action, dict):
            action = SupportAction(**action)

        self._state.step_count += 1

        expected = self._current_task["expected_action"]
        keywords = self._current_task.get("response_keywords", [])

        category_score = 0.25 if action.category == expected["category"] else 0.0
        priority_score = 0.20 if action.priority == expected["priority"] else 0.0
        escalation_score = 0.20 if action.escalate == expected["escalate"] else 0.0
        resolution_score = (
            0.10 if action.resolution_status == expected["resolution_status"] else 0.0
        )
        response_score = self._response_score(action.response_draft, keywords)

        total_reward = round(
            category_score
            + priority_score
            + escalation_score
            + resolution_score
            + response_score,
            3,
        )

        self._done = True
        self._state.last_reward = total_reward
        self._state.completed = True
        self._sync_shared()

        return SupportObservation(
            done=True,
            reward=total_reward,
            ticket_id=self._current_task["task_id"],
            customer_tier=self._current_task["customer_tier"],
            subject=self._current_task["subject"],
            email_body=self._current_task["email_body"],
            previous_interactions=self._current_task.get("previous_interactions", []),
            sentiment_hint=self._current_task["sentiment_hint"],
            sla_hours_remaining=self._current_task["sla_hours_remaining"],
            allowed_actions=self._allowed_actions(),
        )

    @property
    def state(self) -> SupportState:
        return InboxPilotEnvironment._shared_state