import pytest
from content_engine.content_drafting_governance import validate_lifecycle_state

def test_allowed_lifecycle_state():
    assert validate_lifecycle_state("CONCEPTUAL_ONLY") == "CONCEPTUAL_ONLY"

@pytest.mark.parametrize("state", ["PUBLISHED", "FINAL", "SCHEDULED", "AUTO_APPROVED"])
def test_disallowed_lifecycle_states_block(state):
    with pytest.raises(ValueError):
        validate_lifecycle_state(state)
