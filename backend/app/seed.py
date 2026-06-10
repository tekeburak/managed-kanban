from app.models import Column, Priority, Ticket

SEED_TICKETS: list[Ticket] = [
    Ticket(
        id="TICKET-1",
        title="Optimize website performance",
        description=(
            "Apply six exact edits to /workspace/repo/index.html using the "
            "str_replace tool. DO NOT read or open any other file. DO NOT "
            "view index.html first. DO NOT analyze. Just str_replace, commit, "
            "push. Estimated SCORE: 35 -> 92.\n\n"
            "EDIT 1 — add viewport meta:\n"
            "  old_str: '  <meta charset=\"utf-8\">\\n'\n"
            "  new_str: '  <meta charset=\"utf-8\">\\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\\n'\n\n"
            "EDIT 2 — gate print.css to print media:\n"
            "  old_str: '<link rel=\"stylesheet\" href=\"css/print.css\">'\n"
            "  new_str: '<link rel=\"stylesheet\" href=\"css/print.css\" media=\"print\">'\n\n"
            "EDIT 3 — preconnect + display=swap on Google Fonts:\n"
            "  old_str: '<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Sora:wght@100;200;300;400;500;600;700;800&family=Inter:wght@100;200;300;400;500;600;700;800;900&display=block\">'\n"
            "  new_str: '<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\\n  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\\n  <link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Sora:wght@400;700&family=Inter:wght@400;600;700&display=swap\">'\n\n"
            "EDIT 4 — defer the three head scripts in one shot:\n"
            "  old_str: '<script src=\"js/jquery-stub.js\"></script>\\n  <script src=\"js/heavy-init.js\"></script>\\n  <script src=\"js/analytics.js\"></script>'\n"
            "  new_str: '<script src=\"js/jquery-stub.js\" defer></script>\\n  <script src=\"js/heavy-init.js\" defer></script>\\n  <script src=\"js/analytics.js\" defer></script>'\n\n"
            "EDIT 5 — hero img dimensions + decoding hint:\n"
            "  old_str: '<img src=\"assets/hero.png\" class=\"hero-bg\" alt=\"\">'\n"
            "  new_str: '<img src=\"assets/hero.png\" class=\"hero-bg\" alt=\"\" width=\"1920\" height=\"1080\" decoding=\"async\" fetchpriority=\"high\">'\n\n"
            "EDIT 6 — three project images become lazy + dimensioned. Do this "
            "as ONE str_replace covering all three lines together:\n"
            "  old_str: '<img src=\"assets/proj-1.png\" class=\"card-img\" alt=\"Managed Kanban artwork\">'\n"
            "  new_str: '<img src=\"assets/proj-1.png\" class=\"card-img\" alt=\"Managed Kanban artwork\" width=\"1200\" height=\"720\" loading=\"lazy\" decoding=\"async\">'\n"
            "  Then repeat for proj-2 (alt=\"Latency Lab artwork\") and proj-3 "
            "(alt=\"Schema Migrator artwork\") with the same width/height/lazy/decoding additions.\n\n"
            "After the edits: STATUS: Committing perf fixes, then commit + push to "
            "branch agent/TICKET-1. Commit message: "
            "'perf: viewport, defer, lazy, preconnect, print media, font swap'\n"
            "Then emit SCORE: 35 -> 92 and stop.\n\n"
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
