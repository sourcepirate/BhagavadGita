#!/usr/bin/python
# -*- coding: utf-8 -*-

from flasgger import SwaggerView
from flask import jsonify, request

from app.models.chapter import ChapterModel

from ... import csrf, oauth, db
from ...models.verse import VerseModel
from ...schemas.verse import VerseSchema

verse_schema = VerseSchema()
verses_schema = VerseSchema(many=True)

LANGUAGES = {'en': 'English', 'hi': 'हिंदी'}


class VerseList(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('verse')]
    definitions = {'VerseSchema': VerseSchema}

    def get(self):
        """
        Get all the Verses.
        Get a list of all Verses.
        ---
        tags:
        - verse
        parameters:
        - name: access_token
          in: query
          required: True
          type: 'string'
          description: "Your app's access token."
        - name: language
          in: query
          type: 'string'
          description: "Language to query. Leave blank for english."
          enum: ['hi']
        consumes:
        - application/json
        produces:
        - application/json
        responses:
          200:
            description: 'Success: Everything worked as expected.'
            schema:
              $ref: '#/definitions/VerseSchema'
            examples:
              application/json: |-
                {
                  "verses": [
                    {
                      "chapter_number": 1,
                      "meaning": "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?",
                      "text": "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय |||1||",
                      "transliteration": "dhṛitarāśhtra uvācha dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya",
                      "verse_number": 1,
                      "word_meanings": "dhṛitarāśhtraḥ uvācha—Dhritarashtra said; dharma-kṣhetre—the land of dharma; kuru-kṣhetre—at Kurukshetra; samavetāḥ—having gathered; yuyutsavaḥ—desiring to fight; māmakāḥ—my sons; pāṇḍavāḥ—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sañjaya—Sanjay"
                    },
                    {
                      "chapter_number": 1,
                      "meaning": "Sanjay said: On observing the Pandava army standing in military formation, King Duryodhan approached his teacher Dronacharya, and said the following words.",
                      "text": "सञ्जय उवाच | दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा | आचार्यमुपसङ्गम्य राजा वचनमब्रवीत् | ||2||",
                      "transliteration": "sañjaya uvācha dṛiṣhṭvā tu pāṇḍavānīkaṁ vyūḍhaṁ duryodhanastadā āchāryamupasaṅgamya rājā vachanamabravīt",
                      "verse_number": 2,
                      "word_meanings": "sanjayaḥ uvācha—Sanjay said; dṛiṣhṭvā—on observing; tu—but; pāṇḍava-anīkam—the Pandava army; vyūḍham—standing in a military formation; duryodhanaḥ—King Duryodhan; tadā—then; āchāryam—teacher; upasaṅgamya—approached; rājā—the king; vachanam—words; abravīt—spoke"
                    }
                  ]
                }
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Inavlid access_token used.'
          402:
            description: 'Request Failed.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        language = request.args.get('language')

        if language is None:
            sql = """
                    SELECT *
                    FROM verses v
                    ORDER BY v.chapter_number, v.verse_order
                """
            verses = db.session.execute(sql)
        else:
            if language not in LANGUAGES.keys():
                return (jsonify({'message': 'Invalid Language.'}), 404)

            verses_table = "verses_" + language
            sql = """
                    SELECT vt.meaning, vt.word_meanings, v.text, v.transliteration, v.chapter_number, v.verse_number, v.verse_order
                    FROM %s vt
                    JOIN verses v
                    ON
                    vt.chapter_number = v.chapter_number
                    AND vt.verse_number = v.verse_number
                    ORDER BY v.verse_order
                """ % (verses_table)

            verses = db.session.execute(sql)

        result = verses_schema.dump(verses)
        return jsonify(result.data)


class VerseListByChapter(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('verse')]
    definitions = {'VerseSchema': VerseSchema}

    def get(self, chapter_number):
        """
        Get all the Verses from a Chapter.
        Get a list of all Verses from a particular Chapter.
        ---
        tags:
        - verse
        parameters:
        - name: access_token
          in: query
          required: True
          type: 'string'
          description: "Your app's access token."
        - name: chapter_number
          in: path
          type: integer
          enum:
          - 1
          - 2
          - 3
          required: True
          default: 1
          description: Which Chapter Number to filter?
        - name: language
          in: query
          type: 'string'
          description: "Language to query. Leave blank for english."
          enum: ['hi']
        consumes:
        - application/json
        produces:
        - application/json
        responses:
          200:
            description: 'Success: Everything worked as expected.'
            schema:
              $ref: '#/definitions/VerseSchema'
            examples:
              application/json: |-
                {
                  "verses": [
                    {
                      "chapter_number": 1,
                      "meaning": "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?",
                      "text": "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय |||1||",
                      "transliteration": "dhṛitarāśhtra uvācha dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya",
                      "verse_number": 1,
                      "word_meanings": "dhṛitarāśhtraḥ uvācha—Dhritarashtra said; dharma-kṣhetre—the land of dharma; kuru-kṣhetre—at Kurukshetra; samavetāḥ—having gathered; yuyutsavaḥ—desiring to fight; māmakāḥ—my sons; pāṇḍavāḥ—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sañjaya—Sanjay"
                    },
                    {
                      "chapter_number": 1,
                      "meaning": "Sanjay said: On observing the Pandava army standing in military formation, King Duryodhan approached his teacher Dronacharya, and said the following words.",
                      "text": "सञ्जय उवाच | दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा | आचार्यमुपसङ्गम्य राजा वचनमब्रवीत् | ||2||",
                      "transliteration": "sañjaya uvācha dṛiṣhṭvā tu pāṇḍavānīkaṁ vyūḍhaṁ duryodhanastadā āchāryamupasaṅgamya rājā vachanamabravīt",
                      "verse_number": 2,
                      "word_meanings": "sanjayaḥ uvācha—Sanjay said; dṛiṣhṭvā—on observing; tu—but; pāṇḍava-anīkam—the Pandava army; vyūḍham—standing in a military formation; duryodhanaḥ—King Duryodhan; tadā—then; āchāryam—teacher; upasaṅgamya—approached; rājā—the king; vachanam—words; abravīt—spoke"
                    }
                  ]
                }
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          404:
            description: 'Not Found: The chapter number you are looking for could not be found.'
          402:
            description: 'Request Failed.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        language = request.args.get('language')

        if chapter_number not in range(1, 19):
            return (jsonify({'message': 'Invalid Chapter.'}), 404)

        if language is None:
            sql = """
                    SELECT *
                    FROM verses v
                    WHERE v.chapter_number = %s
                    ORDER BY v.verse_order
                """ % (chapter_number)

            verses = db.session.execute(sql)
        else:
            if language not in LANGUAGES.keys():
                return (jsonify({'message': 'Invalid Language.'}), 404)

            verses_table = "verses_" + language
            sql = """
                    SELECT vt.meaning, vt.word_meanings, v.text, v.transliteration, v.chapter_number, v.verse_number, v.verse_order
                    FROM %s vt
                    JOIN verses v
                    ON
                    vt.chapter_number = v.chapter_number
                    AND vt.verse_number = v.verse_number
                    WHERE v.chapter_number = %s
                    ORDER BY v.verse_order
                """ % (verses_table, chapter_number)

            verses = db.session.execute(sql)

        result = verses_schema.dump(verses)
        return jsonify(result.data)


class VerseByChapter(SwaggerView):

    decorators = [csrf.exempt, oauth.require_oauth('verse')]
    definitions = {'VerseSchema': VerseSchema}

    def get(self, chapter_number, verse_number):
        """
        Get a particular verse from a chapter.
        Get a specific verse from a specific chapter.
        ---
        tags:
        - verse
        parameters:
        - name: access_token
          in: query
          required: True
          type: 'string'
          description: "Your app's access token."
        - name: chapter_number
          in: path
          type: integer
          enum:
          - 1
          - 2
          - 3
          required: True
          default: 1
          description: Which Chapter Number to filter?
        - name: verse_number
          in: path
          type: string
          enum:
          - 1
          - 2
          - 3
          required: True
          default: 1
          description: Which Verse Number to filter?
        - name: language
          in: query
          type: 'string'
          description: "Language to query. Leave blank for english."
          enum: ['hi']
        consumes:
        - application/json
        produces:
        - application/json
        responses:
          200:
            description: 'Success: Everything worked as expected.'
            schema:
              $ref: '#/definitions/VerseSchema'
            examples:
              application/json: |-
                {
                  "chapter_number": 1,
                  "meaning": "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?",
                  "text": "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय |||1||",
                  "transliteration": "dhṛitarāśhtra uvācha dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya",
                  "verse_number": 1,
                  "word_meanings": "dhṛitarāśhtraḥ uvācha—Dhritarashtra said; dharma-kṣhetre—the land of dharma; kuru-kṣhetre—at Kurukshetra; samavetāḥ—having gathered; yuyutsavaḥ—desiring to fight; māmakāḥ—my sons; pāṇḍavāḥ—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sañjaya—Sanjay"
                }
          400:
            description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
          401:
            description: 'Unauthorized: Invalid access_token used.'
          402:
            description: 'Request Failed.'
          404:
            description: 'Not Found: The chapter/verse number you are looking for could not be found.'
          500:
            description: 'Server Error: Something went wrong on our end.'
        """

        language = request.args.get('language')

        if chapter_number not in range(1, 19):
            return (jsonify({'message': 'Invalid Chapter.'}), 404)

        if language is None:
            verse = VerseModel.find_by_chapter_number_verse_number(
                chapter_number, verse_number)

        else:
            if language not in LANGUAGES.keys():
                return (jsonify({'message': 'Invalid Language.'}), 404)

            verses_table = "verses_" + language
            sql = """
                    SELECT vt.meaning, vt.word_meanings, v.text, v.transliteration, v.chapter_number, v.verse_number, v.verse_order
                    FROM %s vt
                    JOIN verses v
                    ON
                    vt.chapter_number = v.chapter_number
                    AND vt.verse_number = v.verse_number
                    WHERE v.chapter_number = %s
                    AND v.verse_number = '%s'
                    ORDER BY v.verse_order
                """ % (verses_table, chapter_number, verse_number)

            verse = db.session.execute(sql).first()

        if verse:
            result = verse_schema.dump(verse)
            return jsonify(result.data)
        return (jsonify({'message': 'Verse not found.'}), 404)
