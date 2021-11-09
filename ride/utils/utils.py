import csv

from ride.circles.models import Circle


def import_csv(file):
    """
    Read csv file and extracts circles information
    to be included in the database
    """
    str_to_bool = lambda a: True if int(a) > 0 else False
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader) #skip header
        for row in csv_reader:
            circle = Circle(
                name=row[0],
                slug_name=row[1],
                is_public=str_to_bool(row[2]),
                verified=str_to_bool(row[3]),
                is_limited=str_to_bool(row[4]),
                members_limit=int(row[4]),
            )
            circle.save()
