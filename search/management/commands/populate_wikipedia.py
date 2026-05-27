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

class Command(BaseCommand):
    help = 'Populate database with ~1500 Wikipedia summaries'

    def handle(self, *args, **options):
        wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='NicheSearchCapstone/1.0 (your-email@example.com)'  # CHANGE THIS
        )

        total_added = 0

        for category_name in CATEGORIES:
            if total_added >= TOTAL_ARTICLES_TARGET:
                break
            cat = wiki.page(f"Category:{category_name}")
            if not cat.exists():
                self.stdout.write(self.style.WARNING(f"Category not found: {category_name}"))
                continue

            try:
                articles = self.get_articles_recursive(cat, wiki, depth=1, limit_per_category=60)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to process category '{category_name}': {e}"))
                continue

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

        self.stdout.write(self.style.SUCCESS(f"Total new articles added: {total_added}"))

    def get_articles_recursive(self, category_page, wiki, depth=0, limit_per_category=60):
        collected = {}

        # Direct members of this category
        try:
            for member in category_page.categorymembers.values():
                if member.ns == 0:   # real article
                    try:
                        page = wiki.page(member.title)
                        if page.exists() and page.summary:
                            collected[page.fullurl] = (page.title, page.fullurl, page.summary)
                    except Exception:
                        continue
                if len(collected) >= limit_per_category:
                    break
        except Exception:
            # If the whole categorymembers call fails, return what we have
            pass

        # If depth > 0, also crawl subcategories
        if depth > 0:
            try:
                subcats = [m for m in category_page.categorymembers.values() if m.ns == 14]
            except Exception:
                subcats = []
            for subcat in subcats[:3]:
                try:
                    subcat_page = wiki.page(subcat.title)
                    if subcat_page.exists():
                        sub_articles_dict = self.get_articles_recursive(
                            subcat_page, wiki, depth=depth-1,
                            limit_per_category=limit_per_category // 2
                        )
                        for url, (title, link, summary) in sub_articles_dict.items():
                            if url not in collected:
                                collected[url] = (title, link, summary)
                                if len(collected) >= limit_per_category:
                                    break
                except Exception:
                    continue
                if len(collected) >= limit_per_category:
                    break

        return collected