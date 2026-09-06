import feedparser
import json
import re
import html
import hashlib

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


# ============================================================
# CONFIGURATION
# ============================================================

SOURCES_FILE = "sources.json"
JSON_FILE = "news.json"


# ============================================================
# CHARGER LES SOURCES
# ============================================================

def load_sources():
    """
    Charge les sources RSS depuis sources.json.
    """

    try:
        with open(
            SOURCES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        sources = data.get("sources", [])

        if not sources:
            print("ERREUR : aucune source trouvée dans sources.json")
            return []

        print(f"✓ {len(sources)} sources chargées depuis {SOURCES_FILE}")

        return sources

    except FileNotFoundError:

        print(f"ERREUR : le fichier {SOURCES_FILE} est introuvable.")

        return []

    except json.JSONDecodeError as error:

        print(
            f"ERREUR : {SOURCES_FILE} contient un JSON invalide."
        )

        print(error)

        return []


# ============================================================
# NETTOYAGE HTML
# ============================================================

def clean_html(text):

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)

    text = html.unescape(text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# ID UNIQUE
# ============================================================

def generate_id(url):

    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()


# ============================================================
# DATE
# ============================================================

def parse_date(entry):

    date_string = entry.get(
        "published",
        entry.get("updated", "")
    )

    if not date_string:
        return None

    try:

        date = parsedate_to_datetime(
            date_string
        )

        if date.tzinfo is None:
            date = date.replace(
                tzinfo=timezone.utc
            )

        return date.astimezone(
            timezone.utc
        ).isoformat()

    except Exception:

        return None


# ============================================================
# TAGS
# ============================================================

TAG_KEYWORDS = {

    "python": ["python"],
    "javascript": ["javascript", "node.js", "nodejs"],
    "typescript": ["typescript"],
    "php": ["php"],
    "java": ["java"],
    "csharp": ["c#", ".net", "c sharp"],
    "rust": ["rust"],
    "go": ["golang", "go language"],
    "cpp": ["c++"],

    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git", "github", "gitlab"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],

    "linux": ["linux", "ubuntu", "debian", "fedora", "arch linux"],
    "windows": ["windows"],
    "macos": ["macos", "mac os"],

    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "google_cloud": ["google cloud", "gcp"],

    "nvidia": ["nvidia", "geforce", "rtx"],
    "amd": ["amd", "ryzen", "radeon"],
    "intel": ["intel", "core ultra"],
    "qualcomm": ["qualcomm", "snapdragon"],

    "cve": ["cve-"],
    "ransomware": ["ransomware"],
    "malware": ["malware", "trojan"],
    "phishing": ["phishing"],
    "zero_day": ["zero-day", "zero day"],

    "openai": ["openai", "chatgpt"],
    "gemini": ["gemini", "google ai"],
    "anthropic": ["anthropic", "claude"],
    "llm": ["llm", "large language model"],
    "machine_learning": ["machine learning"],
    "deep_learning": ["deep learning"],

    "android": ["android"],
    "ios": ["ios", "iphone", "ipad"],

    "wifi": ["wifi", "wi-fi"],
    "5g": ["5g"],
    "bluetooth": ["bluetooth"],

    "rgpd": ["rgpd", "gdpr"],
    "ai_act": ["ai act"],

    "blockchain": ["blockchain"],
    "bitcoin": ["bitcoin"],
    "ethereum": ["ethereum"]
}


def detect_tags(title, description, source_tags):

    text = f"{title} {description}".lower()

    tags = set(source_tags)

    for tag, keywords in TAG_KEYWORDS.items():

        for keyword in keywords:

            if keyword.lower() in text:

                tags.add(tag)

                break

    return sorted(tags)


# ============================================================
# CATÉGORIE
# ============================================================

def detect_category(
    title,
    description,
    default_category
):

    text = f"{title} {description}".lower()


    cyber_keywords = [
        "cve-",
        "vulnerability",
        "vulnérabilité",
        "ransomware",
        "malware",
        "phishing",
        "cyberattack",
        "cyberattaque",
        "security breach",
        "exploit"
    ]

    if any(
        keyword in text
        for keyword in cyber_keywords
    ):
        return "cybersecurite"


    ai_keywords = [
        "artificial intelligence",
        "intelligence artificielle",
        "machine learning",
        "deep learning",
        "large language model",
        "llm",
        "generative ai",
        "ia générative"
    ]

    if any(
        keyword in text
        for keyword in ai_keywords
    ):
        return "intelligence_artificielle"


    cloud_keywords = [
        "aws",
        "azure",
        "google cloud",
        "cloud computing",
        "cloud service"
    ]

    if any(
        keyword in text
        for keyword in cloud_keywords
    ):
        return "cloud"


    hardware_keywords = [
        "cpu",
        "gpu",
        "processor",
        "processeur",
        "graphics card",
        "rtx",
        "ryzen",
        "radeon",
        "intel core"
    ]

    if any(
        keyword in text
        for keyword in hardware_keywords
    ):
        return "hardware"


    linux_keywords = [
        "linux",
        "ubuntu",
        "debian",
        "fedora",
        "arch linux"
    ]

    if any(
        keyword in text
        for keyword in linux_keywords
    ):
        return "linux"


    devops_keywords = [
        "docker",
        "kubernetes",
        "terraform",
        "ansible",
        "ci/cd",
        "continuous integration"
    ]

    if any(
        keyword in text
        for keyword in devops_keywords
    ):
        return "devops"


    web_keywords = [
        "javascript",
        "typescript",
        "css",
        "html",
        "frontend",
        "backend",
        "browser",
        "web development"
    ]

    if any(
        keyword in text
        for keyword in web_keywords
    ):
        return "web"


    return default_category


# ============================================================
# CHARGER LE JSON DES NEWS EXISTANTES
# ============================================================

def load_existing_news():

    try:

        with open(
            JSON_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data.get("articles", [])

    except FileNotFoundError:

        print(
            f"{JSON_FILE} inexistant → création."
        )

        return []

    except json.JSONDecodeError:

        print(
            f"ERREUR : {JSON_FILE} est invalide."
        )

        return []


# ============================================================
# TESTER UNE SOURCE
# ============================================================

def check_feed(source):

    try:

        feed = feedparser.parse(
            source["url"]
        )

        if feed.bozo and not feed.entries:

            return False, 0

        return True, len(feed.entries)

    except Exception:

        return False, 0


# ============================================================
# VÉRIFIER LES SOURCES
# ============================================================

def check_sources(sources):

    print()
    print("=" * 70)
    print("              VÉRIFICATION DES SOURCES")
    print("=" * 70)

    working_sources = []

    for source in sources:

        success, count = check_feed(
            source
        )

        if success:

            print(
                f"✓ {source['name']:<30}"
                f"{count:>4} articles"
            )

            working_sources.append(source)

        else:

            print(
                f"✗ {source['name']:<30}"
                f" ERREUR"
            )

    print("=" * 70)

    print(
        f"Sources fonctionnelles : "
        f"{len(working_sources)}/{len(sources)}"
    )

    return working_sources


# ============================================================
# RÉCUPÉRER LES NEWS
# ============================================================

def fetch_news(sources):

    articles = []

    print()
    print("=" * 70)
    print("                 RÉCUPÉRATION")
    print("=" * 70)

    for source in sources:

        print(
            f"\n→ {source['name']}"
        )

        try:

            feed = feedparser.parse(
                source["url"]
            )

            for entry in feed.entries:

                title = clean_html(
                    entry.get(
                        "title",
                        ""
                    )
                )

                url = entry.get(
                    "link",
                    ""
                ).strip()

                if not title or not url:
                    continue

                description = clean_html(
                    entry.get(
                        "summary",
                        entry.get(
                            "description",
                            ""
                        )
                    )
                )

                article_id = generate_id(
                    url
                )

                category = detect_category(
                    title,
                    description,
                    source.get(
                        "category",
                        "actualites_tech"
                    )
                )

                tags = detect_tags(
                    title,
                    description,
                    source.get(
                        "tags",
                        []
                    )
                )

                article = {

                    "id": article_id,

                    "title": title,

                    "description": description,

                    "url": url,

                    "source": source["name"],

                    "category": category,

                    "tags": tags,

                    "published_at": parse_date(
                        entry
                    ),

                    "collected_at":
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                }

                articles.append(article)

            print(
                f"  ✓ {len(feed.entries)} articles"
            )

        except Exception as error:

            print(
                f"  ✗ Erreur : {error}"
            )

    return articles


# ============================================================
# FUSION DES ARTICLES
# ============================================================

def merge_news(
    existing_articles,
    fetched_articles
):

    articles_by_id = {}

    # Anciennes news
    for article in existing_articles:

        if "id" in article:

            articles_by_id[
                article["id"]
            ] = article


    # Nouvelles news
    added = 0

    for article in fetched_articles:

        if article["id"] not in articles_by_id:

            articles_by_id[
                article["id"]
            ] = article

            added += 1


    articles = list(
        articles_by_id.values()
    )


    # Plus récent → plus ancien
    articles.sort(
        key=lambda article:
            article.get(
                "published_at"
            ) or "",
        reverse=True
    )


    print()
    print("=" * 70)
    print("                    RÉSULTAT")
    print("=" * 70)

    print(
        f"Articles récupérés : "
        f"{len(fetched_articles)}"
    )

    print(
        f"Nouveaux articles : "
        f"{added}"
    )

    print(
        f"Doublons ignorés : "
        f"{len(fetched_articles) - added}"
    )

    print(
        f"Total en base : "
        f"{len(articles)}"
    )

    print("=" * 70)

    return articles


# ============================================================
# SAUVEGARDER
# ============================================================

def save_news(articles):

    data = {

        "updated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "count":
            len(articles),

        "articles":
            articles
    }

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(
        f"\n✓ {JSON_FILE} sauvegardé."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("                    TECH WATCH")
    print("=" * 70)


    # 1. Charger sources.json
    sources = load_sources()

    if not sources:
        print("Aucune source à traiter.")
        return


    # 2. Vérifier les sources
    working_sources = check_sources(
        sources
    )

    if not working_sources:

        print(
            "Aucune source fonctionnelle."
        )

        return


    # 3. Charger les anciennes news
    existing_articles = (
        load_existing_news()
    )

    print(
        f"\nArticles déjà présents : "
        f"{len(existing_articles)}"
    )


    # 4. Récupérer les news
    fetched_articles = fetch_news(
        working_sources
    )


    # 5. Fusionner
    final_articles = merge_news(
        existing_articles,
        fetched_articles
    )


    # 6. Sauvegarder
    save_news(
        final_articles
    )


    print()
    print("=" * 70)
    print("                    TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()