import os.path, time
from pprint import pprint

from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from azure.cognitiveservices.vision.contentmoderator.models import ( 
        APIErrorException, ImageList, ImageIds, Image, RefreshIndex, MatchResponse, # images
        TermList, Terms, TermsData, Screen ) # terms
from msrest.authentication import CognitiveServicesCredentials

'''
CONTENT MODERATOR - QUICKSTART SAMPLES

Prerequisites:
    - A Content Moderator subscription in the Azure portal: https://ms.portal.azure.com
    - Python 2.7+ or 3.5+: https://www.python.org/downloads/
    - pip tool: https://pip.pypa.io/en/stable/installing/
    - Install the SDK from the command line: 
        pip install azure-cognitiveservices-vision-contentmoderator

References:
    - SDK: https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-contentmoderator/azure.cognitiveservices.vision.contentmoderator?view=azure-python
    - API: https://docs.microsoft.com/en-us/azure/cognitive-services/content-moderator/api-reference
    - Documentation: https://docs.microsoft.com/en-us/azure/cognitive-services/content-moderator/
'''
# For the terms list
TEXT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "text_files")

# Number of minutes to delay after updating the search index before image/term matching operations against the list.
LATENCY_DELAY = 0.5

# Lists for the custom image list
IMAGE_LIST = {
    "Sports": [ "https://moderatorsampleimages.blob.core.windows.net/samples/sample4.png",
                "https://moderatorsampleimages.blob.core.windows.net/samples/sample6.png",
                "https://moderatorsampleimages.blob.core.windows.net/samples/sample9.png" ],

    "Swimsuit": [ "https://moderatorsampleimages.blob.core.windows.net/samples/sample1.jpg",
                  "https://moderatorsampleimages.blob.core.windows.net/samples/sample3.png",
                  "https://moderatorsampleimages.blob.core.windows.net/samples/sample16.png", ]
}
IMAGES_TO_MATCH = [ "https://moderatorsampleimages.blob.core.windows.net/samples/sample1.jpg",
                    "https://moderatorsampleimages.blob.core.windows.net/samples/sample4.png",
                    "https://moderatorsampleimages.blob.core.windows.net/samples/sample5.png",
                    "https://moderatorsampleimages.blob.core.windows.net/samples/sample16.png" ]

'''
Authenticate
Create a client for all samples.
'''
# Set your environment variables with the values of your key and region, "westus" is the default region.
SUBSCRIPTION_KEY = os.environ.get('CONTENTMODERATOR_SUBSCRIPTION_KEY')
CONTENTMODERATOR_REGION = os.environ.get('CONTENTMODERATOR_REGION', 'westus')

client = ContentModeratorClient(endpoint='https://'+CONTENTMODERATOR_REGION+'.api.cognitive.microsoft.com',
        credentials=CognitiveServicesCredentials(SUBSCRIPTION_KEY))

print('\n##############################################################################\n')

'''
CONTENT MODERATOR - CUSTOM IMAGE LISTS 
This sample shows how to create custom lists for your images and perform the following tasks with them:
- Create an image list.
- Add images to a list. 
- Get all image IDs.
- Update list details.
- Get list details.
- Refresh the index.
- Match images against the image list.
- Remove an image, refresh, and re-match.
- Delete all images.
- Delete list.
- Get all image list IDs.
'''
'''
Create image list
Creates an empty list for custom images, using the List Management API.
'''
print('Creating image list...')
# Returns an ImageList object
custom_image_list = client.list_management_image_lists.create(content_type='application/json',
        body={ 'name':'Generic name', 'description':'A list of sport and swimsuit images',
               'metadata': { 'good': 'Acceptable', 'not_good': 'Potentially racy' } })
print('Image list created:')
assert isinstance(custom_image_list, ImageList)
pprint(custom_image_list.as_dict()) # Prints id, name, description, metadata
image_list_id = custom_image_list.id # Save the ID of the list

'''
Add images
Add from the URL dictionary.
'''
print('\nAdding images to list ID {}'.format(image_list_id))
index = {}  # Keep an index of url ids for later removal
try:
    for label, urls in IMAGE_LIST.items(): # Get list of tuple pairs
        for url in urls:
            print('Adding image {} to list {} with label {}.'.format(url, image_list_id, label))
            # Returns an Image object
            added_image = client.list_management_image.add_image_url_input( 
                list_id=image_list_id, content_type='application/json',
                data_representation='URL', value=url, label=label )
            if added_image:
                index[url] = added_image.content_id
except APIErrorException as err:
    print('Unable to add image to list: {}'.format(err))
else:
    assert isinstance(added_image, Image)
    pprint(added_image.as_dict()) # Prints content_id, additional_info, status, tracking_id

'''
Get all images ids
'''
print('\nGetting all image IDs for list {}'.format(image_list_id))
# Returns an ImageIds object
image_ids = client.list_management_image.get_all_image_ids(list_id=image_list_id)
assert isinstance(image_ids, ImageIds)
pprint(image_ids.as_dict()) # Prints content_source, content_ids, status, tracking_id

'''
Update list details
Changes the name of an existing list.
'''
print('\nUpdating details for list {}'.format(image_list_id))
# Returns an ImageList object
updated_list = client.list_management_image_lists.update( list_id=image_list_id, content_type='application/json', body={ 'name': 'Swimsuits and sports' })
assert isinstance(updated_list, ImageList)
pprint(updated_list.as_dict()) # Prints id, name, description, metadata

'''
Get list details
'''
print('\nGetting details for list {}'.format(image_list_id))
# Returns an ImageList object
list_details = client.list_management_image_lists.get_details(list_id=image_list_id)
assert isinstance(list_details, ImageList)
pprint(list_details.as_dict()) # Prints id, name, description, metadata

'''
Refresh the index
If changed, an image list must be refresh its index for changes to be included in future scans.
'''
print('\nRefreshing the search index for list {}'.format(image_list_id))
# Returns a RefreshIndex object
refresh_image_index = client.list_management_image_lists.refresh_index_method(list_id=image_list_id)
assert isinstance(refresh_image_index, RefreshIndex)
pprint(refresh_image_index.as_dict()) # Prints content_source_id, is_update_success, advanced_info, status, and tracking_id

print('\nWaiting {} minutes to allow the server time to propagate the index changes.'.format(LATENCY_DELAY))
time.sleep(LATENCY_DELAY * 60)

'''
Match images against the image list
Using the Image Moderation API, compares two lists, looks for exact image matches.
'''
for image_url in IMAGES_TO_MATCH:
    print('\nMatching image {} against list {}'.format(image_url, image_list_id))
    # Returns a MatchResponse object
    match_result = client.image_moderation.match_url_input( content_type='application/json',
        list_id=image_list_id, data_representation='URL', value=image_url )
    assert isinstance(match_result, MatchResponse)
    print('Is match? {}'.format(match_result.is_match))
    print('Complete match details:')
    pprint(match_result.as_dict()) # Prints tracking_id, cache_id, is_match, matches, status

'''
Delete images
Deletes an image from the list.
'''
image_to_remove = 'https://moderatorsampleimages.blob.core.windows.net/samples/sample16.png'
print('\nRemove image {} from list {}'.format(image_to_remove, image_list_id))
# Returns a string of the image ID removed
client.list_management_image.delete_image(list_id=image_list_id, image_id=index[image_to_remove])

'''
Refresh the index
Refreshes the index again after replacing one image with another.
'''
print('\nRefreshing the search index for list {}'.format(image_list_id))
client.list_management_image_lists.refresh_index_method(list_id=image_list_id)

print('Waiting {} minutes to allow the server time to propagate the index changes.'.format(LATENCY_DELAY))
time.sleep(LATENCY_DELAY * 60)

'''
Re-match
Compares the lists again after the change.
'''
print('\nMatching image. The removed image should not match.')
for image_url in IMAGES_TO_MATCH:
    print('\nMatching image {} against list {}'.format(image_url, image_list_id))
    match_result = client.image_moderation.match_url_input( content_type='application/json',
        list_id=image_list_id, data_representation='URL', value=image_url )
    assert isinstance(match_result, MatchResponse)
    print('Is match? {}'.format(match_result.is_match))
    print('Complete match details:')
    pprint(match_result.as_dict())

'''
Delete all images
Deletes all images from list. Left with an empty list.
'''
print('\nDelete all images in the image list {}'.format(image_list_id))
# Returns the deletion status, as a string
client.list_management_image.delete_all_images(list_id=image_list_id)

'''
Delete list
Deletes the list entirely.
'''
print('\nDelete the image list {}'.format(image_list_id))
# Returns the deletion status, as a string
client.list_management_image_lists.delete(list_id=image_list_id)

'''
Get all list ids
'''
print('\nVerify that the list {} was deleted.'.format(image_list_id))
# Returns a list[ImageList] object
image_lists = client.list_management_image_lists.get_all_image_lists()
assert not any(image_list_id == image_list.id for image_list in image_lists)
'''
END CONTENT MODERATOR - CUSTOM IMAGE LISTS 
'''
print('\n##############################################################################\n')

'''
CONTENT MODERATOR - CUSTOM TERMS LISTS 
This sample creates a custom terms list, using the List Management API. 
Useful if you want to add/use your own moderation terms to a project.
- Create a terms list.
- Update terms list details.
- Add terms to a list. 
- Get all terms IDs. 
- Refresh the index. 
- Screen the text.
- Remove terms, refresh, and re-screen text.
- Delete all terms. 
- Delete list.
'''
'''
Create term list
Creates an empty terms list with metadata.
'''
print('Creating term list...')
custom_terms_list = client.list_management_term_lists.create(content_type='application/json', 
    body={ 'name': 'Term list name', 'description': 'Term list description' })
print('Term list created:')
assert isinstance(custom_terms_list, TermList)
pprint(custom_terms_list.as_dict())
terms_list_id = custom_terms_list.id # save an ID of the list

'''
Update list details
'''
print("\nUpdating details for list {}".format(terms_list_id))
updated_terms_list = client.list_management_term_lists.update(list_id=terms_list_id, content_type="application/json",
                body={ "name": "Greetings", "description": "Different ways to greet someone." })
assert isinstance(updated_terms_list, TermList)
pprint(updated_terms_list.as_dict())

'''
Add terms
'''
# Do one API call per term added
print("\nAdding terms to list {}".format(terms_list_id))
client.list_management_term.add_term(list_id=terms_list_id, term="hello", language="eng")
client.list_management_term.add_term(list_id=terms_list_id, term="wave", language="eng")

'''
Get all terms ids
'''
print("\nGetting all term IDs for list {}".format(terms_list_id))
terms = client.list_management_term.get_all_terms(list_id=terms_list_id, language="eng")
assert isinstance(terms, Terms)
terms_data = terms.data
assert isinstance(terms_data, TermsData)
pprint(terms_data.as_dict())

'''
Refresh the index
This is a must when you make changes to the list, in order to scan through it again.
'''
refresh_terms_index = client.list_management_term_lists.refresh_index_method(list_id=terms_list_id, language="eng")
assert isinstance(refresh_terms_index, RefreshIndex)
pprint(refresh_terms_index.as_dict())
print("\nWaiting {} minutes to allow the server time to propagate the index changes.".format(LATENCY_DELAY))
time.sleep(LATENCY_DELAY * 60)

'''
Screen text
Searches through a text block to find terms. All terms in a block of screened text are recognized as words within quotes.
'''
terms_text = 'This text contains the terms "hello" and "wave".'
print('\nScreening text "{}" using term list {}'.format(terms_text, terms_list_id))
with open(os.path.join(TEXT_FOLDER, 'content_moderator_term_list.txt'), "rb") as text_fd:
    screen = client.text_moderation.screen_text(text_content_type="text/plain", text_content=text_fd,
        language="eng", autocorrect=False, pii=False, list_id=terms_list_id)
    assert isinstance(screen, Screen)
    pprint(screen.as_dict())

'''
Remove terms
'''
term_to_remove = "hello"
print("\nRemove term {} from list {}".format(term_to_remove, terms_list_id))
client.list_management_term.delete_term(list_id=terms_list_id, term=term_to_remove, language="eng")

'''
Refresh the index
Refresh again since removing a term changed the list
'''
print("\nRefreshing the search index for list {}".format(terms_list_id))
refresh_index = client.list_management_term_lists.refresh_index_method(list_id=terms_list_id, language="eng")
assert isinstance(refresh_index, RefreshIndex)
pprint(refresh_index.as_dict())
print("\nWaiting {} minutes to allow the server time to propagate the index changes.".format(LATENCY_DELAY))
time.sleep(LATENCY_DELAY * 60)
'''
Re-screen text
'''
with open(os.path.join(TEXT_FOLDER, 'content_moderator_term_list.txt'), "rb") as text_fd:
    print('\nScreening text "{}" using term list {}'.format(terms_text, terms_list_id))
    screen = client.text_moderation.screen_text(text_content_type="text/plain", text_content=text_fd,
        language="eng", autocorrect=False, pii=False, list_id=terms_list_id)
    assert isinstance(screen, Screen)
    pprint(screen.as_dict())

'''
Delete all terms
This leaves an empty list.
'''
print("\nDelete all terms in the term list {}".format(terms_list_id))
client.list_management_term.delete_all_terms(list_id=terms_list_id, language="eng")

'''
Delete list
This deletes the list entirely.
'''
print("\nDelete the term list {}".format(terms_list_id))
client.list_management_term_lists.delete(list_id=terms_list_id)
'''
END CONTENT MODERATOR - CUSTOM TERMS LISTS 
'''
print('\n##############################################################################\n')