## Beacon | Questionnaire Flow
###### Prepared for Internal
###### Prepared by Mayank
###### Updated on 24 February 2020


We started with the requirement of having some questions the user needs to answer that we need to store on the backend to be used later on.
So, we created the whole questionnaire thing dynamic which defines the type of question, its validations and to save server calls, each question contains the reference of the next question.

When we integrated MDLive, we got to know that we need to send some of the answers users submitted in Intake flow but as the whole questionnaire thing was dynamic till now it becomes very difficult to know which question response is chief-complaint or location.
To make it happen, we added attributes in each question which signify what each question response is.

Then the requirement of self harm question came and as we don’t have to store the response on the backend, frontend created a static question on their end which they always show after the starting question.

Then the requirement of `Safety Sensitive Positions` came which depends on Organisation and what user selects in chief-complaint. This was easy as backend can create some more questions and return the next question based on organisation but it requires some structure changes on backend as previous flow was global but this flow depends on per organisation. So, we need to link questions with organisations.

But this change won’t solve the whole flow as it changes somewhere in between if the user does not select Alcohol in the beginning. Till now the backend sends the next question with the question details but to make this happen the backend have to send the next question based on what users have answered previously.

As this change was urgent, we added some flags in questions & based on those flags frontend stores answers locally in browser cache and shows the flow but it was not the correct way to handle it.

Now the requirement is of the dependent flow which breaks the whole flow as depending on what user answers we’ll show previous flow or not. To make that happen we need to add more flags on which frontend can store some more data and make that flow happen which will make it more hacky and more vulnerable. Every small change in this and in future can break the whole thing.

Currently some logic is on the frontend and some on the backend which needs to be moved to either frontend or backend. It is difficult to keep all this in sync each time we add some changes and it is getting more and more difficult as new requirements are coming. To make sure it does not happen we need to rewrite it in a way that the whole logic is in the backend.

To do that, backend needs to change the mapping of questions based on organisation and add the logic to return it based on user responses. This requires the frontend also to rewrite the flow of how they get the questions from the backend and they need to remove the hacky solutions we added till now.

Now, we created a table template and each question gets linked with a template also having a link to the next question or a service to get the next question. The new api is get-next-question and get-previous-question which will get the next question based on template and user response.

Templates have a flag is_default which will be assigned to every organisation by default and from CMS admin can attach different templates for a different flow.

A management command has been added to add all questions, two templates and their linking. Some refactoring required there and old code is not removed yet as FE works on new changes. So, just keeping them as backup, will be removed later on.

TODO:
- Refactoring
- UI for client to create the flow for a template
- Unit tests to check the new flow working
