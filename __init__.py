from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'infexp'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 12


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    min_expectation = models.FloatField(
        label = "Was ist Ihre minimale Inflationserwartung? ")
    max_expectation = models.FloatField(
        label = "Was ist Ihre maximale Inflationserwartung? ")
    mid_point = models.FloatField()
    question = models.StringField(
        choices=["A", "B"],
        label=""
    )
    midpoint_q25 = models.FloatField()
    midpoint_q75 = models.FloatField()



class InflationData(ExtraModel):
    # neues Model für die Datenspeicherung, beinhaltet die Variablen, deren Werte gespeichert werden sollen
    player = models.Link(Player)
    round_number = models.IntegerField()
    session = models.IntegerField()
    min_expectation = models.FloatField()
    max_expectation = models.FloatField()
    mid_point = models.FloatField()
    question = models.StringField()
    midpoint_q25 = models.FloatField()
    midpoint_q75 = models.FloatField()




#FUNCTIONS

def midpoint(player: Player):
    # Funktion, die den midpoint ausrechnet und dabei je nach Antwort des Players entweder min oder max mit dem vorherigen midpoint ersetzt (bisection method)
    if player.round_number == 1:
       player.mid_point = (player.min_expectation + player.max_expectation) / 2
    else:
        if player.in_round(player.round_number - 1).question == "A":
            player.max_expectation = player.in_round(player.round_number - 1).mid_point
            player.min_expectation = player.in_round(player.round_number - 1).min_expectation
            player.mid_point = (player.min_expectation + player.max_expectation) / 2
        else:
            player.min_expectation = player.in_round(player.round_number - 1).mid_point
            player.max_expectation = player.in_round(player.round_number - 1).max_expectation
            player.mid_point = (player.min_expectation + player.max_expectation) / 2
    return player.mid_point


def midpoint_q25(player: Player):
    if player.round_number == 4:
        player.midpoint_q25 = (player.in_round(1).min_expectation + player.in_round(1).mid_point) / 2
        player.max_expectation = player.in_round(1).mid_point
    elif player.round_number > 4:
        if player.in_round(player.round_number - 1).question == "A":
            player.max_expectation = player.in_round(player.round_number - 1).midpoint_q25
            player.min_expectation = player.in_round(player.round_number - 1).min_expectation
            player.midpoint_q25 = (player.min_expectation + player.max_expectation) / 2
        else:
            player.min_expectation = player.in_round(player.round_number - 1).midpoint_q25
            player.max_expectation = player.in_round(player.round_number - 1).max_expectation
            player.midpoint_q25 = (player.min_expectation + player.max_expectation) / 2
    return player.midpoint_q25


def midpoint_q75(player: Player):
    if player.round_number == 8:
        player.midpoint_q75 = (player.in_round(1).max_expectation + player.in_round(1).mid_point) / 2
        player.min_expectation = player.in_round(1).mid_point
    elif player.round_number > 8:
        if player.in_round(player.round_number - 1).question == "A":
            player.max_expectation = player.in_round(player.round_number - 1).midpoint_q75
            player.min_expectation = player.in_round(player.round_number - 1).min_expectation
            player.midpoint_q75 = (player.min_expectation + player.max_expectation) / 2
        else:
            player.min_expectation = player.in_round(player.round_number - 1).midpoint_q75
            player.max_expectation = player.in_round(player.round_number - 1).max_expectation
            player.midpoint_q75 = (player.min_expectation + player.max_expectation) / 2
    return player.midpoint_q75



def custom_export(players):
    # zur customized Datenspeicherung, nennt noch mal die Felder die später in der Matrix sein werden
    yield ['player', 'round_number', 'mid_point', 'question', 'min_expectation', 'max_expectation', 'midpoint_q25', 'midpoint_q75']
    #for p in players:
    data = InflationData.filter()
    for d in data:
        player = d.player
        round_number = d.round_number
        mid_point = d.mid_point
        question = d.question
        min_expectation = d.min_expectation
        max_expectation = d.max_expectation
        midpoint_q25 = d.midpoint_q25
        midpoint_q75 = d.midpoint_q75

        yield [d.player, player.round_number, d.mid_point, d.question, d.min_expectation, d.max_expectation, d.midpoint_q25, d.midpoint_q75]



# PAGES

class InflationsErwartung(Page):
    # Spieler werden in Runde 1 nach Inflationserwartung gefragt
    form_model = "player"
    form_fields = ["min_expectation", "max_expectation"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if values['min_expectation'] > values['max_expectation']:
            return 'Ihre minimale Inflationserwartung darf nicht größer als Ihre maximale Inflationserwartung sein.'
        elif values['min_expectation'] == values['max_expectation']:
            return 'Minimale und maximale Inflationserwartung dürfen nicht gleich sein.'


class Bisection(Page):
    form_model = "player"
    form_fields = ["question"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 1 and player.round_number <=4


    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            min_expectation = player.in_round(1).min_expectation,
            max_expectation = player.in_round(1).max_expectation,
            mid_point=midpoint(player)
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # fügt jede Runde Werte zur customized Datenmatrix hinzu
        InflationData.create(
            player=player,
            round_number=player.round_number,
            mid_point =player.mid_point,
            question = player.question,
            min_expectation = player.min_expectation,
            max_expectation = player.max_expectation,
            midpoint_q25= None,
            midpoint_q75 = None
        )


class Results(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 4

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            min_expectation = player.in_round(1).min_expectation,
            max_expectation = player.in_round(1).max_expectation,
            mid_point=player.in_round(4).mid_point
        )


class Q25(Page):
    form_model = "player"
    form_fields = ["question"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 4 and player.round_number <= 8

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            min_expectation = player.in_round(1).min_expectation,
            mid_point = player.in_round(1).mid_point,
            midpoint_q25=midpoint_q25(player)
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # fügt jede Runde Werte zur customized Datenmatrix hinzu
        InflationData.create(
            player=player,
            round_number=player.round_number,
            mid_point =None,
            question = player.question,
            min_expectation = player.min_expectation,
            max_expectation = player.max_expectation,
            midpoint_q25= player.midpoint_q25,
            midpoint_q75 = None
        )


class Results_Q25(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 8

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            min_expectation = player.in_round(1).min_expectation,
            mid_point=player.in_round(1).mid_point,
            midpoint_q25=player.in_round(8).midpoint_q25
        )


class Q75(Page):
    form_model = "player"
    form_fields = ["question"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 8 and player.round_number <= 12

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            max_expectation = player.in_round(1).max_expectation,
            mid_point = player.in_round(1).mid_point,
            midpoint_q75=midpoint_q75(player)
        )
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # fügt jede Runde Werte zur customized Datenmatrix hinzu
        InflationData.create(
            player=player,
            round_number=player.round_number,
            mid_point =None,
            question = player.question,
            min_expectation = player.min_expectation,
            max_expectation = player.max_expectation,
            midpoint_q25= None,
            midpoint_q75 = player.midpoint_q75
        )



class Results_Q75(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 12

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            max_expectation = player.in_round(1).max_expectation,
            mid_point=player.in_round(1).mid_point,
            midpoint_q75=player.in_round(12).midpoint_q75
        )

page_sequence = [InflationsErwartung, Bisection, Results, Q25, Results_Q25, Q75, Results_Q75]
