SESSIONS = [
    {
        "name": "Session PLN - integration smoke",
        "queries": [
            "Search for recent technical discussions plus formal papers on EBM stability for geometric tasks.",
            "Based on what was just collected, what is the most likely key takeaway?",
            "Reason through the takeaway one more time and give one caveat.",
        ],
        "expected_actions": [
            "act_search",
            "act_think",
            "act_think",
        ],
        "acceptable_actions": [
            ["act_synthesize"],
            [],
            ["act_verify"],
        ],
    }
]
