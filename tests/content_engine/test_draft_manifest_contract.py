from content_engine.content_drafting_governance import build_manifest

def test_manifest_hard_false():
    manifest = build_manifest({"x": 1})
    assert manifest["draft_creation_allowed"] is False
    assert manifest["content_generation_allowed"] is False
    assert manifest["canonical_json"] is True
    assert "self_sha256" in manifest
