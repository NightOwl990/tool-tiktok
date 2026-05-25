from creator_rewards import infer_content_pillar, risk_level, score_monetization_risk


def clean_text(value, fallback="this topic"):
    value = " ".join(str(value or "").split())
    return value or fallback


def short_text(value, limit=96):
    value = clean_text(value)
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def detect_format(keyword, title, platform, category):
    text = f"{keyword} {title} {platform} {category}".lower()

    if any(x in text for x in ["aita", "relationship", "date", "girlfriend", "boyfriend", "wife", "husband"]):
        return "US Reddit story / relationship debate"
    if any(x in text for x in ["ai", "chatgpt", "tool", "app", "tech"]):
        return "AI tool explainer"
    if any(x in text for x in ["scary", "horror", "creepy", "nosleep"]):
        return "Horror storytelling"
    if any(x in text for x in ["money", "job", "salary", "business", "side hustle", "boss", "career"]):
        return "Work and money explainer"
    if any(x in text for x in ["meme", "funny", "viral"]):
        return "Trend recap"
    return "Story explainer"


def title_options(item, pillar):
    title = short_text(item.title or item.keyword, 82)

    if pillar == "AI tools":
        return [
            f"I tested the {short_text(item.keyword, 44)} trend",
            f"What {short_text(item.keyword, 44)} actually does",
            f"Is {short_text(item.keyword, 44)} useful or hype?",
        ]
    if pillar == "Workplace":
        return [
            "My boss made one mistake that changed everything",
            f"This workplace story has TikTok split: {title}",
            "The job drama people cannot agree on",
        ]
    if pillar == "Money":
        return [
            f"The money lesson inside this trend: {title}",
            "This sounds like bad advice until you hear the context",
            "The personal finance debate people keep missing",
        ]
    if pillar == "Relationship drama":
        return [
            f"Was this a boundary or a betrayal?",
            f"This relationship post has everyone choosing sides",
            f"The detail that changed this entire story",
        ]
    if pillar == "Horror story":
        return [
            "The moment this story stops feeling normal",
            f"This creepy story gets worse after one detail",
            "I would have left after this happened",
        ]
    return [
        f"Why this trend is taking off: {title}",
        f"The part of this story people are missing",
        f"This sounds simple until you hear the context",
    ]


def build_hook(item, pillar):
    title = short_text(item.title or item.keyword, 88)

    if pillar == "AI tools":
        return f"I looked into the {short_text(item.keyword, 50)} trend, and the useful part is not what people are posting."
    if pillar == "Workplace":
        return f"A workplace story is blowing up because one decision made everyone pick a side: {title}"
    if pillar == "Money":
        return f"This money conversation sounds simple at first, but one detail changes the whole takeaway: {title}"
    if pillar == "Relationship drama":
        return f"A relationship post has people split between calling it a boundary and calling it a betrayal: {title}"
    if pillar == "Horror story":
        return f"This story starts like a normal night, and then one detail makes it impossible to ignore: {title}"
    return f"This topic is starting to trend because the comments cannot agree on the real issue: {title}"


def hook_variants_for(item, pillar):
    title = short_text(item.title or item.keyword, 76)
    keyword = short_text(item.keyword or item.title, 48)

    variants = {
        "Curiosity": f"The weirdest part of {keyword} is not the part everyone is talking about.",
        "Conflict": f"People are split on this because both sides think they are obviously right: {title}",
        "Search": f"Here is what {keyword} means, why it is trending, and what most videos leave out.",
        "POV": f"If this happened to you, I do not think the answer would be as obvious as the comments make it sound.",
        "Comment bait": f"I need to know which side you are on after hearing the last detail.",
    }

    if pillar == "AI tools":
        variants.update({
            "Curiosity": f"I tested {keyword}, and the demo is less important than the workflow.",
            "Conflict": f"Some people think {keyword} is a shortcut, but the real question is whether it saves judgment.",
            "Search": f"What is {keyword}, who is it for, and is it actually useful?",
            "POV": f"I would only use {keyword} for one specific part of the workflow.",
        })
    elif pillar == "Money":
        variants.update({
            "Curiosity": f"The money lesson in this story is hidden in one small tradeoff.",
            "Conflict": f"One side calls this smart money management. The other side calls it a huge risk.",
            "Search": f"Before you copy this money move, here is the context that changes it.",
            "POV": f"I would not treat this as advice, but it is a useful decision breakdown.",
        })
    elif pillar == "Horror story":
        variants.update({
            "Curiosity": f"This story gets disturbing because of one detail that sounds normal at first.",
            "Conflict": f"Some people would leave immediately. Others say they would check one more thing.",
            "Search": f"Here is why this story works: it delays the answer just long enough.",
            "POV": f"I would have left the second this detail showed up.",
        })

    return variants


def script_angle_for(pillar):
    if pillar == "AI tools":
        return "Open with the result, show the exact use case, then explain who should and should not use it."
    if pillar == "Workplace":
        return "Frame the conflict as a workplace decision, reveal the missing context, then ask viewers what they would do."
    if pillar == "Money":
        return "Turn the trend into a practical lesson with caveats, examples, and no guaranteed-outcome claims."
    if pillar == "Relationship drama":
        return "Retell the situation in three beats: setup, boundary violation, and the detail that makes comments split."
    if pillar == "Horror story":
        return "Use slow pacing, sensory detail, and a delayed reveal without graphic detail."
    return "Use explain/story recap format with a new piece of context every 6-8 seconds."


def beat_sheet_for(item, pillar):
    topic = short_text(item.title or item.keyword, 110)

    if pillar == "AI tools":
        return [
            "0-3s: Show the output or result first.",
            f"3-12s: Name the trend: {topic}",
            "12-25s: Explain the real use case in plain English.",
            "25-45s: Show two practical examples or prompts.",
            "45-65s: Mention the limitation most videos skip.",
            "65-80s: Give a clear recommendation and who it is for.",
        ]
    if pillar in {"Workplace", "Relationship drama"}:
        return [
            "0-3s: State the conflict as a yes/no choice.",
            f"3-15s: Set up the situation: {topic}",
            "15-30s: Add the first detail that makes one side look right.",
            "30-48s: Reveal the detail that flips the debate.",
            "48-68s: Explain why comments are split.",
            "68-85s: Ask viewers what they would do before giving your take.",
        ]
    if pillar == "Money":
        return [
            "0-3s: Lead with the practical lesson or surprising cost.",
            f"3-15s: Set up the trend: {topic}",
            "15-35s: Explain the mistake or tradeoff.",
            "35-55s: Give a realistic example with numbers only if sourced.",
            "55-75s: Add caveats and avoid one-size-fits-all advice.",
            "75-90s: End with a question about the viewer's situation.",
        ]
    if pillar == "Horror story":
        return [
            "0-4s: Open on the unsettling detail.",
            f"4-18s: Ground the scene: {topic}",
            "18-38s: Add one strange event, then pause.",
            "38-58s: Reveal the detail that makes the story feel wrong.",
            "58-78s: End on the question or unresolved implication.",
        ]
    return [
        "0-3s: Start with the tension or question.",
        f"3-15s: Set up the context: {topic}",
        "15-35s: Explain why people care.",
        "35-58s: Add the missing context or twist.",
        "58-80s: Give your takeaway and ask for comments.",
    ]


def voiceover_for(item, pillar, hook):
    title = clean_text(item.title or item.keyword)
    source = "Reddit" if item.platform == "reddit" else "TikTok"

    if pillar == "AI tools":
        return f"""
{hook}

Here is the actual use case. The trend is about {clean_text(item.keyword)}, but most posts only show the flashy result.

The useful question is: does this save time, make better output, or just create another thing to check?

For a real workflow, I would test it on one narrow task first, compare the result to doing it manually, and only keep it if it removes a repeated step.

The limitation is that tools like this can look impressive in a demo but fail when the prompt, source material, or goal changes.

So the takeaway is simple: use it for drafts, structure, and speed, but do not treat the first output as finished work.
""".strip()

    if pillar in {"Workplace", "Relationship drama"}:
        return f"""
{hook}

The {source} post is about this situation: {title}

At first, one side looks obvious. Someone makes a decision, someone else reacts, and the comments start treating it like a simple right-or-wrong story.

But the reason this works as a video is the missing context. The real question is not just what happened. It is whether the reaction was proportionate.

One side sees a boundary. The other side sees an overreaction. And that is why this kind of story keeps people watching: every new detail changes who seems reasonable.

My take is that the strongest version of this video should not copy the post word for word. Retell it, add your own framing, and ask viewers what they would have done before giving your opinion.
""".strip()

    if pillar == "Money":
        return f"""
{hook}

The trend is about {title}

The important part is the tradeoff. Money topics usually go viral when they sound like there is one obvious answer, but real life has constraints: income, timing, risk, and personal responsibility.

So instead of turning this into advice, frame it as a decision breakdown. What was the person optimizing for? What did they give up? And what would make the choice smarter or riskier?

That keeps the video useful without promising results. It also makes the comments better, because people can compare the decision to their own situation.
""".strip()

    if pillar == "Horror story":
        return f"""
{hook}

The story is built around this premise: {title}

Do not rush it. Start normal, keep the details specific, and let the audience notice that something is off before you explain it.

The retention point is the delayed reveal. Every few seconds, add one detail that makes the previous detail feel worse.

Keep it atmospheric, not graphic. The goal is suspense, not shock.
""".strip()

    return f"""
{hook}

The trend is about {title}

The reason it is getting attention is not just the topic. It is the disagreement underneath it.

First, explain the context in one sentence. Then give the strongest argument for one side, the strongest argument for the other side, and the detail that makes the story worth debating.

End by asking viewers which side they are on. That gives the video a reason to continue in the comments instead of ending when the recap ends.
""".strip()


def onscreen_text_for(item, pillar):
    keyword = short_text(item.keyword or item.title, 42)

    if pillar == "AI tools":
        return [
            f"Testing: {keyword}",
            "Useful or hype?",
            "The limitation nobody mentions",
            "Would you use this?",
        ]
    if pillar == "Money":
        return [
            "The money tradeoff",
            "What they optimized for",
            "The risk people skip",
            "Smart move or mistake?",
        ]
    if pillar == "Workplace":
        return [
            "Workplace drama",
            "One decision changed everything",
            "Was this fair?",
            "What would you do?",
        ]
    if pillar == "Relationship drama":
        return [
            "Boundary or betrayal?",
            "The detail that split comments",
            "Who is wrong here?",
            "What would you do?",
        ]
    if pillar == "Horror story":
        return [
            "This started normal",
            "Then one detail changed it",
            "Listen closely",
            "Would you stay?",
        ]
    return [
        f"Trending: {keyword}",
        "The missing context",
        "Why comments are split",
        "Pick a side",
    ]


def broll_for(pillar):
    if pillar == "AI tools":
        return "Screen recording, prompt/result comparison, cursor closeups, simple before-after captions."
    if pillar == "Money":
        return "Calculator, notes app, spreadsheet, bills, generic city/work desk shots; avoid showing private data."
    if pillar == "Workplace":
        return "Office desk, email inbox mockup, calendar, commute, coffee, neutral workplace B-roll."
    if pillar == "Relationship drama":
        return "Text-message mockups, neutral apartment shots, wedding/relationship stock-style B-roll, no real private photos."
    if pillar == "Horror story":
        return "Dark hallway, door handle, phone flashlight, rainy window, slow zooms; keep it non-graphic."
    return "Relevant screenshots you own, simple captions, neutral B-roll, and one visual reset every 5-7 seconds."


def hashtags_for(item, pillar):
    tags = ["#storytime", "#viral", "#tiktokcreator"]

    if item.platform == "reddit":
        tags.append("#redditstories")
    if pillar == "AI tools":
        tags.extend(["#aitools", "#chatgpt", "#productivity"])
    elif pillar == "Money":
        tags.extend(["#moneytok", "#careertok", "#personalfinance"])
    elif pillar == "Workplace":
        tags.extend(["#worktok", "#careertok", "#jobstory"])
    elif pillar == "Relationship drama":
        tags.extend(["#relationshiptok", "#aita", "#redditdrama"])
    elif pillar == "Horror story":
        tags.extend(["#scarystory", "#horrortok"])
    else:
        tags.extend(["#explained", "#storytelling"])

    return " ".join(dict.fromkeys(tags[:9]))


def safety_notes_for(item, pillar):
    risk = score_monetization_risk(item)
    level = risk_level(risk)
    notes = [
        "Transform the source with original commentary and structure.",
        "Use licensed, original, or self-created visuals.",
        "Avoid reading Reddit/TikTok text verbatim for the full video.",
    ]

    if level != "Low":
        notes.append("Remove graphic, sexual, illegal, or advice-like claims before posting.")
    if pillar == "Money":
        notes.append("Use disclaimers and avoid guaranteed financial outcomes.")

    return f"{level} risk. " + " ".join(notes)


def generate_idea(item):
    keyword = clean_text(item.keyword or item.title)
    title = clean_text(item.title or keyword)
    pillar = item.content_pillar or infer_content_pillar(item)
    fmt = detect_format(keyword, title, item.platform, item.category)
    hook = build_hook(item, pillar)
    beat_sheet = beat_sheet_for(item, pillar)
    voiceover_script = voiceover_for(item, pillar, hook)

    caption = "Which side are you on? Full context in the video."
    if pillar == "AI tools":
        caption = "Would this actually save you time, or is it just hype?"
    elif pillar == "Money":
        caption = "Smart move or risky tradeoff? It depends on the context."
    elif pillar == "Horror story":
        caption = "Would you have stayed after this detail?"

    return {
        "format": fmt,
        "content_pillar": pillar,
        "target_duration": "60-90 seconds",
        "hook": hook,
        "hook_variants": hook_variants_for(item, pillar),
        "title_options": title_options(item, pillar),
        "script_angle": script_angle_for(pillar),
        "beat_sheet": "\n".join(beat_sheet),
        "voiceover_script": voiceover_script,
        "onscreen_text": "\n".join(onscreen_text_for(item, pillar)),
        "broll_plan": broll_for(pillar),
        "caption": caption,
        "hashtags": hashtags_for(item, pillar),
        "safety_notes": safety_notes_for(item, pillar),
    }
