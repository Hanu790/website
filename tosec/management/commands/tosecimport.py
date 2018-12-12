"""Import a TOSEC database to the local database"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand

from tosec import models
from tosec.parser import TosecParser


class Command(BaseCommand):
    """Import a TOSEC dump to the Lutris database"""
    args = '<tosec_catalog tosec_catalog ...>'
    help = "Import Tosec catalog files in the database"

    @staticmethod
    def import_tosec_database(filename):
        """Import a TOSEC database referenced by filename"""
        with open(filename, 'r') as tosec_dat:
            dat_contents = tosec_dat.readlines()

        tosec_parser = TosecParser(dat_contents)
        tosec_parser.parse()

        category = models.Category(
            name=tosec_parser.headers['name'],
            description=tosec_parser.headers['description'],
            category=tosec_parser.headers['category'],
            version=tosec_parser.headers['version'],
            author=tosec_parser.headers['author'],
        )
        category.save()

        for game in tosec_parser.games:
            game_row = models.Game(
                category=category,
                name=game['name'],
                description=game['description'],
            )
            game_row.save()
            rom = game['rom']
            rom_row = models.Rom(
                game=game_row,
                name=rom['name'],
                size=rom['size'],
                crc=rom['crc'],
                md5=rom.get('md5', ''),
                sha1=rom.get('sha1', ''),
            )
            rom_row.save()

    def handle(self, *args, **_options):
        if args:
            filenames = args
        else:
            basepath = os.path.join(settings.TOSEC_DAT_PATH, 'TOSEC')
            if not os.path.exists(basepath):
                self.stderr.write("No TOSEC database found in %s" % basepath)
                return
            filenames = [os.path.join(basepath, f)
                         for f in os.listdir(basepath)]
        total_files = len(filenames)
        for index, filename in enumerate(filenames, start=1):
            self.stdout.write("Importing {} [{} of {}]".format(filename,
                                                               index,
                                                               total_files))
            self.import_tosec_database(filename)
