import atac

#@pytest.mark.skip(reason="we fight spam :)")
def test_send_irc():
    """ """
    #
    katie = atac.SendIRC(False, "auth.json", None)
    status = katie.send(None)

    assert (status == 0) is True