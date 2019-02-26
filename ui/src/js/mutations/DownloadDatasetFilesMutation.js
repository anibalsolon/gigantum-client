import {
  commitMutation,
  graphql,
} from 'react-relay';
import environment from 'JS/createRelayEnvironment';
// utils
import FooterUtils from 'Components/common/footer/FooterUtils';

const mutation = graphql`
mutation DownloadDatasetFilesMutation($input: DownloadDatasetFilesInput!){
    downloadDatasetFiles(input: $input){
        backgroundJobKey
        clientMutationId
    }
}
`;

let tempID = 0;


export default function DownloadDatasetFilesMutation(
  datasetOwner,
  datasetName,
  labbookName,
  labbookOwner,
  successCall,
  failureCall,
  keys,
  allKeys,
  callback,
) {
  const variables = {
    input: {
      datasetOwner,
      datasetName,
      clientMutationId: tempID++,
    },
  };
  if (allKeys) {
    variables.input.allKeys = allKeys;
  } else {
    variables.input.keys = keys;
  }
  if (labbookName) {
    variables.input.labbookName = labbookName;
  }
  if (labbookOwner) {
    variables.input.labbookOwner = labbookOwner;
  }

  commitMutation(environment, {
    mutation,
    variables,
    onCompleted: (response, error) => {
      if (error) {
        console.log(error);
      }
      FooterUtils.getJobStatus(response, 'downloadDatasetFiles', 'backgroundJobKey', successCall, failureCall);

      callback(error);
    },
    onError: err => console.error(err),
  });
}
