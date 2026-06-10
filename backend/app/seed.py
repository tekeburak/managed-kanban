from app.models import Column, Priority, Ticket

SEED_TICKETS: list[Ticket] = [
    Ticket(
        id="TICKET-1",
        title="Optimize website performance",
        description=(
            "Audit my portfolio site for Core Web Vitals and front-end performance "
            "issues. The repo is mounted at /workspace/repo. Fetch the live page to "
            "baseline, then read the source from the mount and identify the highest-"
            "impact problems (render-blocking CSS, sync scripts in head, "
            "unoptimized images, missing viewport / lazy-loading / preconnect).\n\n"
            "Apply the fixes directly: defer/async non-critical scripts, add "
            "media=print to print.css, add a viewport meta, add loading=lazy + "
            "width/height on imgs, preconnect to fonts.googleapis.com, switch "
            "font display=block to swap.\n\n"
            "Push to branch agent/TICKET-1 (NOT main). A human reviewer will "
            "fast-forward main from the branch after they accept the change, "
            "which triggers the Cloudflare Pages redeploy. Output one "
            "SCORE: <before> -> <after> line with your estimated Lighthouse "
            "Performance score before and after.\n\n"
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
