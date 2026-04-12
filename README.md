---
title: InboxPilot-OpenEnv
emoji: 👀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# InboxPilot-OpenEnv

Built for the Meta x Hugging Face OpenEnv Hackathon 🚀

InboxPilot-OpenEnv is a real-world customer support triage environment for evaluating AI agents using the OpenEnv standard.

## Overview

This project simulates a realistic customer support workflow where an AI agent must:

- classify the issue category
- assign a priority level
- decide whether escalation is needed
- draft a customer response
- choose a resolution status

The environment is designed to be lightweight, structured, and suitable for automated evaluation.

## Why this matters

Customer support triage is a real business workflow used in SaaS, e-commerce, and enterprise platforms. InboxPilot turns that workflow into a benchmarkable environment for AI agents.

## Tasks

The environment includes 3 tasks with increasing difficulty:

- **Easy** — damaged product refund request
- **Medium** — duplicate billing issue from a premium user
- **Hard** — enterprise outage complaint requiring urgent escalation

## Action Space

The agent returns a structured action with:

- `category`
- `priority`
- `escalate`
- `request_more_info`
- `response_draft`
- `resolution_status`

## Observation Space

The environment returns structured observations including:

- `ticket_id`
- `customer_tier`
- `subject`
- `email_body`
- `previous_interactions`
- `sentiment_hint`
- `sla_hours_remaining`
- `allowed_actions`

## Reward Logic

The reward is a partial score between `0.0` and `1.0`.

Scoring breakdown:

- category correctness → `0.25`
- priority correctness → `0.20`
- escalation correctness → `0.20`
- resolution status correctness → `0.10`
- response relevance → up to `0.25`

This creates meaningful partial progress signals instead of simple pass/fail scoring.

## Project Structure

```text
inboxpilot_openenv/
├── Dockerfile
├── __init__.py
├── models.py
├── client.py
├── inference.py
├── openenv.yaml
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── tasks/
│   ├── easy.json
│   ├── medium.json
│   └── hard.json
└── server/
    ├── __init__.py
    ├── environment.py
    └──  app.py