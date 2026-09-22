from django.core.management.base import BaseCommand
from django.db import transaction
from restaurants.models import MenuItem

try:
    from fastembed import TextEmbedding
    HAS_FASTEMBED = True
except ImportError:
    HAS_FASTEMBED = False


def build_menu_item_embedding_text(item: MenuItem) -> str:
    """
    Constructs a deterministic, semantic text representation of a MenuItem.
    Includes explicit metadata and descriptive text.
    """
    parts = [f"{item.name}."]
    if item.description:
        parts.append(f"{item.description}.")
    
    parts.append(f"Category: {item.category.name}.")
    parts.append(f"Cuisine: {item.restaurant.cuisine.name}.")
    
    tags = [t.name for t in item.tags.all()]
    if tags:
        parts.append(f"Tags: {', '.join(tags)}.")
        
    return " ".join(parts)


class Command(BaseCommand):
    help = "Generate missing or stale vector embeddings for MenuItems."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Force regenerate all embeddings regardless of stale state.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of items to embed in a single batch.",
        )

    def handle(self, *args, **options):
        if not HAS_FASTEMBED:
            self.stdout.write(self.style.ERROR("fastembed is not installed. Run `pip install fastembed`."))
            return

        force_all = options["all"]
        batch_size = options["batch_size"]

        if force_all:
            queryset = MenuItem.objects.all()
        else:
            queryset = MenuItem.objects.filter(is_embedding_stale=True)

        queryset = queryset.select_related("category", "restaurant__cuisine").prefetch_related("tags")
        total = queryset.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No stale embeddings found. Everything is up to date."))
            return

        self.stdout.write(self.style.NOTICE(f"Loading BAAI/bge-small-en-v1.5 model..."))
        # Initialize the model (downloads if not present)
        embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        self.stdout.write(self.style.NOTICE(f"Generating embeddings for {total} items..."))

        items = list(queryset)
        for i in range(0, total, batch_size):
            batch = items[i:i + batch_size]
            
            # 1. Build texts
            texts = [build_menu_item_embedding_text(item) for item in batch]
            
            # 2. Generate embeddings
            embeddings = list(embedding_model.embed(texts))
            
            # 3. Update DB
            with transaction.atomic():
                for item, vector in zip(batch, embeddings):
                    item.embedding = list(vector)  # Ensure it's a list for pgvector
                    item.is_embedding_stale = False
                MenuItem.objects.bulk_update(batch, ["embedding", "is_embedding_stale"])
                
            self.stdout.write(f"Processed batch {i // batch_size + 1}...")

        self.stdout.write(self.style.SUCCESS(f"Successfully generated embeddings for {total} items."))
