import {
  commitMutation,
  graphql,
} from 'react-relay';
import environment from 'JS/createRelayEnvironment';

import FooterUtils from 'Components/common/footer/FooterUtils';

const mutation = graphql`
  mutation SyncLabbookMutation($input: SyncLabbookInput!){
    syncLabbook(input: $input){
      jobKey
      clientMutationId
    }
  }
`;

let tempID = 0;

export default function SyncLabbookMutation(
  owner,
  labbookName,
  overrideMethod,
  successCall,
  failureCall,
  callback,
) {
  const variables = {
    input: {
      owner,
      labbookName,
      clientMutationId: tempID++,
    },
    first: 10,
    cursor: null,
    hasNext: false,
  };
  if (overrideMethod) {
    variables.input.overrideMethod = overrideMethod;
  }

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
          FooterUtils.getJobStatus(response, 'syncLabbook', 'jobKey', successCall, failureCall);
        }
      },
    },
  );
}
