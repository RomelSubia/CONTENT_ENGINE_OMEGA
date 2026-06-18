from content_engine.content_draft_publication_governance.models import (
    ALLOWED_DECISIONS,
    FAILED_STATUS,
    FORBIDDEN_DECISIONS,
    READY_STATUS,
    PublicationGovernanceResult,
)


def test_models_define_plan_only_statuses_and_decisions():
    assert READY_STATUS == "READY_FOR_PUBLICATION_EXECUTION_GOVERNANCE_PLAN_ONLY"
    assert FAILED_STATUS == "FAILED_CLOSED"
    assert "AUTHORIZE_PUBLICATION_GOVERNANCE_PLAN_ONLY" in ALLOWED_DECISIONS
    assert "PUBLISH_NOW" in FORBIDDEN_DECISIONS
    assert "TRIGGER_N8N_NOW" in FORBIDDEN_DECISIONS


def test_result_defaults_keep_all_side_effects_false():
    result = PublicationGovernanceResult(
        request_id="REQ-1",
        publication_governance_status=READY_STATUS,
    )
    assert result.result_is_plan_only is True
    assert result.publication_performed is False
    assert result.posting_performed is False
    assert result.publication_scheduled is False
    assert result.publication_channel_mutated is False
    assert result.automation_started is False
    assert result.n8n_started is False
    assert result.webhook_started is False
    assert result.capa9_started is False
    assert result.queue_write_performed is False
    assert result.queue_item_created is False
    assert result.queue_item_updated is False
    assert result.runtime_execution_started is False
