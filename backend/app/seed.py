from app.models import Column, Priority, Ticket

SEED_TICKETS: list[Ticket] = [
    Ticket(
        id="TICKET-1",
        title="Optimize website performance",
        description=(
            "The portfolio repo is mounted at /workspace/repo. Read index.html "
            "plus the four CSS files and three JS files referenced from <head> "
            "to spot the obvious perf wins, then apply ALL of these fixes "
            "directly to the source (do not fetch the live page — work from "
            "the mount):\n"
            "  - add <meta name=viewport content=...>\n"
            "  - add media=\"print\" to css/print.css link\n"
            "  - add defer to all three <script> tags in <head>\n"
            "  - add loading=\"lazy\" plus width/height to every <img>\n"
            "  - add <link rel=preconnect href=\"https://fonts.googleapis.com\"> "
            "and switch the Google Fonts URL to display=swap\n\n"
            "Push to branch agent/TICKET-1 (NOT main). A human reviewer will "
            "fast-forward main on Done, which triggers the Cloudflare Pages "
            "redeploy. Output one SCORE: <before> -> <after> line — "
            "estimated Lighthouse Performance, around 35 -> 92.\n\n"
            "Live site: https://portfolio-539.pages.dev/\n"
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
