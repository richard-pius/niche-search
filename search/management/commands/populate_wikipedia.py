import time
import wikipediaapi
from django.core.management.base import BaseCommand
from search.models import SearchResult

CATEGORIES = [
    "Technology", "History", "Science", "Geography", "Philosophy",
    "Mathematics", "Computing", "Culture", "Health", "Music",
    "Business", "Politics", "Literature", "Art", "Biology",
    "Physics", "Chemistry", "Engineering", "Education", "Sports",
    "Food", "Environment", "Religion", "Language", "Archaeology",
]

TOTAL_ARTICLES_TARGET = 1500
REQUEST_DELAY = 0.3        # seconds between API calls (be polite!)
MAX_RETRIES = 3             # retry up to 3 times on failure

class Command(BaseCommand):
    help = 'Populate database with ~1500 Wikipedia summaries (with retry & backoff)'

    def handle(self, *args, **options):
        wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='NicheSearchCapstone/1.0 (your-email@example.com)'  # CHANGE THIS TO YOUR EMAIL
        )

        total_added = 0

        for category_name in CATEGORIES:
            cat = wiki.page(f"Category:{category_name}")
            if not cat.exists():
                self.stdout.write(self.style.WARNING(f"Category not found: {category_name}"))
                continue

            articles = self.get_articles_recursive(cat, wiki, depth=1, limit_per_category=60)

            for url, (title, link, summary) in articles.items():
                if total_added >= TOTAL_ARTICLES_TARGET:
                    break
                obj, created = SearchResult.objects.get_or_create(
                    url=link,
                    defaults={
                        'title': title,
                        'description': summary[:500],
                        'source_site': 'Wikipedia',
                    }
                )
                if created:
                    self.stdout.write(f"Added: {title}")
                    total_added += 1
                else:
                    self.stdout.write(f"Skipped (exists): {title}")

            self.stdout.write(
                self.style.SUCCESS(
                    f"--- Finished category '{category_name}' ({total_added} total so far) ---"
                )
            )
            if total_added >= TOTAL_ARTICLES_TARGET:
                break

        self.stdout.write(self.style.SUCCESS(f"Total new articles added: {total_added}"))

    # ------------------------------------------------------------------
    #  Retry helper – tries to fetch a page attribute several times
    # ------------------------------------------------------------------
    def _safe_get_page_attr(self, page, attr_name):
        """
        Return getattr(page, attr_name) with retry & exponential backoff.
        If all retries fail, returns a safe default (empty string or False).
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                time.sleep(REQUEST_DELAY)            # always pause between requests
                value = getattr(page, attr_name)
                # If the value is callable (e.g., exists()), call it
                if callable(value):
                    return value()
                return value
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Attempt {attempt}/{MAX_RETRIES} failed for '{page.title}' "
                        f"({attr_name}): {e}"
                    )
                )
                if attempt < MAX_RETRIES:
                    backoff = 2 ** attempt          # 2, 4, 8 seconds
                    time.sleep(backoff)
        # All retries exhausted → return a safe fallback
        if attr_name == "exists":
            return False
        return ""

    # ------------------------------------------------------------------
    #  Recursive article collector (unchanged logic, but uses the safe
    #  helper for page.exists() and page.summary)
    # ------------------------------------------------------------------
    def get_articles_recursive(self, category_page, wiki, depth=0, limit_per_category=60):
        collected = {}

        for member in category_page.categorymembers.values():
            if member.ns == 0:                     # real article
                page = wiki.page(member.title)

                # Use safe helper for exists and summary
                exists = self._safe_get_page_attr(page, "exists")
                if not exists:
                    continue

                summary = self._safe_get_page_attr(page, "summary")
                if summary:
                    collected[page.fullurl] = (page.title, page.fullurl, summary)

            if len(collected) >= limit_per_category:
                break

        if depth > 0:
            subcats = [m for m in category_page.categorymembers.values() if m.ns == 14]
            for subcat in subcats[:3]:
                subcat_page = wiki.page(subcat.title)
                sub_exists = self._safe_get_page_attr(subcat_page, "exists")
                if sub_exists:
                    sub_articles_dict = self.get_articles_recursive(
                        subcat_page, wiki, depth=depth - 1,
                        limit_per_category=limit_per_category // 2
                    )
                    for url, (title, link, summary) in sub_articles_dict.items():
                        if url not in collected:
                            collected[url] = (title, link, summary)
                            if len(collected) >= limit_per_category:
                                break
                if len(collected) >= limit_per_category:
                    break

        return collected