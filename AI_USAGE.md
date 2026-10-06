# AI usage disclosure

## Tool used

OpenAI Codex (ChatGPT) was used in this project session to inspect the provided assignment/reference document, draft the scraper and processing modules, create offline tests, and write the documentation.

## Representative prompts

- “Complete the Python web scraping take-home assignment in my current project folder. First inspect my existing files and folder structure.”
- “Follow the assignment requirements exactly: scrape Books to Scrape and Quotes to Scrape with dynamic Next links, clean, validate, deduplicate, and produce a CSV and JSON report.”
- “Actually run the scraper and tests; inspect the generated files and verify both sources, ratings, prices, and reconciled counts.”

## AI-assisted work

The initial project structure and source code, data cleaning/validation/fingerprinting functions, tests, README, and this disclosure were AI-assisted. The operator remains responsible for understanding and reviewing the delivered implementation.

## Review changes and issues

The reference guidance was reviewed before implementation. The code leaves book category and description empty because listing cards do not supply them, and defines quote source URLs as listing-page URLs. Retry behavior is configured for temporary HTTP errors; page-level failures are logged and end that source while allowing the next source to run. These choices are documented. No external network results have yet been used to claim a scrape count in this document; the actual run results belong in the generated report and final verification.

The first test run exposed an edge case in quote-mark cleanup: spaces inside the outer curly quotes remained at the text edges after removing the marks. The cleaner was corrected to trim again after quote removal, and the test now covers it.

## Verification record

Verification performed: `python -m pytest -q` passed all 7 offline tests. `python main.py` completed against both live practice sites, following all next links. The run collected 1,000 Books to Scrape records and 100 Quotes to Scrape records, rejected 0, detected and removed 1 duplicate, and wrote 1,099 CSV rows. The generated CSV was parsed and checked: both sources are present, all non-empty prices are numeric and non-negative, all non-empty ratings are integers from 1 to 5, and the final/rejection/deduplication counts reconcile with the CSV. The generated log records page progress through both sites. The current execution environment reports Python 3.13.7, outside the assignment's 3.10–3.12 target; the code is written using 3.10-compatible language features.
