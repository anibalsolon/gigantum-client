import {
  commitMutation,
  graphql,
} from 'react-relay';
import uuidV4 from 'uuid/v4';
import environment from 'JS/createRelayEnvironment';

const mutation = graphql`
  mutation MergeFromBranchMutation($input: MergeFromBranchInput!, $first: Int, $cursor: String, $hasNext: Boolean!, $includeInitial: Boolean){
    mergeFromBranch(input: $input){
      labbook{
        ...Labbook_labbook
      }
      clientMutationId
    }
  }
`;

export default function MergeFromBranchMutation(
  owner,
  labbookName,
  otherBranchName,
  overrideMethod,
  callback,
) {
  const clientMutationId = uuidV4();
  const variables = {
    input: {
      owner,
      labbookName,
      otherBranchName,
      clientMutationId,
    },
    first: 10,
    cursor: null,
    hasNext: false,
    includeInitial: true,
  };
  if (overrideMethod) {
    input.overrideMethod = overrideMethod;
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

        callback(response, error);
      },
      onError: (err) => { console.error(err); },
    },
  );
}
