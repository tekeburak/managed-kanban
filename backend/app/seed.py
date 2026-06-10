from app.models import Column, Priority, Ticket

SEED_TICKETS: list[Ticket] = [
    Ticket(
        id="TICKET-1",
        title="Optimize website performance",
        description=(
            "Audit my portfolio site for Core Web Vitals and front-end performance "
            "issues. Fetch the live page and its linked CSS/JS, identify the "
            "highest-impact problems (render-blocking resources, unoptimized "
            "images, sync scripts, missing viewport/meta), and propose concrete "
            "fixes for each. Output one SCORE: <before> -> <after> line that "
            "reflects the estimated Lighthouse Performance score before and after "
            "applying your recommendations (0-100). Then narrate the top 5 fixes "
            "ranked by expected impact.\n\n"
            "Live site: https://tekeburak.github.io/portfolio/\n"
            "Source:    https://github.com/tekeburak/portfolio"
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
