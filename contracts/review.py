# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""CortexLedger: GenLayer web-backed fact verification contract."""

from genlayer import *
import json


WIKIPEDIA_SEARCH = "https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=3&srsearch="
ALLOWED_CATEGORIES = ("Technology", "Science")


def clean_text(value: str, max_len: int) -> str:
    return " ".join(str(value).strip().split())[:max_len]


def encode_query(value: str) -> str:
    # Good enough for plain English user submissions and accepted by Wikipedia.
    return clean_text(value, 180).replace(" ", "%20").replace('"', "%22")


def sentence_count(value: str) -> int:
    count = 0
    for char in value:
        if char in ".!?":
            count += 1
    return count


def is_ascii_english(value: str) -> bool:
    if len(value.strip()) == 0:
        return False
    for char in value:
        if ord(char) > 127:
            return False
    return True


def mentions_politics(value: str) -> bool:
    lowered = value.lower()
    blocked_terms = (
        "president",
        "election",
        "senator",
        "parliament",
        "government policy",
        "politician",
        "political party",
        "congress",
        "campaign",
    )
    for term in blocked_terms:
        if term in lowered:
            return True
    return False


def valid_verdict(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if not isinstance(value.get("is_approved"), bool):
        return False
    if not isinstance(value.get("reasoning"), str):
        return False
    if not isinstance(value.get("evidence_summary"), str):
        return False
    if not isinstance(value.get("source_count"), int):
        return False
    if value["source_count"] < 0 or value["source_count"] > 3:
        return False
    return 1 <= len(value["reasoning"].strip()) <= 500


class CortexLedger(gl.Contract):
    verified_ledger: DynArray[str]
    last_verdict: str
    submissions_count: u256
    approved_count: u256

    def __init__(self):
        self.last_verdict = "No verification has been finalized yet."
        self.submissions_count = u256(0)
        self.approved_count = u256(0)

    @gl.public.view
    def get_verified_ledger(self) -> list:
        return list(self.verified_ledger)

    @gl.public.view
    def get_last_verdict(self) -> str:
        return self.last_verdict

    def _fetch_web_evidence(self, title: str, content: str) -> dict:
        query = encode_query(title + " " + content[:120])
        response = gl.nondet.web.get(WIKIPEDIA_SEARCH + query)
        payload = json.loads(response.body.decode("utf-8"))
        results = payload.get("query", {}).get("search", [])
        evidence = []
        for item in results[:3]:
            page_id = int(item.get("pageid", 0))
            page_title = clean_text(item.get("title", ""), 120)
            snippet = clean_text(item.get("snippet", ""), 300)
            evidence.append(
                {
                    "title": page_title,
                    "url": "https://en.wikipedia.org/?curid=" + str(page_id),
                    "snippet": snippet,
                }
            )
        return {"query": query, "sources": evidence}

    def _verify_with_consensus(self, category: str, title: str, content: str) -> dict:
        cat = clean_text(category, 40)
        ttl = clean_text(title, 120)
        cnt = clean_text(content, 1200)

        def leader_fn() -> str:
            evidence = self._fetch_web_evidence(ttl, cnt)

            if cat not in ALLOWED_CATEGORIES:
                verdict = {
                    "is_approved": False,
                    "reasoning": "Category rejected. Only Technology and Science are accepted.",
                    "evidence_summary": "Rule failed before web evidence was needed.",
                    "source_count": len(evidence["sources"]),
                    "sources": evidence["sources"],
                }
                return json.dumps(verdict, sort_keys=True)

            if not is_ascii_english(ttl + " " + cnt):
                verdict = {
                    "is_approved": False,
                    "reasoning": "Content rejected because it is not plain English.",
                    "evidence_summary": "Rule failed before web evidence was needed.",
                    "source_count": len(evidence["sources"]),
                    "sources": evidence["sources"],
                }
                return json.dumps(verdict, sort_keys=True)

            if mentions_politics(ttl + " " + cnt):
                verdict = {
                    "is_approved": False,
                    "reasoning": "Political topics are out of scope for CortexLedger.",
                    "evidence_summary": "Rule failed before web evidence was needed.",
                    "source_count": len(evidence["sources"]),
                    "sources": evidence["sources"],
                }
                return json.dumps(verdict, sort_keys=True)

            if sentence_count(cnt) < 2 or len(cnt) < 50:
                verdict = {
                    "is_approved": False,
                    "reasoning": "Content must contain at least two specific sentences.",
                    "evidence_summary": "Rule failed before web evidence was needed.",
                    "source_count": len(evidence["sources"]),
                    "sources": evidence["sources"],
                }
                return json.dumps(verdict, sort_keys=True)

            prompt = f"""You are a strict GenLayer fact-verification validator.

Verify the submitted Technology/Science fact using ONLY the live web evidence below.
Do not rely on training data. If the evidence is missing, weak, unrelated, or contradicts
the claim, reject it.

Category: {cat}
Title: {ttl}
Content: {cnt}
Live web evidence from Wikipedia search:
{json.dumps(evidence["sources"])}

Return ONLY JSON:
{{
  "is_approved": true_or_false,
  "reasoning": "short explanation, max 500 chars",
  "evidence_summary": "what the web evidence supports or fails to support",
  "source_count": number_of_relevant_sources_used
}}"""
            raw = gl.nondet.exec_prompt(prompt, response_format="json")
            if not isinstance(raw, dict):
                raw = json.loads(str(raw))

            verdict = {
                "is_approved": bool(raw.get("is_approved", False)),
                "reasoning": clean_text(raw.get("reasoning", ""), 500),
                "evidence_summary": clean_text(raw.get("evidence_summary", ""), 500),
                "source_count": int(raw.get("source_count", 0)),
                "sources": evidence["sources"],
            }
            if verdict["source_count"] <= 0:
                verdict["is_approved"] = False
            return json.dumps(verdict, sort_keys=True)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                proposed = json.loads(leader_result.calldata)
                if not valid_verdict(proposed):
                    return False
                observed = self._fetch_web_evidence(ttl, cnt)
                proposed_titles = []
                for source in proposed.get("sources", []):
                    proposed_titles.append(source.get("title", ""))
                observed_titles = []
                for source in observed.get("sources", []):
                    observed_titles.append(source.get("title", ""))
                return proposed_titles == observed_titles
            except Exception:
                return False

        return json.loads(gl.vm.run_nondet_unsafe(leader_fn, validator_fn))

    @gl.public.write
    def submit_fact(self, category: str, title: str, content: str) -> dict:
        verdict = self._verify_with_consensus(category, title, content)
        self.submissions_count += u256(1)
        self.last_verdict = json.dumps(verdict, sort_keys=True)

        if verdict["is_approved"]:
            sources = verdict.get("sources", [])
            first_source = ""
            if len(sources) > 0:
                first_source = sources[0].get("url", "")
            entry = (
                str(gl.message.sender_address)
                + "|"
                + clean_text(category, 40)
                + "|"
                + clean_text(title, 120)
                + "|"
                + clean_text(content, 1200)
                + "|"
                + clean_text(verdict["reasoning"], 500)
                + "|"
                + first_source
            )
            self.verified_ledger.append(entry)
            self.approved_count += u256(1)

        return verdict
