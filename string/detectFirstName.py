from SmartFramework.files import directory
from SmartFramework.string import normalize
from collections import namedtuple
import csv

# fichier provenant de https://www.data.gouv.fr/fr/datasets/liste-de-prenoms/#_
firstNames = dict()
normalizedToFirstName = dict()
firstNameGendersLangagesFrequency = dict()
# from collections import namedtuple
GendersLangagesFrequency = namedtuple(
    "GendersLangagesFrequency", ["genders", "langages", "frequency"]
)

with open(directory(__file__) + "/Prenoms.csv", "r", encoding="ISO-8859-2") as f:
    csvDictReader = csv.DictReader(f, delimiter=";")
    for row in csvDictReader:
        firstName = row["01_prenom"]
        gendersLangagesFrequency = GendersLangagesFrequency(
            row["02_genre"].split(","),
            row["03_langage"].split(","),
            float(row["04_fréquence"]),
        )
        firstNameGendersLangagesFrequency[firstName] = gendersLangagesFrequency
        normalizedFirstName = normalize(firstName)
        existingFirstName = normalizedToFirstName.get(normalizedFirstName, None)
        if (
            existingFirstName is None
            or gendersLangagesFrequency.frequency
            > firstNameGendersLangagesFrequency[existingFirstName].frequency
        ):
            normalizedToFirstName[normalizedFirstName] = firstName


def detectFirstName(obj):
    if isinstance(obj, str):
        obj = normalize(obj).split(" ")
    if isinstance(obj, (list, tuple)):
        # condidats = []
        for elt in obj:
            firstName = normalizedToFirstName.get(normalize(elt), None)
            if firstName is not None:
                return firstName
        return None
    else:
        raise TypeError(
            "obj must be a string, list or tuple, not a %s" % str(type(obj))
        )
