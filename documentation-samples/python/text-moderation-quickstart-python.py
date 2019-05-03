# the ContentModeratorClient interacts with the service
from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient

# the Screen class represents the result of a text screen request
from azure.cognitiveservices.vision.contentmoderator.models import (
    Screen
)

# special class that represents a CogServ credential (key)
from msrest.authentication import CognitiveServicesCredentials

from pprint import pprint
import io

# Replace with a valid key
subscription_key = '<your subscription key>'
endpoint_url = 'westus.api.cognitive.microsoft.com'

TEXT = """Is this a grabage email abcdef@abcd.com, phone: 6657789887, \
IP: 255.255.255.255, 1 Microsoft Way, Redmond, WA 98052. \
Crap is the profanity here. Is this information PII? phone 3144444444
"""

# Create the Content Moderator client
client = ContentModeratorClient(endpoint_url, CognitiveServicesCredentials(subscription_key))

# Screen the input text: check for profanity, 
# autocorrect text, check for personally identifying 
# information (PII), and classify text
screen = client.text_moderation.screen_text(
    text_content=io.StringIO(TEXT),
    language="eng",
    text_content_type="text/plain",
    autocorrect=True,
    pii=True,
    classify=True
)

assert isinstance(screen, Screen)
pprint(screen.as_dict())
