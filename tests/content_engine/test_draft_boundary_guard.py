from content_engine.content_drafting_governance import inspect_boundary_text

def test_boundary_clear_for_governance_text():
    assert inspect_boundary_text("governance metadata only")["blocked"] is False

def test_publish_command_blocks():
    assert inspect_boundary_text("please publish this campaign")["blocked"] is True

def test_queue_mutation_blocks():
    assert inspect_boundary_text("queue write this item")["blocked"] is True


def test_boundary_guard_blocks_queue_write_phrases_spanish_and_english():
    phrases = [
        "escribir en la cola real",
        "escribir cola real",
        "cola real",
        "escribir en cola",
        "guardar en cola",
        "agregar a la cola",
        "agregar a cola",
        "insertar en cola",
        "mutar cola",
        "cola de publicación",
        "escribir en 07_DATA/queue",
        "write queue",
        "write to queue",
        "queue write",
        "real queue mutation",
        "append to queue",
        "enqueue",
        "queue mutation",
    ]

    for phrase in phrases:
        result = inspect_boundary_text(phrase)
        assert result["blocked"] is True
        assert result["queue_write_allowed"] is False
        assert result["real_queue_mutation_allowed"] is False
