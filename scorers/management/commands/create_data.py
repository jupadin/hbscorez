import os
import re
from urllib.parse import parse_qs, urlsplit

import requests
import tabula
from django.conf import settings
from django.core.management import BaseCommand
from lxml import html

from scorers.models import District, League, Player, Score, Team, Association


class Command(BaseCommand):
    def log(self, text: str) -> None:
        self.stdout.write(self.style.SUCCESS(text))

    def handle(self, *args, **options):
        Score.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()
        League.objects.all().delete()
        District.objects.all().delete()
        Association.objects.all().delete()

        badHV = Association(name='Badischer Handball-Verband', acronym='BHV', abbreviation='BAD')
        badHV.save()
        bayHV = Association(name='Bayerischer Handball-Verband', acronym='BHV', abbreviation='BAY')
        bayHV.save()
        # todo: shv - südbadischer handballverband

        districts = [
            ('Baden-Württemberg Oberliga', 'BWOL', badHV, 35, 4),
            ('Badischer Handball-Verband', 'BHV', badHV, 35, 35),
            ('Bezirk Nord', 'NORD', badHV, 35, 84),
            ('Bezirk Süd', 'SÜD', badHV, 35, 43),
            ('Bruchsal', 'BR', badHV, 35, 36),
            ('Heidelberg', 'HD', badHV, 35, 37),
            ('Karlsruhe', 'KA', badHV, 35, 38),
            ('Mannheim', 'MA', badHV, 35, 39),
            ('Pforzheim', 'PF', badHV, 35, 40),
        ]
        for num, data in enumerate(districts):
            self.log('District {}/{}'.format(num + 1, len(districts)))
            self.create_district(*data)

    def create_district(self, name, abbreviation, association, group_id, org_id):
        district = District(name=name, abbreviation=abbreviation, association=association)
        district.save()

        url = 'http://spo.handball4all.de/Spielbetrieb/index.php'
        request_data = {
            'orgGrpID': group_id,
            'orgID': org_id,
        }
        response = requests.post(url=url, data=request_data)

        tree = html.fromstring(code(response.text))
        league_links = tree.xpath('//*[@id="results"]/div/table[2]/tr/td[1]/a')

        for num, league_link in enumerate(league_links):
            self.log('  - League {}/{}'.format(num + 1, len(league_links)))
            self.create_league(league_link, district)

    def create_league(self, link, district):
        url = 'http://spo.handball4all.de/Spielbetrieb/index.php' + link.get('href') + '&all=1'
        response = requests.get(url=url)

        tree = html.fromstring(code(response.text))
        heading = tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
        name = heading.split(' - ')[0]
        abbreviation = link.text

        league = League(name=name, abbreviation=abbreviation, district=district)
        league.save()

        team_links = tree.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a')

        for team_link in team_links:
            team = Team(name=team_link.text, league=league)
            team.save()

        game_rows = tree.xpath('//table[@class="gametable"]/tr[position() > 1 and ./td[11]/a/@href]')
        for num, game_row in enumerate(game_rows):
            self.log("Game {}/{}".format(num + 1, len(game_rows)))
            self.create_scores(game_row, league=league)

    def create_scores(self, game_row, league):
        reports_path = settings.BASE_DIR + "/reports/"
        report_url = game_row.xpath('./td[11]/a/@href')[0]
        params = urlsplit(report_url)[3]
        game_id = parse_qs(params)['sGID'][0]
        file_path = "{}/{}.pdf".format(reports_path, game_id)

        if not os.path.isfile(file_path):
            response = requests.get(report_url, stream=True)
            with open(file_path, 'wb') as file:
                file.write(response.content)

        teams_pdf = tabula.read_pdf(file_path, output_format='json', encoding='cp1252',
                                    **{'pages': 1, 'lattice': True})
        team_names = teams_pdf[0]['data'][3][1]['text']
        home_team_name, guest_team_name = self.parse_team_names(team_names)
        scores_pdf = tabula.read_pdf(file_path, output_format='json', encoding='cp1252',
                                     **{'pages': 2, 'lattice': True})

        self.add_scores(scores_pdf[0], team_name=home_team_name, league=league)
        self.add_scores(scores_pdf[1], team_name=guest_team_name, league=league)

    def add_scores(self, table, team_name, league):
        team = Team.objects.get_or_create(name=team_name, league=league)[0]
        table_rows = table['data']
        for table_row in table_rows[2:]:
            row_data = [cell['text'] for cell in table_row]
            # player_number = row_data[0]
            player_name = row_data[1]
            # player_year_of_birth = row_data[2]
            goals_total = row_data[5] or 0
            penalty_tries, penalty_goals = self.parse_penalty_data(row_data[6])
            # warning_time = row_data[7]
            # first_suspension_time = row_data[8]
            # second_suspension_time = row_data[9]
            # third_suspension_time = row_data[10]
            # disqualification_time = row_data[11]
            # report_time = row_data[12]
            # team_suspension_time = row_data[13]

            if not player_name:
                continue

            player = Player.objects.get_or_create(name=player_name, team=team)[0]

            try:
                score = Score(
                    player=player,
                    goals=goals_total,
                    penalty_goals=penalty_goals,
                )
                score.save()
            except ValueError:
                continue

    def parse_penalty_data(self, text: str) -> (int, int):
        match = re.match("([0-9]+)/([0-9]+)", text)
        if match:
            return match.group(1), match.group(2)
        return 0, 0

    def parse_team_names(self, text: str) -> (int, int):
        match = re.match("(.+) - (.+)", text)
        return match.group(1), match.group(2)


def code(text: str):
    return text.encode("latin-1").decode()
