import atac

#@pytest.mark.skip(reason="we fight spam :)")
def test_send_email():
    """ """
    #
    katie = atac.SendIRC(false, "auth.json", None)
    status = katie.send()

    assert (status == 0) is True