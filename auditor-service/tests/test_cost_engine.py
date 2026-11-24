def test_ebs_monthly_waste():

    size_gb = 10
    price_per_gb = 30

    result = size_gb * price_per_gb

    assert result == 300