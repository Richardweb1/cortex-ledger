# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""CortexLedger: simple GenLayer web-backed fact verification contract."""

from genlayer import *
import json


WIKIPEDIA_SEARCH = "https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=3&srsearch="
ALLOWED_CATEGORIES = ("Technology", "Science")


def clean_text(value: str, max_len: int) -> str:
    return " ".join(str(value).strip().split())[:max_len]


def encode_query(value: str) -> str:
    return clean_text(value, 160).replace(" ", "%20").replace('"', "%22")


def sentence_count(value: str) -> int:
    total = 0
    for char in value:
        if char in ".!?":
            total += 1
    return total


def is_plain_english(value: str) -> bool:
    if len(value.strip()) == 0:
        return False
    for char in value:
        if ord(char) > 127:
            return False
    return True


def has_political_terms(value: str) -> bool:
    lowered = value.lower()
    blocked = (
        "president",
        "election",
        "politician",
        "political party",
        "senator",
        "parliament",
        "congress",
        "government policy",
    )
    for term in blocked:
        if term in lowered:
            return True
    return False


def valid_result(result: object) -> bool:
    if not isinstance(result, dict):
        return False
    return (
        isinstance(result.get("approved"), bool)
        and isinstance(result.get("category"), str)
        and isinstance(result.get("title"), str)
        and isinstance(result.get("content"), str)
        and isinstance(result.get("reasoning"), str)
        and isinstance(result.get("source_title"), str)
        and isinstance(result.get("source_url"), str)
        and isinstance(result.get("source_count"), int)
        and 0 <= result.get("source_count") <= 3
        and 1 <= len(result.get("reasoning").strip()) <= 500
    )


class CortexLedger(gl.Contract):
    last_entry: str
    last_verdict: str
    submissions_count: u256
    approved_count: u256

    def __init__(self):
        self.last_entry = ""
        self.last_verdict = "No verification has been finalized yet."
        self.submissions_count = u256(0)
        self.approved_count = u256(0)

    def _fetch_evidence(self, title: str, content: str) -> dict:
        query = encode_query(title + " " + content[:100])
        response = gl.nondet.web.get(WIKIPEDIA_SEARCH + query)
        payload = json.loads(response.body.decode("utf-8"))
        results = payload.get("query", {}).get("search", [])
        first = {}
        if len(results) > 0:
            item = results[0]
            first = {
                "title": clean_text(item.get("title", ""), 120),
                "url": "https://en.wikipedia.org/?curid=" + str(int(item.get("pageid", 0))),
                "snippet": clean_text(item.get("snippet", ""), 300),
            }
        return {
            "query": query,
            "source_count": len(results[:3]),
            "first_source": first,
        }

    def _verify(self, category: str, title: str, content: str) -> dict:
        cat = clean_text(category, 40)
        ttl = clean_text(title, 120)
        cnt = clean_text(content, 1000)

        def leader_fn() -> str:
            evidence = self._fetch_evidence(ttl, cnt)
            source = evidence["first_source"]
            approved = True
            reason = "Approved with live web evidence fetched during GenLayer execution."

            if cat not in ALLOWED_CATEGORIES:
                approved = False
                reason = "Rejected: only Technology and Science categories are accepted."
            elif not is_plain_english(ttl + " " + cnt):
                approved = False
                reason = "Rejected: only plain English content is accepted."
            elif has_political_terms(ttl + " " + cnt):
                approved = False
                reason = "Rejected: political topics are outside this ledger scope."
            elif len(cnt) < 50 or sentence_count(cnt) < 2:
                approved = False
                reason = "Rejected: content must contain at least two specific sentences."
            elif evidence["source_count"] <= 0:
                approved = False
                reason = "Rejected: no live web evidence was found for this claim."
            else:
                prompt = f"""You are a GenLayer fact-verification validator.
Use ONLY this live web evidence to judge whether the claim is reasonably supported.

Claim title: {ttl}
Claim content: {cnt}
Source title: {source.get("title", "")}
Source snippet: {source.get("snippet", "")}

Return ONLY JSON: {{"approved": true_or_false, "reasoning": "max 300 chars"}}"""
                raw = gl.nondet.exec_prompt(prompt, response_format="json")
                if not isinstance(raw, dict):
                    raw = json.loads(str(raw))
                approved = bool(raw.get("approved", False))
                reason = clean_text(raw.get("reasoning", reason), 300)

            result = {
                "approved": approved,
                "category": cat,
                "title": ttl,
                "content": cnt,
                "reasoning": reason,
                "source_count": int(evidence["source_count"]),
                "source_title": clean_text(source.get("title", ""), 120),
                "source_url": clean_text(source.get("url", ""), 160),
            }
            return json.dumps(result, sort_keys=True)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                proposed = json.loads(leader_result.calldata)
                if not valid_result(proposed):
                    return False
                observed = self._fetch_evidence(ttl, cnt)
                source = observed["first_source"]
                return (
                    proposed["source_count"] == int(observed["source_count"])
                    and proposed["source_title"] == clean_text(source.get("title", ""), 120)
                )
            except Exception:
                return False

        return json.loads(gl.vm.run_nondet_unsafe(leader_fn, validator_fn))

    @gl.public.write
    def submit_fact(self, category: str, title: str, content: str) -> dict:
        result = self._verify(category, title, content)
        self.submissions_count += u256(1)
        self.last_verdict = json.dumps(result, sort_keys=True)

        if result["approved"]:
            self.last_entry = (
                str(gl.message.sender_address)
                + "|"
                + result["category"]
                + "|"
                + result["title"]
                + "|"
                + result["content"]
                + "|"
                + result["reasoning"]
                + "|"
                + result["source_url"]
            )
            self.approved_count += u256(1)

        return result

    @gl.public.view
    def get_verified_ledger(self) -> list:
        if self.last_entry == "":
            return []
        return [self.last_entry]

    @gl.public.view
    def get_last_verdict(self) -> str:
        return self.last_verdict
