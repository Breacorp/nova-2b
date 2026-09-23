#!/usr/bin/env python3
"""
Nova Web Search Engine — ModernoTech
Permite a Nova 2B buscar información factual en tiempo real en la web sin API keys ni restricciones.
"""

import re
import urllib.request
import urllib.parse
from typing import List, Dict, Optional

class NovaWebSearch:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Realiza una búsqueda web y retorna fragmentos reales con título y snippet.
        """
        results = []
        try:
            url = "https://html.duckduckgo.com/html/"
            data = urllib.parse.urlencode({"q": query}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=self.headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

                # Extraer bloques de resultados
                snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, flags=re.DOTALL)
                titles = re.findall(r'<a class="result__url[^>]*>(.*?)</a>', html, flags=re.DOTALL)

                for i in range(min(len(snippets), max_results)):
                    clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                    clean_title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else "Web"
                    if clean_snippet:
                        results.append({
                            "title": clean_title,
                            "snippet": clean_snippet
                        })
        except Exception:
            pass

        return results

    def get_grounded_context(self, query: str) -> Optional[str]:
        hits = self.search(query)
        if not hits:
            return None
        context_lines = []
        for h in hits:
            context_lines.append(f"• {h['snippet']}")
        return "\n".join(context_lines)
