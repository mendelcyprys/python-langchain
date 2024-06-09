
# Note the system and user templates are almost identical
# Changes made to one might have to be made to the other
# Ideally the identical parts should be put into separate variables to avoid that

summary_system_template = """
Your task is to generate increasingly concise, entity-dense summaries of a research paper.
You will repeat the following 2 steps 5 times.
Step 1. Identify 1-3 informative Entities (";" delimited) from the article which are missing from the previously generated summary, and which should be included in a high-level summary.
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary, but which also includes the Missing Entities identified above.
        The summary should be 6 to 8 sentences, about 120 words.
A Missing Entity is:
- relevant to the research paper, and relevant to being included in a high-level summary
- specific yet concise (5 words or fewer),
- novel (not in the previous summary),
- faithful (present in the article),
- anywhere (can be located anywhere in the article).
A Missing Entity is not an email, or something about FIGURE X, or a name.
It must be relevant to the paper and relevant to being part of a high-level summary.

Guidelines:
- The first summary should be long (6 to 8 sentences, about 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.
  Use overly verbose language and fillers (e.g., "this article discusses") to reach approximately 120 words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
- Make sure the text is clear of HTML Character Entities (avoid for example &quot; or &#x27), and UTF-8 representations (like \\u2019s).

Remember, use exactly the same number of words for each summary.

Answer in JSON. The JSON object should have an entry "summaryList", which should be a list (length 5) of dictionaries whose keys are "missingEntities" and "denserSummary".
The JSON object should also contain the following keys:
- "title": This should be the title of the article, without any changes. Only fix obvious formating mistakes, like extra spaces. Double check to make sure that the title is correct and does not include bits that are not part of the title.
- "authors": A list containing the names of the authors of the aritcle.
- "slug": A slug URL for a webpage fitting for this article (lowercase, dashes instead of spaces).
- "introduction": A 1-2 sentence summary of the article, 20-40 words long (not the same length as a summary).
- "publicationDate": The publication date of the article in the format "DD-MM-YYYY". If only the year is available then in the format "YYYY". If no date information is available, this should be null.
- "keywords": A list of the 5 most revelant keywords relating to the article.
- "link": The link to the DOI, and if not available, to the journal. If link not available, should be null.

The JSON should look like this:
{{
    summaryList: [
        {{
            missingEntities: "...",
            denserSummary: "..."
        }},
        ...
    ],
    title: "...",
    authors: ["...", ...],
    slug: "...",
    introduction: "...",
    publicationDate: "...",
    keywords: ["...", ...],
    link: "..."
}}

Write only valid JSON. Remember that summaryList should be a list of length 5.
"""

summary_user_template = """
<Article>
{text}
</Article>

You will generate increasingly concise, entity-dense summaries of the above research paper.
Repeat the following 2 steps 5 times.
Step 1. Identify 1-3 informative Entities (";" delimited) from the article which are missing from the previously generated summary, which should be included in a high-level summary.
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary, but which also includes the Missing Entities identified above.
        The summary should be 6 to 8 sentences, about 120 words.
A Missing Entity is:
- relevant to the research paper, and relevant to being included in a high-level summary
- specific yet concise (5 words or fewer),
- novel (not in the previous summary),
- faithful (present in the article),
- anywhere (can be located anywhere in the article).
A Missing Entity is not an email, or something about FIGURE X, or a name.
It must be relevant to the paper and relevant to being part of a high-level summary.

Guidelines:
- The first summary should be long (6 to 8 sentences, about 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.
  Use overly verbose language and fillers (e.g., "this article discusses") to reach approximately 120 words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
- Make sure the text is clear of HTML Character Entities (avoid for example &quot; or &#x27), and UTF-8 representations (like \\u2019s).

Remember, use exactly the same number of words for each summary.

Answer in JSON. The JSON object should have an entry "summaryList", which should be a list (length 5) of dictionaries whose keys are "missingEntities" and "denserSummary".
The JSON object should also contain the following keys:
- "title": This should be the title of the article, without any changes. Only fix obvious formating mistakes, like extra spaces. Double check to make sure that the title is correct and does not include bits that are not part of the title.
- "authors": A list containing the names of the authors of the aritcle.
- "slug": A slug URL for a webpage fitting for this article (lowercase, dashes instead of spaces).
- "introduction": A 1-2 sentence summary of the article, 20-40 words long (not the same length as a summary).
- "publicationDate": The publication date of the article in the format "DD-MM-YYYY". If only the year is available then in the format "YYYY". If no date information is available, this should be null.
- "keywords": A list of the 5 most revelant keywords relating to the article.
- "link": The link to the DOI, and if not available, to the journal. If link not available, should be null.

The JSON should look like this:
{{
    summaryList: [
        {{
            missingEntities: "...",
            denserSummary: "..."
        }},
        ...
    ],
    title: "...",
    authors: ["...", ...],
    slug: "...",
    introduction: "...",
    publicationDate: "...",
    keywords: ["...", ...],
    link: "..."
}}

Write only valid JSON. Remember that summaryList should be a list of length 5.
"""