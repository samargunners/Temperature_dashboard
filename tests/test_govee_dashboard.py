def test_temperature_none():
    temp = None
    ALERT_TEMP_THRESHOLD = 75
    color = "green" if temp is None or temp <= ALERT_TEMP_THRESHOLD else "red"
    assert color == "green"

def test_temperature_below_threshold():
    temp = 70
    ALERT_TEMP_THRESHOLD = 75
    color = "green" if temp is None or temp <= ALERT_TEMP_THRESHOLD else "red"
    assert color == "green"

def test_temperature_above_threshold():
    temp = 80
    ALERT_TEMP_THRESHOLD = 75
    color = "green" if temp is None or temp <= ALERT_TEMP_THRESHOLD else "red"
    assert color == "red"