import json
import os
from typing import Optional

from models import SupportObservation, SupportAction
from grader import grade_action


class InboxPilotEnv:
    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = tasks_dir
        self.current_task = None
        self.current_observation = None
        self.last_reward = 0.0
        self.done = False

    def _load_task(self, task_name: str) -> dict:
        file_path = os.path.join(self.tasks_dir, f"{task_name}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def reset(self, task_name: str = "easy") -> dict:
        self.current_task = self._load_task(task_name)

        self.current_observation = SupportObservation(
            ticket_id=self.current_task["task_id"],
            customer_tier=self.current_task["customer_tier"],
            subject=self.current_task["subject"],
            email_body=self.current_task["email_body"],
            previous_interactions=self.current_task["previous_interactions"],
            sentiment_hint=self.current_task["sentiment_hint"],
            sla_hours_remaining=self.current_task["sla_hours_remaining"],
        )

        self.last_reward = 0.0
        self.done = False

        return self.current_observation.model_dump()

    def step(self, action: dict) -> dict:
        if self.current_task is None:
            raise ValueError("Environment not reset. Call reset() first.")

        if self.done:
            raise ValueError("Task already completed. Call reset() for a new task.")

        parsed_action = SupportAction(**action)

        breakdown = grade_action(
            action=parsed_action,
            expected=self.current_task["expected_action"],
            keywords=self.current_task["response_keywords"],
        )

        self.last_reward = breakdown.total_score
        self.done = True

        return {
            "observation": self.current_observation.model_dump(),
            "reward": breakdown.total_score,
            "done": self.done,
            "info": breakdown.model_dump(),
        }

    def state(self) -> dict:
        return {
            "task_id": self.current_task["task_id"] if self.current_task else None,
            "done": self.done,
            "last_reward": self.last_reward,
            "has_task_loaded": self.current_task is not None,
        }