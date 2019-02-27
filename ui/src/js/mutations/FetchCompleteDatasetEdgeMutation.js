import {
  commitMutation,
  graphql,
} from 'react-relay';
import environment from 'JS/createRelayEnvironment';


const mutation = graphql`
mutation FetchCompleteDatasetEdgeMutation($input: FetchDatasetEdgeInput!, $first: Int!, $cursor: String){
    fetchDatasetEdge(input: $input){
        newDatasetEdge{
          node {
            ...Dataset_dataset
          }
        }
        clientMutationId
    }
}
`;

let tempID = 0;


export default function FetchCompleteDatasetEdgeMutation(
  owner,
  datasetName,
  callback,
) {
  const variables = {
    input: {
      owner,
      datasetName,
    },
    first: 10,
    cursor: null,
  };
  commitMutation(environment, {
    mutation,
    variables,
    onCompleted: (response, error) => {
      if (error) {
        console.log(error);
      }
      callback(error);
    },
    onError: err => console.error(err),
  });
}
