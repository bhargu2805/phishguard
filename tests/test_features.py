from phishguard.features import extract_url_features, feature_names

def test_feature_vector_stable():
    cols = feature_names()
    f = extract_url_features("https://example.com/login?x=1")
    assert set(cols) == set(f.keys())
    # stable order across calls
    cols2 = feature_names()
    assert cols == cols2

def test_has_ip_detection():
    f = extract_url_features("http://192.168.0.1/login")
    assert f["has_ip"] == 1.0
