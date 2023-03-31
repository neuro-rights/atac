from operator import truediv
import os
import random
import sys
import pytest
import atac

# :(
emergency = True
#
encrypted_config = False
config_file = "auth.json"
key_file = None
#
subjects = [
    "Criminal associates of Colegio Militar alumni linked to Paulo Ribeiro - REMAX and criminal associates of Tiago Alves, Paulo Jorge Varanda, Hugo Caldeira, Joao Filipe Saraiva Pinheiro, Pedro Saraiva Pinheio and Pedro Miguel de Brito Esteves Grilo @PSP exact cybertorture extrajudicial sentences via recruited criminals at Jardim do Adamastor and bar Crew Hassan to bypass physical ban in criminal association with law enforcement, creating drug addicts and directing violence to parents women and children, automating sentences for chewing, breathing, walking and thinking about words under sleep deprivation since 2016 to turn me homeless, force me into psychiatric care and kick me out of the Netherlands sabotaging work systematically by simulating Van Gogh syndrome",
    "ricardo rebordao de brito, carla maria marinho rodrigues, goncalo bandeira duarte, tiago jorge roque, luis muskiado e associados criminosos de pedro miguel de brito esteves grilo @PSP, e joao filipe saraiva pinheiro enchem portugal de violencia domestica e criam toxicodependentes e sem abigo em rituais de cibertortura vibrotactil para insuzirem psicose instantanea desde que acordam as suas vitimas para jogarem auto-mutilacao e articular linguas, com interesse especial em torturar pessoas dentro de igrejas, dirigindo violencia contra mulheres e idosos para forcarem prisao, suicidio ou internamento compulsivo"
    "jasper kums and colégio militar alumni gamble with life and direct violence inducing synthetic psychosis in the middle of the night, abusing biophotonics to direct violence against parents, women and children",
    "colégio militar alumni and criminal associates participate in interactive human degradation spectacles to turn people homeless, force them into poverty, gambling life in blue whale suicide games where they take turns abusing biophotonics to execute vibrotactile cybertorture, force psychosis and simulate Van Gogh syndrome in a style reminiscent of the murder of Matthew Puncher",
    "colégio militar alumni linked Pedro Miguel de Brito Esteves Grilo @PSP and criminal associates of Jasper Kums spent the last 6 years trying to force me into a psychiatric asylum waking me up daily to induce psychosis in blue whale suicide game where they take turns abusing biophotonics to simulate Van Gogh syndrome whilst having intercouse with each others, sabotaging my ex-girlfriends plans to get wed, with Emile Barkhof hidding the extrajudicial sentence",
    "Colegio Militar alumni (largo da luz, Portugal) linked to the CM93 blue-whale suicide group are degrading a Ukranian renal patient everyday as an interactive ritualistic cybertorture spectacle (planned over a decade ago) intensified daily at 4:00 am in front of Law Enforcement and directed violence towards her daily for over 1 year, sabotaging plans to get wed and putting her child in danger. They are linked to HUGO FARINHA, Raul Durao, Oscar Ferreira, Augusto Tavares, Tiago Alves and his brother, Tiago Baleizao (pharmaceutical expert at CICLUM FARMA), Ricardo Rebordao de Brito, Tiago Goncalves @Aegis with links to cyber-terrorist group 'Anonymous', Nuno Goncalves and criminal associates linked to Roy Van Putten, Jurgen Braam, JASPER KUMS, Bill Wandi, Tiago Santos Sousa and his idiotic and cowardly friend ARTUR, along with criminal wannabe's JOAO LEIRIA, GONCALO BANDEIRA DUARTE and TIAGO JORGE ROQUE, Arthur Moreno, LUIS MUSKIADO.",
    "Idiotic and cowardly Colegio Militar alumni (largo da luz, Portugal) Augusto Tavares who thinks he is king of the underworld, freemason Oscar Ferreira, Tiago Alves and his coward brother from the armed forces, Tiago Baleizao (pharmaceutical expert), The cowards from the Goncalves family Tiago Goncalves @Aegis with links to cyber-terrorist group 'Anonymous' and Nuno Goncalves and criminal associates linked to Roy Van Putten, Jurgen Braam, JASPER KUMS, Bill Wandi, Tiago Santos Sousa and his friend Artur and netherlands law enforcement attempting to portrait me as a grotesque and psychotic Putin fanboy in an attempt to either coerce psychiatric care or force me out of the Netherlands penniless, sabotaged the wedding plans of my Ukranian girlfriend (a renal patient) by abusing counter-terrorism / crowd control government infrastructure, resorting to biophotonics, optoacoustics and other methodologies to degrade my cognition, physical and mental well being.",
    "Paulo Portas @CDS, Eduardo Marcal Grilo @PS, Pedro Miguel de Brito Esteves Grilo @PSP, Oscar Ferreira, Paulo Varanda (former president of Cartaxo), Tiago Alves and his brothers and Tiago Goncalves @Aegis insurance - cybertorture, #opMentalHealth and A/HRC/43/49 - 'tango' versus the racial hate mongering 'cha cha cha' of Carla Maria Marinho Rodrigues, Pedro Silva - bar A Capela, Luis Muskiado, Filipa Sequeira, Tiago Santos Sousa and Arthur Moreno - how 'deep state' extrajudicial delusional ridders in the netherlands narcostate linked to Jasper Kums and related law enforcement officers (including relatives and some guy named Fuller) mongered racial hatred recruited the CM93 blue whale suicide game group who abused me and my parents along with some members of the 'anonymous' group decided to recruit known criminal from jardim do adamastor in lisbon, portugal linked to the demonic capoverdians known as Calo and Marcio to clean out 'human trash' by abusing bio-photonics to induce psychosis, direct violence to women systematically, articulate tongues and simulate van gogh syndrome to coerce conventional pharmacotherapy upon the population by abusing a medium that could provide superior therapeutic value to instead exact extrajudicial sentences, bypassing physical proximity ban whilst wearing silly Guy Fawkes terrorist masks and sexually subjugating the population to soviet style psychiatry under banners such as 'the mating calls of crickets' and 'NO LOVE LOST'",
]

emergency_recipients = [
    "contacto@psp.pt",
    "geral@prociv.pt",
    "gnr@gnr.pt",
    "mail@ansr.pt",
    "sef@sef.pt",
    "geral@igai.pt",
    "sec.geral.mai@sg.mai.gov.pt",
    "geral@igai.pt",
]

development_recipients = [
    "strikles@gmail.com",
    "opvs.minor@gmail.com",
    "benedictvs.ora.labora@gmail.com",
]

emergency_email_file = "atac/tests/contacts/emergency_used_only_whilst_under_torture.csv"
development_email_file = "atac/tests/contacts/test_development.csv"

recipients = development_recipients
email_file = development_email_file

if emergency:
    recipients = emergency_recipients
    email_file = emergency_email_file

target_languages = ["el", "fr", "it", "ja", "pt", "uk", "nl", "la"]


@pytest.mark.skip(reason="we fight spam :)")
def test_send_email():
    """ """
    #
    katie = atac.SendEmail(encrypted_config, config_file, key_file)
    auth, _ = katie.get_config()
    #
    subject = random.sample(subjects, 1).pop()
    message_content = katie.get_file_content(
        os.path.abspath(os.path.join(os.getcwd(), "data/messages/email/neurorights.md")),
        "message",
    )
    print(os.path.abspath(os.getcwd()))
    mailing_list = "; ".join(recipients)
    status = katie.send(
        mailing_list,
        message_content,
        subject
    )
    assert (status == 0) is True

