import {
  commitMutation,
  graphql,
} from 'react-relay';
import environment from 'JS/createRelayEnvironment';

import FooterUtils from 'Components/common/footer/FooterUtils';

const mutation = graphql`
  mutation SyncDatasetMutation($input: SyncDatasetInput!){
    syncDataset(input: $input){
      jobKey
      clientMutationId
    }
  }
`;

let tempID = 0;

export default function SyncDatasetMutation(
  owner,
  datasetName,
  force,
  successCall,
  failureCall,
  callback,
) {
  const variables = {
    input: {
      owner,
      datasetName,
      force,
      clientMutationId: tempID++,
    },
    first: 10,
    cursor: null,
    hasNext: false,
  };

  commitMutation(
    environment,
    {
      mutation,
      variables,
      onCompleted: (response, error) => {
        if (error) {
          console.log(error);
        }

        callback(error);
      },
      onError: (err) => { console.error(err); },
      updater: (store, response) => {
        if (response) {
          FooterUtils.getJobStatus(response, 'syncDataset', 'jobKey', successCall, failureCall);
        }
      },
    },
  );
}
