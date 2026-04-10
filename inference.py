import json
import os
from typing import List, Optional

from openai import OpenAI

from client import InboxPilotEnvClient
from models import SupportAction

# ✅ Use Scaler-injected env vars — DO NOT hardcode or use fallback credentials
API_KEY = os.environ["API_KEY"]
API_BASE_URL = os.environ["API_BASE_URL"]
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
HF_SPACE_URL = os.getenv("HF_SPACE_URL", "https://navyansh77-inboxpilot-openenv1-0.hf.space")

TASKS = ["easy", "medium", "hard"]
BENCHMARK = "inboxpilot-openenv"
SUCCESS_SCORE_THRESHOLD = 0.5


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def build_prompt(observation) -> str:
    return f"""
You are a customer support triage assistant.

Return a valid JSON object with exactly these keys:
category, priority, escalate, request_more_info, response_draft, resolution_status

Allowed category values:
refund, billing, technical_issue, account_access, shipping, general_query, complaint

Allowed priority values:
low, medium, high, urgent

Allowed resolution_status values:
open, waiting_for_customer, resolved, escalated

escalate and request_more_info must be true or false (boolean).

Ticket ID: {observation.ticket_id}
Customer tier: {observation.customer_tier}
Subject: {observation.subject}
Email body: {observation.email_body}
Previous interactions: {observation.previous_interactions}
Sentiment hint: {observation.sentiment_hint}
SLA hours remaining: {observation.sla_hours_remaining}

Return JSON only. No markdown, no explanation.
""".strip()


def llm_action(client: OpenAI, observation) -> dict:
    """
    Makes LLM call through Scaler's proxy (client is initialized with
    API_BASE_URL and API_KEY from environment — required by the validator).
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise support triage assistant that returns valid JSON only. No markdown, no explanation.",
                },
                {
                    "role": "user",
                    "content": build_prompt(observation),
                },
            ],
            temperature=0.2,
            max_tokens=300,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        raise


def main() -> None:
    print(f"[DEBUG] API_BASE_URL={API_BASE_URL}", flush=True)
    print(f"[DEBUG] API_KEY={'SET' if API_KEY else 'NOT SET'}", flush=True)
    print(f"[DEBUG] MODEL_NAME={MODEL_NAME}", flush=True)

    # ✅ OpenAI client MUST use Scaler's base_url and api_key
    # This is what the LLM Criteria Check validates
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # The env client connects to your HF Space (not the LLM proxy)
    env = InboxPilotEnvClient(base_url=HF_SPACE_URL)

    for task in TASKS:
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False

        log_start(task=task, env=BENCHMARK, model=MODEL_NAME)

        try:
            result = env.reset(task_name=task)
            observation = result.observation

            # ✅ LLM call goes through Scaler's proxy via `client`
            action_dict = llm_action(client, observation)
            action_str = json.dumps(action_dict, separators=(",", ":"))

            action_obj = SupportAction(**action_dict)
            result = env.step(action_obj)

            reward = float(result.reward or 0.0)
            done = bool(result.done)
            steps_taken = 1
            rewards.append(reward)

            log_step(step=1, action=action_str, reward=reward, done=done, error=None)

            score = min(max(reward, 0.0), 1.0)
            success = score >= SUCCESS_SCORE_THRESHOLD

        except Exception as exc:
            log_step(step=1, action="null", reward=0.00, done=True, error=str(exc))
            score = 0.0
            success = False
            steps_taken = 1
            rewards.append(0.0)

        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()
