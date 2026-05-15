import wikipediaapi
from django.core.management.base import BaseCommand
from search.models import SearchResult

# Broad list of top‑level categories (Wikipedia’s main topics)
CATEGORIES = [
    "Technology",
    "History",
    "Science",
    "Geography",
    "Philosophy",
    "Mathematics",
    "Computing",
    "Culture",
    "Health",
    "Music",
    "Business",
    "Politics",
    "Literature",
    "Art",
    "Biology",
    "Physics",
    "Chemistry",
    "Engineering",
    "Education",
    "Sports",
    "Food",
    "Environment",
    "Religion",
    "Language",
    "Archaeology",
]

TOTAL_ARTICLES_TARGET = 1500

class Command(BaseCommand):
    help = 'Populate database with ~1500 Wikipedia summaries from multiple categories'

    def handle(self, *args, **options):
        wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='NicheSearchCapstone/1.0 (your-email@example.com)'  # CHANGE THIS
        )

        total_added = 0

        for category_name in CATEGORIES:
            cat = wiki.page(f"Category:{category_name}")
            if not cat.exists():
                self.stdout.write(self.style.WARNING(f"Category not found: {category_name}"))
                continue

            # Fetch articles from the category and its immediate subcategories.
            # Returns a dict {url: (title, url, summary)}
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

            self.stdout.write(f"--- Finished category '{category_name}' ({total_added} total so far) ---")
            if total_added >= TOTAL_ARTICLES_TARGET:
                break

        self.stdout.write(self.style.SUCCESS(f"Total new articles added: {total_added}"))

    def get_articles_recursive(self, category_page, wiki, depth=0, limit_per_category=60):
        """
        Recursively collect articles from a category and its subcategories.
        Returns a dictionary {url: (title, url, summary)} to avoid duplicates.
        """
        collected = {}

        # Direct members of this category
        for member in category_page.categorymembers.values():
            if member.ns == 0:   # real article
                page = wiki.page(member.title)
                if page.exists() and page.summary:
                    collected[page.fullurl] = (page.title, page.fullurl, page.summary)
            if len(collected) >= limit_per_category:
                break

        # If depth > 0, also crawl subcategories
        if depth > 0:
            subcats = [m for m in category_page.categorymembers.values() if m.ns == 14]  # ns=14 = subcategory
            for subcat in subcats[:3]:   # limit to 3 subcats to avoid explosion
                subcat_page = wiki.page(subcat.title)
                if subcat_page.exists():
                    # Recursive call returns a dictionary
                    sub_articles_dict = self.get_articles_recursive(
                        subcat_page, wiki, depth=depth-1,
                        limit_per_category=limit_per_category // 2
                    )
                    # Merge the returned dict (skip duplicates)
                    for url, (title, link, summary) in sub_articles_dict.items():
                        if url not in collected:
                            collected[url] = (title, link, summary)
                            if len(collected) >= limit_per_category:
                                break
                if len(collected) >= limit_per_category:
                    break

        return collected