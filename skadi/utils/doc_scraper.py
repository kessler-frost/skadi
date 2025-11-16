"""
PennyLane Documentation Scraper

This module provides functionality to scrape PennyLane documentation from docs.pennylane.ai
and prepare it for RAG (Retrieval Augmented Generation) systems.

Key Features:
- Async web scraping using Crawl4AI
- Text extraction (clean text, no markdown conversion)
- Intelligent chunking for RAG (500-1000 tokens per chunk)
- Metadata preservation (URL, title, section)
- Rate limiting and error handling
"""

import asyncio
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import NoExtractionStrategy


@dataclass
class DocumentChunk:
    """Represents a chunk of documentation with metadata."""

    text: str
    url: str
    title: str
    section: str
    chunk_index: int
    total_chunks: int
    char_count: int
    estimated_tokens: int


class PennyLaneDocScraper:
    """
    Scraper for PennyLane documentation.

    This class handles crawling docs.pennylane.ai, extracting clean text content,
    chunking it appropriately for RAG systems, and saving to disk.

    Configuration:
    - Base URL: https://docs.pennylane.ai
    - Chunk size: 500-1000 tokens (approx 2000-4000 characters)
    - Rate limiting: 1 second between requests
    - Browser: Headless Chromium via Playwright
    """

    def __init__(
        self,
        output_dir: str | Path = "data/pennylane_docs",
        chunk_size_tokens: int = 750,
        chunk_overlap_tokens: int = 100,
        rate_limit_seconds: float = 1.0,
    ):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save scraped chunks
            chunk_size_tokens: Target tokens per chunk (default: 750)
            chunk_overlap_tokens: Overlap between chunks for context (default: 100)
            rate_limit_seconds: Seconds to wait between requests (default: 1.0)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Estimate characters per token (rough average for English text)
        self.chars_per_token = 4
        self.chunk_size_chars = chunk_size_tokens * self.chars_per_token
        self.chunk_overlap_chars = chunk_overlap_tokens * self.chars_per_token
        self.rate_limit_seconds = rate_limit_seconds

        # PennyLane docs base URL
        self.base_url = "https://docs.pennylane.ai"

        # Track visited URLs to avoid duplicates
        self.visited_urls: set[str] = set()

    async def scrape_page(
        self, url: str, crawler: AsyncWebCrawler
    ) -> dict[str, Any] | None:
        """
        Scrape a single page and extract clean text.

        Args:
            url: URL to scrape
            crawler: AsyncWebCrawler instance

        Returns:
            Dictionary containing extracted text and metadata, or None if failed
        """
        if url in self.visited_urls:
            print(f"Skipping already visited URL: {url}")
            return None

        try:
            print(f"Scraping: {url}")

            # Configure the crawl
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,  # Always fetch fresh content
                extraction_strategy=NoExtractionStrategy(),  # We'll extract manually
                word_count_threshold=10,  # Minimum words to consider valid content
                exclude_external_links=True,
                remove_overlay_elements=True,
            )

            result = await crawler.arun(url=url, config=config)

            if not result.success:
                print(f"Failed to scrape {url}: {result.error_message}")
                return None

            self.visited_urls.add(url)

            # Extract clean text from the page
            # Crawl4AI provides cleaned text in result.markdown or result.cleaned_html
            # We'll use the markdown but strip all formatting to get plain text
            raw_text = result.markdown or result.cleaned_html or ""

            # Clean the text - remove markdown formatting
            clean_text = self._clean_text(raw_text)

            # Extract metadata
            title = self._extract_title(result.metadata) or "Untitled"
            section = self._extract_section(url)

            # Extract internal links for further crawling
            internal_links = self._extract_internal_links(
                result.links.get("internal", [])
            )

            return {
                "url": url,
                "title": title,
                "section": section,
                "text": clean_text,
                "internal_links": internal_links,
            }

        except Exception as e:
            print(f"Error scraping {url}: {e!s}")
            return None

    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing markdown formatting and extra whitespace.

        Args:
            text: Raw text with markdown formatting

        Returns:
            Clean plain text
        """
        # Remove markdown headers (## Header -> Header)
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

        # Remove markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        # Remove markdown bold/italic **text** or *text* -> text
        text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^\*]+)\*", r"\1", text)

        # Remove markdown code blocks ```code``` -> code
        text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text, flags=re.DOTALL)

        # Remove inline code `code` -> code
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove markdown lists - or * prefix
        text = re.sub(r"^[\*\-]\s+", "", text, flags=re.MULTILINE)

        # Remove extra whitespace and normalize line breaks
        text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 consecutive newlines
        text = re.sub(r" {2,}", " ", text)  # Multiple spaces -> single space

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _extract_title(self, metadata: dict) -> str:
        """Extract page title from metadata."""
        if not metadata:
            return "Untitled"
        return metadata.get("title", metadata.get("og:title", "Untitled"))

    def _extract_section(self, url: str) -> str:
        """
        Extract section name from URL.

        Example: https://docs.pennylane.ai/en/stable/code/qml.html -> code/qml
        """
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        # Remove language and version prefixes (e.g., en/stable/)
        path = re.sub(r"^(en|fr|de|es)/[^/]+/", "", path)

        # Remove file extension
        path = re.sub(r"\.(html|htm)$", "", path)

        return path or "index"

    def _extract_internal_links(self, links: list[dict]) -> list[str]:
        """
        Extract and filter internal PennyLane doc links.

        Args:
            links: List of link dictionaries from Crawl4AI

        Returns:
            List of clean internal URLs
        """
        internal_urls = []
        for link in links:
            href = link.get("href", "")
            if href.startswith("http"):
                # Absolute URL - check if it's a PennyLane doc
                if "docs.pennylane.ai" in href:
                    internal_urls.append(href)
            elif href.startswith("/"):
                # Relative URL - construct full URL
                full_url = urljoin(self.base_url, href)
                internal_urls.append(full_url)

        return list(set(internal_urls))  # Remove duplicates

    def chunk_text(
        self, text: str, url: str, title: str, section: str
    ) -> list[DocumentChunk]:
        """
        Split text into chunks suitable for RAG.

        Uses a simple sliding window approach with overlap to maintain context.

        Args:
            text: Text to chunk
            url: Source URL
            title: Page title
            section: Section name

        Returns:
            List of DocumentChunk objects
        """
        if not text:
            return []

        chunks = []

        # Split by paragraphs first to avoid breaking mid-paragraph
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, save current chunk
            if (
                len(current_chunk) + len(paragraph) > self.chunk_size_chars
                and current_chunk
            ):
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap (last N characters of previous chunk)
                overlap_text = current_chunk[-self.chunk_overlap_chars :]
                current_chunk = overlap_text + "\n\n" + paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Create DocumentChunk objects
        total_chunks = len(chunks)
        chunk_objects = []

        for i, chunk_text in enumerate(chunks):
            char_count = len(chunk_text)
            estimated_tokens = char_count // self.chars_per_token

            chunk_obj = DocumentChunk(
                text=chunk_text,
                url=url,
                title=title,
                section=section,
                chunk_index=i,
                total_chunks=total_chunks,
                char_count=char_count,
                estimated_tokens=estimated_tokens,
            )
            chunk_objects.append(chunk_obj)

        return chunk_objects

    def save_chunks(self, chunks: list[DocumentChunk], page_url: str) -> None:
        """
        Save chunks to disk with metadata.

        Creates one JSON file per page containing all chunks.

        Args:
            chunks: List of DocumentChunk objects
            page_url: URL of the source page
        """
        if not chunks:
            return

        # Create a safe filename from the URL
        parsed = urlparse(page_url)
        safe_filename = parsed.path.strip("/").replace("/", "_").replace(".", "_")
        if not safe_filename:
            safe_filename = "index"

        output_file = self.output_dir / f"{safe_filename}.json"

        # Convert chunks to dict for JSON serialization
        chunks_data = [asdict(chunk) for chunk in chunks]

        # Save to file
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "page_url": page_url,
                    "chunk_count": len(chunks),
                    "chunks": chunks_data,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"Saved {len(chunks)} chunks to {output_file}")

    async def scrape_documentation(
        self,
        start_urls: list[str] | None = None,
        max_pages: int | None = None,
        follow_links: bool = False,
    ) -> None:
        """
        Scrape PennyLane documentation starting from given URLs.

        This method:
        1. Crawls pages starting from start_urls
        2. Extracts clean text
        3. Chunks the text
        4. Saves chunks with metadata
        5. Optionally follows internal links (breadth-first)

        Args:
            start_urls: List of URLs to start crawling (default: main docs page)
            max_pages: Maximum number of pages to scrape (None = unlimited)
            follow_links: Whether to follow internal links for recursive crawling (default: False)
        """
        if start_urls is None:
            start_urls = [f"{self.base_url}/en/stable/"]

        # Configure browser for optimal performance
        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            # Queue for URLs to scrape
            url_queue = list(start_urls)
            pages_scraped = 0

            while url_queue and (max_pages is None or pages_scraped < max_pages):
                url = url_queue.pop(0)

                # Scrape the page
                result = await self.scrape_page(url, crawler)

                if result:
                    # Chunk the text
                    chunks = self.chunk_text(
                        result["text"],
                        result["url"],
                        result["title"],
                        result["section"],
                    )

                    # Save chunks
                    self.save_chunks(chunks, result["url"])

                    pages_scraped += 1
                    print(f"Progress: {pages_scraped}/{max_pages or '∞'} pages")

                    # Add internal links to queue (if following links)
                    if follow_links:
                        for link in result["internal_links"]:
                            if link not in self.visited_urls and link not in url_queue:
                                url_queue.append(link)

                # Rate limiting
                await asyncio.sleep(self.rate_limit_seconds)

        print(f"\nScraping complete! Scraped {pages_scraped} pages.")
        print(f"Output saved to: {self.output_dir}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about scraped documentation.

        Returns:
            Dictionary with statistics
        """
        if not self.output_dir.exists():
            return {"error": "Output directory does not exist"}

        json_files = list(self.output_dir.glob("*.json"))
        total_chunks = 0
        total_chars = 0
        total_tokens = 0

        for json_file in json_files:
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                total_chunks += data["chunk_count"]
                for chunk in data["chunks"]:
                    total_chars += chunk["char_count"]
                    total_tokens += chunk["estimated_tokens"]

        return {
            "total_pages": len(json_files),
            "total_chunks": total_chunks,
            "total_characters": total_chars,
            "estimated_total_tokens": total_tokens,
            "average_chunks_per_page": total_chunks / len(json_files)
            if json_files
            else 0,
            "average_tokens_per_chunk": total_tokens / total_chunks
            if total_chunks
            else 0,
        }


# Convenience function for quick scraping
async def scrape_pennylane_docs(
    output_dir: str = "data/pennylane_docs",
    start_urls: list[str] | None = None,
    max_pages: int | None = 10,
    follow_links: bool = False,
) -> None:
    """
    Quick function to scrape PennyLane documentation.

    Args:
        output_dir: Where to save the chunks
        start_urls: URLs to start scraping from
        max_pages: Maximum pages to scrape
        follow_links: Whether to follow internal links for recursive crawling
    """
    scraper = PennyLaneDocScraper(output_dir=output_dir)
    await scraper.scrape_documentation(
        start_urls=start_urls, max_pages=max_pages, follow_links=follow_links
    )
    stats = scraper.get_statistics()
    print("\nStatistics:")
    print(json.dumps(stats, indent=2))
