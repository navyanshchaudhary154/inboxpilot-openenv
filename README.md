---

title: InboxPilot-OpenEnv
emoji: 👀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
--------------

# InboxPilot-OpenEnv 🚀

**Built for the Meta × Hugging Face OpenEnv Hackathon**

InboxPilot-OpenEnv is a **real-world customer support triage simulation environment** designed to evaluate AI agents using the OpenEnv standard.

It transforms a common business workflow into a structured, testable environment where agents can be trained, evaluated, and benchmarked.

---

## 🔍 Overview

InboxPilot simulates how modern customer support systems operate.

Given a customer ticket, an AI agent must:

* understand the issue
* make structured decisions
* generate a useful human-like response

This environment is intentionally designed to reflect **real production scenarios**, not toy problems.

---

## 💡 Why this matters

Customer support triage is a **critical real-world workflow** used across:

* SaaS platforms
* E-commerce systems
* Enterprise support teams

Poor triage leads to:

* delayed resolutions
* customer dissatisfaction
* increased operational cost

InboxPilot turns this workflow into a **benchmarkable AI environment**, enabling:

* consistent evaluation of agents
* measurable performance scoring
* realistic decision-making challenges

---

## 🧠 Tasks

The environment includes **three progressively challenging tasks**:

### 🟢 Easy

A straightforward damaged product refund request
→ Focus: classification + basic response

### 🟡 Medium

A duplicate billing issue from a premium user
→ Focus: prioritization + customer sensitivity

### 🔴 Hard

An enterprise-level outage complaint
→ Focus: escalation, urgency, and structured handling

---

## ⚙️ Action Space

The agent must return a **structured action object**:

* `category` → type of issue (refund, billing, technical, etc.)
* `priority` → low / medium / high
* `escalate` → whether human intervention is required
* `request_more_info` → if clarification is needed
* `response_draft` → message to the customer
* `resolution_status` → resolved / pending / escalated

---

## 📥 Observation Space

Each step returns a structured observation:

* `ticket_id`
* `customer_tier` (free / premium / enterprise)
* `subject`
* `email_body`
* `previous_interactions`
* `sentiment_hint`
* `sla_hours_remaining`
* `allowed_actions`

This ensures the agent operates with **context similar to real support systems**.

---

## 🎯 Reward Function

The environment provides a **continuous reward signal (0.0 → 1.0)**.

### Scoring Breakdown:

* category correctness → **0.25**
* priority correctness → **0.20**
* escalation decision → **0.20**
* resolution status → **0.10**
* response quality → **up to 0.25**

This allows:

* partial credit
* nuanced evaluation
* better learning signals for agents

---

## 🏗️ Project Structure

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
<<<<<<< HEAD
    └── app.py
```

---

## 🚀 Key Highlights

* ✅ Real-world task simulation (not a toy problem)
* ✅ Fully structured OpenEnv-compatible environment
* ✅ Multi-level difficulty with graded evaluation
* ✅ Partial reward scoring for better agent learning
* ✅ Ready for deployment on Hugging Face Spaces

---

## 🧪 Usage

Once deployed, the environment exposes standard OpenEnv endpoints:

* `/reset` → initialize a new task
* `/step` → perform an action
* `/state` → get current environment state

Agents can interact programmatically or via API testing tools.

---

## ⚠️ Notes

* The environment uses the **LiteLLM proxy provided during evaluation**
* All LLM calls are routed via injected environment variables
* Designed to comply fully with OpenEnv validation requirements

---

## 📌 Final Thoughts

InboxPilot is built with one goal:

> **Make AI evaluation feel like the real world.**

Instead of abstract benchmarks, it focuses on practical decision-making, structured outputs, and measurable impact.

---

**Built with focus, iteration, and a bit of chaos 😄**
=======
    └──  app.py
>>>>>>> 5ce4fc8aa6735d1c80302c6718c2bb808d8a22e0
