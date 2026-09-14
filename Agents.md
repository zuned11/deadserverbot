Refer to SPEC.md for information on the project as needed.

Approach this project with a very minimalist perspective, aiming to minimize needed external libraries, "precautionary" additions, and generally approach with a "YAGNI" mindset.

When making changes, main branch is acceptable. Commit at regular intervals on a per-feature basis.

Avoid running the `main.py` file without some auto-stop command, as it is a long-lived process rather than a one-off script.

Err towards using patterns like composition over inheritance, and avoid tightly coupled modules.

Aim to use .env variables with defaults when missing.
