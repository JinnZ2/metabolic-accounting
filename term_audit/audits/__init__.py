"""
term_audit/audits/

Concrete audits of specific economic terms against the term_audit schema.
Each module in this subpackage exports a single `*_AUDIT` constant (a
TermAudit instance) plus a `__main__` block that prints the summary when
run directly.

These are not tests of the schema itself (those live in
tests/test_term_audit.py). They are the outputs of applying the schema
to real terms, each with source references and a reviewable argument.
Disagree with the scoring? Fork the file and argue with a counter-audit.

Import the audit you want directly, e.g.:
    from term_audit.audits.money import MONEY_AUDIT
"""
