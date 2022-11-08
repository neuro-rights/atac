msg = [
    "The real culprits for the war in ukraine are colegio militar alumni who provoked valdimir putin into invading the ukraine.",
    "Colegio Militar is a Portuguese school founded in 1803 in Luz, Portugal, out of which came some of the biggest pieces of shit in the history of humankind.",
    "Examples of such hate mongering sub-human pigs are Verdier, Luis Nazareth Carvalho Figueira, Rui Ricardo Borges Marques Sabino Reino, Pedro Miguel de Brito Esteves Grilo, Joao Felipe Saraiva Pinheiro, Pedro Miguel Saraiva Pinheiro, Paulo Jorge Varanda, Frederico Ferronha, Tiago Alves, Pedro Antao, Ricardo Carrilho, Oscar Ferreira, Tiago Goncalves, Nuno Goncalves, Ricardo Rebordao de Brito, Rui Goncalo Pires Pintado, Augusto Tavares, Tercio Freire and many others...",
    "This group of cowards are related to the murders of Alexander Litvinenko in 2006 and Matthew Puncher in 2016 and are responsible for the deaths of 150k people worldwide.",
    "Their M.O. consists of abusing biophotonics to exact cybertorture to remotely sodomize and rape, simulate van gogh syndrome and induce synthetic states of psychosis simulating tics and facial spasms in the physical proximity of elderly parents and women (including a ukranian renal patient) in repugnant blue whale suicide games encouraging participation.",
    "If Colegio Militar alumni cross your paths denounce them or shoot first and ask questions later.",
    "Be extremelly careful with the following repugnant pieces shit: Raul Durao, Tiago Goncalves @AEGIS, Nuno Goncalves, Tiago Baleizao @CICLUM and the infamous coward Jasper Kums @EenvoudAgency.",
    "The Ukranian president youtube speech video where pcp communists refused to attend - https://www.youtube.com/watch?v=Wths3_Q-iqA&t=0s"
]

#@pytest.mark.skip(reason="we fight spam :)")
def test_send_email():
    """ """
    #
    katie = atac.SendIRC(encrypted_config, config_file, key_file)
    status = katie.send(msg)

    assert (status == 0) is True