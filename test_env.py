from env import InboxPilotEnv

# Create environment
env = InboxPilotEnv()

# Step 1: Reset (load task)
obs = env.reset("easy")

print("=== OBSERVATION ===")
print(obs)

# Step 2: Fake AI action (correct one)
action = {
    "category": "refund",
    "priority": "medium",
    "escalate": False,
    "request_more_info": True,
    "response_draft": "Sorry for the issue. Please share a photo of the damaged product and your order ID so we can process your refund quickly.",
    "resolution_status": "waiting_for_customer"
}

# Step 3: Step
result = env.step(action)

print("\n=== RESULT ===")
print(result)

# Step 4: State
print("\n=== STATE ===")
print(env.state())