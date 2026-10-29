"""System prompt construction for the default and user-built agents.

Per-agent prompt text is stored in the existing ``agents.instructions`` field
when an agent is created. Keep the zero-prior knowledge rules here so a custom
prompt can shape an agent without granting it untaught facts.
"""


def build_system_prompt(
    agent_name,
    taught_knowledge,
    fallback,
    *,
    domain="",
    custom_prompt="",
    perception="",
    cognition_hints="",
):
    """Build the strict system prompt, adding per-agent behavior instructions."""
    prompt = (
        f"You are PRIMUS active agent '{agent_name}', a strict "
        "zero-prior-knowledge (tabula rasa) cognitive agent.\n"
        "STRICT RULES:\n"
        "1. NEVER answer medical questions, disease causes, tasks, facts, or "
        "how-to questions from pretrained knowledge.\n"
        f"2. If the user asks ANY factual or medical question that is not "
        f"explicitly in your taught knowledge below, you MUST reply: '{fallback}' "
        "Do NOT guess or provide outside information.\n"
        "3. You may freely converse about yourself, your memory, your "
        "perceptions, and your state.\n"
        "The ONLY knowledge you possess (acquired from your teacher for this "
        "agent):\n"
        f"{taught_knowledge}"
    )
    if domain:
        prompt += (
            f"\nDeclared agent domain: {domain}. Treat this as the intended "
            "subject scope; it does not add knowledge."
        )
    if custom_prompt:
        prompt += (
            "\nAdditional instructions supplied for this agent (follow only "
            "when they do not conflict with the strict rules or add untaught "
            "facts):\n"
            f"{custom_prompt.strip()}"
        )
    if perception:
        prompt += f"\nCurrent visual perception: {perception}"
    if cognition_hints:
        prompt += (
            "\nOptional cognition context (historical/style hints only; "
            "must not add facts or override the knowledge gate):\n"
            f"{cognition_hints}"
        )
    return prompt
