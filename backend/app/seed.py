from app.models import Column, Priority, Ticket

SEED_TICKETS: list[Ticket] = [
    Ticket(
        id="TICKET-1",
        title="Optimize website performance",
        description=(
            "First, create a realistic but deliberately unoptimized landing page "
            "in the workspace at ./site/index.html: large unminified JS, render-blocking "
            "scripts, no defer attribute, oversized hero image. Then run Lighthouse via "
            "bash to capture the baseline performance score, make targeted improvements "
            "(defer non-critical JS, compress assets, inline critical CSS), and re-run "
            "Lighthouse until the score is at or above 90. Self-grade against the rubric "
            "after each attempt and stop after 3 attempts max."
        ),
        priority=Priority.HIGH,
        tag="Performance",
        column=Column.BACKLOG,
    ),
    Ticket(
        id="TICKET-2",
        title="SaaS pricing audit and weekly report",
        description=(
            "Track pricing and plan changes across the SaaS tools our company uses. "
            "Search the web for the current published pricing of: Linear, Vercel, "
            "GitHub, Notion, and Anthropic. Compare against memory of last week's "
            "pricing if available, write a one-page markdown report to "
            "./reports/pricing-{date}.md highlighting any deltas, then update memory."
        ),
        priority=Priority.MEDIUM,
        tag="Research",
        column=Column.BACKLOG,
    ),
    Ticket(
        id="TICKET-3",
        title="Incident response: API latency spike",
        description=(
            "ALERT: P1 — API response times spiked to 4200ms (threshold: 500ms) at "
            "2026-04-30T19:42Z. Investigate by reading the simulated logs at "
            "./incident/access.log and ./incident/db-slow.log, identify the most "
            "likely root cause, propose a remediation, and produce a post-incident "
            "summary at ./incident/postmortem.md. Output STATUS: lines as you progress."
        ),
        priority=Priority.HIGH,
        tag="Incident",
        column=Column.BACKLOG,
    ),
]
