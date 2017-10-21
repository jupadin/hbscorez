from django.db import models
from django.urls import reverse

from associations.models import Association


class District(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField(unique=True)
    association = models.ForeignKey(Association)

    def get_absolute_url(self):
        params = {
            'assoc_abbr': self.association.abbreviation.lower(),
            'dist_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:district', kwargs=params)

    def __str__(self):
        return 'District: {}'.format(self.abbreviation)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def get_absolute_url(self):
        params = {
            'assoc_abbr': self.district.association.abbreviation.lower(),
            'dist_abbr': self.district.abbreviation.lower(),
            'league_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:league', kwargs=params)

    def scorers_url(self):
        params = {
            'assoc_abbr': self.district.association.abbreviation.lower(),
            'dist_abbr': self.district.abbreviation.lower(),
            'league_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:scorers', kwargs=params)

    def __str__(self):
        return 'League: {} - {}'.format(self.district.abbreviation, self.abbreviation)


class Team(models.Model):
    name = models.TextField()
    league = models.ForeignKey(League)

    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = ('name', 'league')

    def __str__(self):
        return 'Team: {}/{}'.format(self.name, self.league.abbreviation)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def __str__(self):
        return 'Player: {}'.format(self.name)

    def get_url(self):
        return self.team.logo.url


class Score(models.Model):
    player = models.ForeignKey(Player)
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
