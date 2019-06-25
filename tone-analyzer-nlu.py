import sys
import json
import glob
import twitter
from watson_developer_cloud import PersonalityInsightsV3
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions, SemanticRolesOptions
from operator import itemgetter
import settings

# This Watson Python SDK example uses the Personality Insights service to extract the most positive sentences, and to do things

def main():
   # Check for service credentials and transcript files location
   if not hasattr(settings, 'TONE_ANALYZER_APIKEY')  or not hasattr(settings, 'NLU_APIKEY') or not hasattr(settings, 'TEST_DATA_DIR'):
       print("Error: Service credentials and/or test data dir  missing. Terminating ...")
       sys.exit(1)
   elif settings.NLU_APIKEY.strip() == '' or settings.TONE_ANALYZER_APIKEY.strip() == '' or settings.TEST_DATA_DIR.strip() == '':
       print("Error: Service credentials and/or test data dir empty . Terminating ...")
       sys.exit(1)
   else:
       tone_analyzer_apikey =  settings.TONE_ANALYZER_APIKEY
       nlu_apikey = settings.NLU_APIKEY
       test_data_dir = settings.TEST_DATA_DIR
       twit_cons_apikey=settings.TWITTER_CONSUMER_API_KEY
       twit_cons_s_apikey=settings.TWITTER_CONSUMER_SECRET_API_KEY
       twit_secret_access_token=settings.TWITTER_SECRET_ACCESS_TOKEN
       twit_access_token=settings.TWITTER_ACCESS_TOKEN

        # Create service clients
       tone_analyzer = PersonalityInsightsV3(iam_apikey= tone_analyzer_apikey, version='2017-09-21')
       #twit = twitter.Twitter()
       #print(twit)
       twitter_api = twitter.Api(consumer_key=twit_cons_apikey,consumer_secret=twit_cons_s_apikey,access_token_key=twit_access_token,access_token_secret=twit_secret_access_token)
       natural_language_understanding = NaturalLanguageUnderstandingV1(version='2018-03-16', iam_apikey=nlu_apikey)
       print(twitter_api.VerifyCredentials())
       # Loop through all call transcript files
       test_files = glob.glob(test_data_dir + '/**/*.txt', recursive=True)
       print('Analyzing  %d earnings call transcripts ...' % (len(test_files)))
       for filename in  test_files:
           print("Analyzing  file name " + filename)

           with open(filename, 'r') as transcript:

              tone = tone_analyzer.profile(transcript.read(), content_type="text/plain").get_result()

              # Get joy and sort by descending score
              sentences_with_joy = []
              for each_sentence in tone['personality']:
                 for each_tone in each_sentence['children']:
                    sentences_with_joy.append({'sentence_id': each_tone['trait_id'], 'text': each_tone['name'], 'score': each_tone['percentile']})

              sentences_with_joy = sorted(sentences_with_joy,key=itemgetter('score'), reverse=True)
              # Only top 5 are being selected
              if len(sentences_with_joy) > 5:
                   sentences_with_joy = sentences_with_joy[:5]


              index = 1
              print('\nStrongest personality traits:\n')

              # Go through top positive sentences and use NLU to get keywords and
              # Semantic Roles
              for sentence in sentences_with_joy:
                 print(str(index) + ') ' + sentence['text'])

if __name__ == "__main__":
   main()
