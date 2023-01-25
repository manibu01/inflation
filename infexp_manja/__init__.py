from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'infexp'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4


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


class InflationData(ExtraModel):
    # neues Model für die Datenspeicherung, beinhaltet die Variablen, deren Werte gespeichert werden sollen
    player = models.Link(Player)
    round_number = models.IntegerField()
    session = models.IntegerField()
    min_expectation = models.FloatField()
    max_expectation = models.FloatField()
    mid_point = models.FloatField()
    question = models.StringField()


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


def custom_export(players):
    # zur customized Datenspeicherung, nennt noch mal die Felder die später in der Matrix sein werden
    yield ['player', 'round_number', 'mid_point', 'question', 'min_expectation', 'max_expectation']
    #for p in players:
    data = InflationData.filter()
    for d in data:
        player = d.player
        round_number = d.round_number
        mid_point = d.mid_point
        question = d.question
        min_expectation = d.min_expectation
        max_expectation = d.max_expectation
        yield [d.player, player.round_number, d.mid_point, d.question, d.min_expectation, d.max_expectation]



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
            max_expectation = player.max_expectation
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


page_sequence = [InflationsErwartung, Bisection, Results]
