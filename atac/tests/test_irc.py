import atac

#@pytest.mark.skip(reason="we fight spam :)")
def test_send_email():
    """ """
    #
    katie = atac.SendIRC(encrypted_config, config_file, key_file)
    status = katie.send()

    assert (status == 0) is True