# AI prompt log: technical questions and design decisions

Conversation dates: 2026-10-10 through 2026-10-11.
Tool: OpenAI Codex desktop.

This log groups the technical questions I asked and the implementation directions
I gave by topic. The wording is paraphrased from the conversation for clarity;
this is not a verbatim or chronological transcript. Changes of direction are
retained within each topic.

I set the three-function scope, questioned the need for additional dependencies,
requested direct SEC access, and directed the changes to packaging.
The sections below record those questions and decisions.
AI assistance is described at the end. Contact details are redacted.

## 1. Assignment scope and system approach

Questions I asked:

- How should we approach this coding assignment?
- What do the references to Docker and APIs mean for the implementation?
- After rereading the assignment, do we need to expose our own API?
- Will I be able to understand and explain this approach in the coding interview?

Directions I gave:

- Treat this as a data engineering task and use a data pipeline approach.

I also supplied the recruiter's clarification: Python was preferred; input format and output location were flexible;
Docker and an API endpoint were optional. Fetching and conversion were sufficient.
The submission needed a GitHub link, and the assignment required an AI prompt log
if AI was used. Evaluation focused on coding, problem-solving, and explaining
reasoning; heavy delegation to tools or libraries could reduce discussion value.

My scope kept the solution focused on a batch script with three main functions:
read companies, fetch reports, and convert to PDF. A web API, database, scheduler,
and pipeline framework were outside that simple implementation.

## 2. Data handling and dependencies

Questions I asked:

- Would DuckDB be useful for this task?
- Does DuckDB add enough value to justify including it?
- Is pandas actually necessary for the operations we are performing?

Directions I gave:

- Initially consider pandas or Polars for handling the filing metadata.
- Remove pandas usage once the discussion showed that plain Python could handle
  the filtering and selection.
- Keep the code small and concise, and limit that refactor to `reports.py`.

I questioned whether these dependencies added enough value for the work being
done, then requested plain Python for the metadata operations. `reports.py` now
uses lists and dictionaries. Pandas usage was removed from the source;
`requirements.txt` was left unchanged under the file-only scope of that edit.

## 3. SEC access and the hosted PDF service

Questions I asked:

- Can we obtain PDFs directly through SEC's API?
- How does PDF conversion work in the
  [sec-api-python repository](https://github.com/SEC-API-io/sec-api-python/tree/master)?
- What does `PdfGeneratorApi` in sec-api-python use to generate a PDF?
- Does that project use WeasyPrint for its conversion?

Directions I gave, in order:


- Clarify that Requests could call the hosted PDF endpoint directly.
- Later change that decision: use SEC directly and do not use sec-api.io.

I also supplied a contact email for the identifying SEC User-Agent when asked.
The address is excluded from this log.

My final direction was to fetch metadata, filing HTML, and referenced assets
from official SEC endpoints. This replaced the earlier hosted-service approach.

## 4. PDF rendering and alternatives

Questions I asked:

- Does the conversion require rendering the filing in a browser?
- Is there a tool that handles conversion without Playwright or browser automation?
- What is WeasyPrint?
- What alternatives are available to WeasyPrint?
- How do other HTML-to-PDF converters handle rendering?

Direction I gave:

- Move the CSS out of the Python code into a separate file.

I asked for alternatives to browser automation and an explanation of how the
available converters work. The resulting implementation uses WeasyPrint locally,
with the stylesheet in `reports.css` as requested. The earlier exploration of
Chromium and hosted conversion informed these follow-up questions.

## 5. Docker and the development environment

Questions I asked:

- Should we Dockerize this implementation?
- Does the dev container include the required Python packages and system libraries?

Directions I gave, in order:

- Leave Docker and additional infrastructure out of the initial simple version.
- Later add a Dockerfile and a dev container.

I deferred container setup initially, then requested it as a way to package and
develop the existing script. Both execution options use the same Dockerfile,
which includes the Python requirements, native PDF libraries, and fonts.

## Other project instructions

I instructed that the repository should not be pushed. I also requested a message to HR
explaining that I had been on vacation until the previous day and planned to
complete the assessment over the weekend. A draft was prepared; it was not sent.

For this log, I requested clearer wording and a topic-based account of my
technical questions, with the decisions I directed made explicit.

## AI assistance

I also asked Codex to write the README and update the dev container setup and run
instructions.

I used OpenAI Codex to explore implementation options, generate
and refactor Python and container configuration, troubleshoot PDF output, draft
documentation. I supplied the
requirements and directed the scope, tool choices, and simplifications recorded
in this log. No subagents were used. Contact information and credentials are
excluded.
