"""
FastAPI application entrypoint.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.core.exceptions import ModelNotReadyError, register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.data_layer.repository import Repository
from app.services.compliance import ComplianceEngine
from app.services.embeddings import EmbeddingService, Encoder
from app.services.extractor import (
    ProductVocabulary,
    RuleBasedRequirementExtractor,
    build_product_vocabulary,
)
from app.services.fixer import AIFixer
from app.services.gap_analysis import GapAnalyzer
from app.services.index_builder import build_index
from app.services.matcher import Matcher
from app.services.normative import NormativeGraphService
from app.services.provenance import ProvenanceResolver
from app.services.qco import QcoLookup
from app.services.reranker import Reranker
from app.services.vector_db import FaissVectorStore, VectorStore

logger = get_logger(__name__)

@dataclass
class AppState:
    settings: Settings
    repository: Repository
    embedding_service: EmbeddingService
    vector_store: VectorStore
    provenance: ProvenanceResolver
    qco_lookup: QcoLookup
    normative: NormativeGraphService
    compliance_engine: ComplianceEngine
    reranker: Reranker
    matcher: Matcher
    vocabulary: ProductVocabulary
    requirement_extractor: RuleBasedRequirementExtractor
    gap_analyzer: GapAnalyzer
    fixer: AIFixer

def _load_or_build_vector_store(
    repository: Repository,
    embedding_service: EmbeddingService,
    settings: Settings,
) -> VectorStore:
    try:
        store = FaissVectorStore.load(settings.vector_index_dir)
        if store.dimension != embedding_service.dimension:
            raise ModelNotReadyError(
                "Persisted index dimension does not match the current embedding model."
            )
        logger.info("Loaded persisted vector index", extra={"context": {"size": store.size}})
        return store
    except Exception as exc:
        logger.info(
            "No usable persisted vector index (%s); building a fresh one.",
            type(exc).__name__,
        )
        return build_index(
            repository, embedding_service, index_dir=settings.vector_index_dir
        )

def build_app_state(
    settings: Settings, encoder: Encoder | None = None
) -> AppState:
    repository = Repository(
        metadata_path=settings.bis_metadata_path,
        compliance_path=settings.bis_compliance_path,
        qco_mapping_path=settings.qco_mapping_path,
        normative_graph_path=settings.normative_graph_path,
        sources_path=settings.sources_path,
    )
    embedding_service = EmbeddingService(
        model_name=settings.embedding_model_name, encoder=encoder
    )
    return _assemble(repository, embedding_service, settings)

def _assemble(
    repository: Repository,
    embedding_service: EmbeddingService,
    settings: Settings,
) -> AppState:
    vector_store = _load_or_build_vector_store(
        repository, embedding_service, settings
    )

    provenance = ProvenanceResolver(repository)
    qco_lookup = QcoLookup(repository, provenance)
    normative = NormativeGraphService(repository, provenance)
    compliance_engine = ComplianceEngine(
        repository, provenance, qco_lookup, normative
    )
    reranker = Reranker()
    matcher = Matcher(
        embedding_service,
        vector_store,
        repository,
        top_k=settings.top_k_candidates,
        min_score=settings.min_match_score,
        reranker=reranker,
        provenance=provenance,
    )
    vocabulary = build_product_vocabulary(repository.get_all_standards())
    requirement_extractor = RuleBasedRequirementExtractor(vocabulary)
    gap_analyzer = GapAnalyzer(repository, compliance_engine, qco_lookup)
    fixer = AIFixer()

    return AppState(
        settings=settings,
        repository=repository,
        embedding_service=embedding_service,
        vector_store=vector_store,
        provenance=provenance,
        qco_lookup=qco_lookup,
        normative=normative,
        compliance_engine=compliance_engine,
        reranker=reranker,
        matcher=matcher,
        vocabulary=vocabulary,
        requirement_extractor=requirement_extractor,
        gap_analyzer=gap_analyzer,
        fixer=fixer,
    )

def refresh_state(state: AppState) -> AppState:
    state.repository.reload()
    return _assemble(
        state.repository, state.embedding_service, state.settings
    )

def create_app(
    settings: Settings | None = None,
    encoder: Encoder | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(resolved_settings.log_level)
        logger.info(
            "Starting up",
            extra={"context": {"app_env": resolved_settings.app_env}},
        )
        app.state.services = build_app_state(
            resolved_settings, encoder=encoder
        )
        logger.info(
            "Startup complete",
            extra={
                "context": {
                    "standards": len(
                        app.state.services.repository.get_all_standards()
                    ),
                    "vector_index_size": app.state.services.vector_store.size,
                }
            },
        )
        yield
        logger.info("Shutting down")

    app = FastAPI(
        title=resolved_settings.app_name,
        description=(
            "AI-driven BIS Standard Recommendation & Compliance Auditor -- "
            "decision-support only; every output must be verified against "
            "the current BIS portal before official use."
        ),
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    
    from fastapi.middleware.cors import CORSMiddleware
    
    # Configure CORS for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, restrict this to frontend domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    from app.core.logging_config import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)
    
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import RedirectResponse
    
    # Mount frontend static files
    app.mount("/frontend", StaticFiles(directory="static"), name="frontend")
    
    @app.get("/", include_in_schema=False)
    async def redirect_to_frontend():
        return RedirectResponse(url="/frontend/index.html")

    from app.api.endpoints import router
    from app.api.endpoints_bulk import router as bulk_router
    app.include_router(router, prefix=resolved_settings.api_v1_prefix)
    app.include_router(bulk_router, prefix=resolved_settings.api_v1_prefix)
    return app

app = create_app()
