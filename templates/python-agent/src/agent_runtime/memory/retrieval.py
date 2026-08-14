from __future__ import annotations

import json
import re
from datetime import timezone

from .contracts import MemoryQuery, MemorySearchResult
from .sqlite_store import SQLiteMemoryStore, _iso


TOKEN = re.compile(r"[^\W_]+", re.UNICODE)


def _tokens(value: str) -> list[str]:
    return [token.casefold() for token in TOKEN.findall(value) if token.strip()]


class MemoryRetriever:
    def __init__(self, store: SQLiteMemoryStore) -> None:
        self.store = store

    def search(self, query: MemoryQuery) -> list[MemorySearchResult]:
        tokens = _tokens(query.text)
        if not tokens:
            return []
        self.store.apply_pending_index_events()
        match = " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in sorted(set(tokens)))
        limit = max(1, min(int(query.limit), 50))
        parameters: list[object] = [
            match,
            query.scope.tenant_id,
            query.scope.user_id,
            query.scope.project_id,
            _iso(query.as_of),
        ]
        type_clause = ""
        if query.memory_types:
            type_clause = f" AND r.memory_type IN ({','.join('?' for _ in query.memory_types)})"
            parameters.extend(query.memory_types)
        parameters.append(min(limit * 8, 200))
        rows = self.store.connection.execute(
            f"""
            SELECT r.*, bm25(memory_fts) AS fts_rank
            FROM memory_fts
            JOIN memory_records AS r ON r.id = memory_fts.record_id
            WHERE memory_fts MATCH ?
              AND memory_fts.tenant_id = ? AND memory_fts.user_id = ? AND memory_fts.project_id = ?
              AND r.tenant_id = ? AND r.user_id = ? AND r.project_id = ?
              AND r.status = 'active' AND (r.expires_at IS NULL OR r.expires_at > ?)
              {type_clause}
            ORDER BY fts_rank, r.id
            LIMIT ?
            """,
            [
                parameters[0],
                query.scope.tenant_id,
                query.scope.user_id,
                query.scope.project_id,
                query.scope.tenant_id,
                query.scope.user_id,
                query.scope.project_id,
                *parameters[4:],
            ],
        ).fetchall()
        results: list[MemorySearchResult] = []
        query_tokens = set(tokens)
        as_of = query.as_of.astimezone(timezone.utc)
        for row in rows:
            record = self.store._from_row(row)
            searchable = f"{record.summary} {json.dumps(record.content, ensure_ascii=False, sort_keys=True, default=str)}"
            record_tokens = set(_tokens(searchable))
            keyword = len(query_tokens & record_tokens) / len(query_tokens)
            fts = 1.0 / (1.0 + abs(float(row["fts_rank"])))
            age_days = max(0.0, (as_of - record.updated_at.astimezone(timezone.utc)).total_seconds() / 86400.0)
            freshness = 1.0 / (1.0 + age_days / 30.0)
            components = {
                "keyword_relevance": round(keyword, 6),
                "fts_relevance": round(fts, 6),
                "importance": round(max(0.0, min(record.importance, 1.0)), 6),
                "confidence": round(max(0.0, min(record.confidence, 1.0)), 6),
                "freshness": round(freshness, 6),
            }
            score = (
                0.55 * components["keyword_relevance"]
                + 0.10 * components["fts_relevance"]
                + 0.15 * components["importance"]
                + 0.10 * components["confidence"]
                + 0.10 * components["freshness"]
            )
            results.append(
                MemorySearchResult(
                    record=record,
                    score=round(score, 6),
                    score_components=components,
                    source=record.source,
                    evidence_refs=record.evidence_refs,
                    confidence=record.confidence,
                )
            )
        results.sort(key=lambda item: (-item.score, item.record.id))
        return results[:limit]
