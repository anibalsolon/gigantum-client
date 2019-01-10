import {
    commitMutation,
    graphql,
  } from 'react-relay';
  import environment from 'JS/createRelayEnvironment';


  const mutation = graphql`
  mutation LinkDatasetMutation($input: LinkDatasetInput!){
      linkDataset(input: $input){
          newDatasetEdge{
              node{
                id
                name
              }
          }
      }
  }
  `;

  let tempID = 0;


  export default function LinkDatasetMutation(
    owner,
    labbookName,
    datasetUrl,
    callback,
  ) {
    const variables = {
      input: {
        owner,
        labbookName,
        datasetUrl,
        clientMutationId: tempID++,
      },
    };
    commitMutation(environment, {
      mutation,
      variables,
      onCompleted: (response, error) => {
        if (error) {
          console.log(error);
        }
        callback(response, error);
      },
      onError: err => console.error(err),
      optimisticUpdater: (store, response) => {
      },
      updater: (store, response) => {
      },
    });
  }
