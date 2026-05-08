# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import typing

class CortexLedger(gl.Contract):
    verified_ledger: DynArray[str]

    def __init__(self):
        pass

    @gl.public.view
    def get_verified_ledger(self) -> list:
        return list(self.verified_ledger)

    @gl.public.write
    def submit_fact(
        self,
        category: str,
        title: str,
        content: str
    ) -> None:
        cat = category
        ttl = title
        cnt = content

        def get_verdict() -> str:
            task = f"""You are a strict fact-checking judge for the Cortex Ledger platform.
Your role is to verify submitted facts in Technology and Science ONLY.

Submitted fact:
Category: {cat}
Title: {ttl}
Content: {cnt}

Apply these rules in order:

RULE 1 - ENGLISH ONLY:
If content is not in English return:
{{"is_approved": false, "reasoning": "Content rejected: Only English content is accepted."}}

RULE 2 - NO POLITICS:
If content mentions politics, politicians, elections, or government policies return:
{{"is_approved": false, "reasoning": "Content rejected: Political topics are out of scope."}}

RULE 3 - ALLOWED CATEGORIES ONLY:
Only Technology and Science are allowed.
If category is anything else return:
{{"is_approved": false, "reasoning": "Content rejected: Category not allowed. Only Technology and Science are accepted."}}

RULE 4 - FACT QUALITY:
Content must be:
- A real verifiable fact
- At least 2 sentences
- Specific and accurate
- Not misleading

If content passes ALL rules return:
{{"is_approved": true, "reasoning": "Content verified and approved."}}

Respond ONLY with this JSON format:
{{
    "is_approved": bool,
    "reasoning": str
}}
Nothing else. No extra words. No markdown. Pure JSON only."""
            result = (
                gl.nondet.exec_prompt(task)
                .replace("```json", "")
                .replace("```", "")
            )
            print(result)
            return result

        result = gl.eq_principle.prompt_comparative(
            get_verdict,
            "The value of is_approved must match"
        )
        parsed = json.loads(result)

        if parsed["is_approved"]:
            entry = f"{str(gl.message.sender_address)}|{cat}|{ttl}|{cnt}"
            self.verified_ledger.append(entry)