from django.conf import settings
from django.core import validators
from django.db import models
from django.urls import reverse

from districts.models import District


class Season(models.Model):
    start_year = models.PositiveIntegerField(unique=True, validators=[
        validators.MinValueValidator(1990),
        validators.MaxValueValidator(2050)])

    def __str__(self):
        return '{}/{}'.format(self.start_year, self.start_year + 1)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district', 'season'), ('abbreviation', 'district', 'season'))

    def __str__(self):
        return '{} {} {}'.format(self.bhv_id, self.name, self.season)

    def get_absolute_url(self):
        return reverse('leagues:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_source_url(bhv_id):
        return settings.ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&all=1&score={}'.format(bhv_id)

    def source_url(self):
        return self.build_source_url(self.bhv_id)

    @property
    def youth(self) -> bool:
        return self.is_youth(self.abbreviation, self.name)

    @staticmethod
    def is_youth(abbreviation: str, name: str) -> bool:
        youth_name_indicators_direct = [
            'Jugend', 'Jgd', 'Mini', 'Jungen', 'Mädchen',
            'Jongen', 'Meedercher', 'weiblich', 'männlich',
            'Auswahl', 'Mini']
        youth_names_indicators_two_letters = [
            gender + age_class
            for gender in ['m', 'w']
            for age_class in ['A', 'B', 'C', 'D', 'E']]
        youth_names_indicators_three_letters = [
            gender + 'J' + age_class
            for gender in ['M', 'W', 'm', 'w']
            for age_class in ['A', 'B', 'C', 'D', 'E']]
        youth_abbreviation_indicators_first_letter = ['m', 'w', 'g', 'u', 'U']

        youth_match = abbreviation[:1] in youth_abbreviation_indicators_first_letter \
            or any(n in name for n in
                   youth_name_indicators_direct
                   + youth_names_indicators_two_letters
                   + youth_names_indicators_three_letters)

        adult_name_indicators = [
            'Männer', 'Frauen', 'Herren', 'Damen',
            'Hären', 'Dammen', 'Senioren', 'Seniorinnen',
            'Hommes', 'Dames', 'Fraen', 'Inklusion']
        adult_abbreviation_indicators_first_letter = ['M', 'F', 'Ü']
        adult_match = abbreviation[:1] in adult_abbreviation_indicators_first_letter \
            or any(n in name for n in adult_name_indicators)

        if youth_match == adult_match:
            raise YouthUndecidableError(abbreviation, name, youth_match)
        return youth_match


class YouthUndecidableError(Exception):
    def __init__(self, abbreviation: str, name: str, message: str, *args: object) -> None:
        self.abbreviation = abbreviation
        self.name = name
        self.message = message or f"Youth undecidable: '{self.abbreviation}' '{self.name}'"
        super().__init__(self.message, *args)
