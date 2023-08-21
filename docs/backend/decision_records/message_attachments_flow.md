## Beacon | Documents as Message Attachment
###### Prepared for Internal
###### Prepared by Mayank
###### Updated on 22 January 2020

**Restrictions**:
For user privacy and Hipaa Compliance, Django backend will not store documents directly. It will only keep the metadata of document to attach and reference with the message.

As Django backend will be getting the document data from frontend using api only when they upload the document successfully on MDLive. So, Django backend won’t be having any reference of already existing documents and documents uploaded from MDLive dashboard.

Flow:

- Frontend will upload the documents on MDLive using the api:
  https://developers.mdlive.com/#customer-documents-create
  **Note**: Documents will be uploaded in base64 encoded string format

- Frontend will send the metadata of the uploaded document to Django backend using the endpoint: [create a user document](../../api/endpoints.md#create-a-user-document)

- From django backend in response frontend will receive the uuid of each document which they will send with the message under key documents using the endpoint: [create a message](../../api/endpoints.md#create-a-message)

- Django backend will send the message to MDLive after appending an extra line if documents are attached with the message.
  The extra line will be:
  {patient first name} uploaded {number of} files with this message. These files can be found in their user profile; named:
  Filename1.jpg
  Filename2.pdf

- Frontend can fetch all the user documents using the endpoint: [get all user documents](../../api/endpoints.md#get-all-user-documents)
  Django backend will only return the Mdlive Id of the document. To get the actual file frontend needs to hit the MDLive api:
  https://developers.mdlive.com/#customer-documents-show
  **Note**: MDLive will return the document file as base64 encoded string which they have to convert before previewing or letting the user download it.

- Similar document data will be returned from django backend in message detail endpoint if document was attached with that message:
  [fetch message detail](../../api/endpoints.md#fetch-message-detail)
