"""
RevenueAI 360 - RAG Vector Search Tool
Allows agents to execute deterministic vector similarity queries against enterprise documents.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from shared.state import CitationItem
from services.rag.knowledge_service import knowledge_service
from tools.registry import tool_registry, ToolDefinition


class SearchKnowledgeInput(BaseModel):
    query: str
    top_k: int = 3
    doc_type: Optional[str] = None


class SearchKnowledgeOutput(BaseModel):
    citations: List[CitationItem] = Field(default_factory=list)
    query: str
    result_count: int


async def handle_search_knowledge(
    query: str,
    top_k: int = 3,
    doc_type: Optional[str] = None,
) -> SearchKnowledgeOutput:
    citations = await knowledge_service.search(query=query, top_k=top_k, doc_type=doc_type)
    return SearchKnowledgeOutput(
        citations=citations,
        query=query,
        result_count=len(citations),
    )


tool_registry.register(
    ToolDefinition(
        name="search_knowledge",
        description="Searches enterprise knowledge base for policies, product specifications, and case studies.",
        input_schema=SearchKnowledgeInput,
        output_schema=SearchKnowledgeOutput,
        side_effect=False,
        approval_required=False,
        permission_level="read_only",
    ),
    handle_search_knowledge,
)
