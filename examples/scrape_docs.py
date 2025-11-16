"""
Example script to scrape PennyLane documentation.

This script demonstrates how to use the PennyLaneDocScraper to crawl
docs.pennylane.ai and prepare documentation for RAG systems.

Usage:
    uv run examples/scrape_docs.py

The script will:
1. Scrape a limited number of PennyLane documentation pages
2. Extract clean text content
3. Chunk the text for RAG (500-1000 tokens per chunk)
4. Save chunks to data/pennylane_docs/ directory
5. Display statistics about the scraped content
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import skadi
sys.path.insert(0, str(Path(__file__).parent.parent))

from skadi.utils.doc_scraper import PennyLaneDocScraper


async def main():
    """Main function to run the scraper."""
    print("=" * 80)
    print("PennyLane Documentation Scraper")
    print("=" * 80)
    print()

    # Configuration
    output_dir = "data/pennylane_docs"
    max_pages = 5  # Limit to 5 pages for testing

    # Example URLs to scrape (you can customize these)
    start_urls = [
        "https://docs.pennylane.ai/en/stable/",  # Main docs page
        "https://docs.pennylane.ai/en/stable/introduction/circuits.html",  # Circuits intro
        "https://docs.pennylane.ai/en/stable/code/qml.html",  # QML API reference
    ]

    print("Configuration:")
    print(f"  Output directory: {output_dir}")
    print(f"  Max pages: {max_pages}")
    print(f"  Start URLs: {len(start_urls)}")
    print()

    # Create scraper instance
    scraper = PennyLaneDocScraper(
        output_dir=output_dir,
        chunk_size_tokens=750,  # Target chunk size
        chunk_overlap_tokens=100,  # Overlap for context
        rate_limit_seconds=1.0,  # Be nice to the server
    )

    print("Starting scrape...")
    print("-" * 80)
    print()

    try:
        # Scrape the documentation
        await scraper.scrape_documentation(start_urls=start_urls, max_pages=max_pages)

        print()
        print("=" * 80)
        print("Scraping Statistics")
        print("=" * 80)
        print()

        # Get and display statistics
        stats = scraper.get_statistics()

        print(f"Total pages scraped: {stats['total_pages']}")
        print(f"Total chunks created: {stats['total_chunks']}")
        print(f"Total characters: {stats['total_characters']:,}")
        print(f"Estimated total tokens: {stats['estimated_total_tokens']:,}")
        print(f"Average chunks per page: {stats['average_chunks_per_page']:.2f}")
        print(f"Average tokens per chunk: {stats['average_tokens_per_chunk']:.2f}")
        print()

        print("=" * 80)
        print("Next Steps")
        print("=" * 80)
        print()
        print("1. Check the output directory for JSON files:")
        print(f"   ls -lh {output_dir}/")
        print()
        print("2. Inspect a chunk file:")
        print(f"   cat {output_dir}/<filename>.json | jq")
        print()
        print("3. To scrape more pages, increase 'max_pages' in this script")
        print()
        print("4. To crawl all linked pages, uncomment the link-following code")
        print("   in doc_scraper.py (scrape_documentation method)")
        print()

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        print(f"Partial results saved to: {output_dir}")
    except Exception as e:
        print(f"\n\nError during scraping: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
