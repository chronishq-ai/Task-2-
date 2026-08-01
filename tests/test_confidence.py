from core.confidence_handler import confidence_weighted_update


def test_confidence_effect():

    result = confidence_weighted_update(
        current_value=8,
        evidence_value=2,
        variable_speed=0.8,
        confidence_score=0.5
    )

    # Expected calculation:
    # effective_speed = 0.8 * 0.5 = 0.4
    # new_value = 8 + 0.4*(2-8)
    # new_value = 5.6

    assert result == 5.6



def test_high_confidence_changes_more():

    high_confidence = confidence_weighted_update(
        current_value=8,
        evidence_value=2,
        variable_speed=0.8,
        confidence_score=1
    )


    low_confidence = confidence_weighted_update(
        current_value=8,
        evidence_value=2,
        variable_speed=0.8,
        confidence_score=0.1
    )


    # Higher confidence should create a bigger movement

    assert abs(high_confidence - 8) > abs(low_confidence - 8)



def test_value_range_limit():

    result = confidence_weighted_update(
        current_value=5,
        evidence_value=10,
        variable_speed=1,
        confidence_score=1
    )


    # Value should never exceed max range

    assert result <= 10



def test_invalid_confidence():

    try:

        confidence_weighted_update(
            current_value=5,
            evidence_value=8,
            variable_speed=0.5,
            confidence_score=2
        )

        assert False

    except ValueError:

        assert True



test_confidence_effect()
test_high_confidence_changes_more()
test_value_range_limit()
test_invalid_confidence()


print("All confidence tests passed")