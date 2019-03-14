// vendor
import { graphql } from 'react-relay';
// environment
import { fetchQuery } from 'JS/createRelayEnvironment';

const fetchPackageLatestVersionQuery = graphql`
  query fetchPackageLatestVersionQuery($name: String!, $owner: String!, $first: Int!, $cursor: String){
  labbook(name: $name, owner: $owner){
    id
    description
    environment {
      packageDependencies(first: $first, after: $cursor){
          edges {
            node{
              id
              latestVersion
              manager
              package
            }
            cursor
          }
          pageInfo{
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
          }
        }
      }
    }
  }
`;

const FetchPagkageLatestVersion = {
  getPackageVersions: (owner, name, first, cursor) => {
    const variables = {
      owner,
      name,
      first,
      cursor,
    };
    return new Promise((resolve, reject) => {
      const fetchData = function () {
        fetchQuery(fetchPackageLatestVersionQuery(), variables).then((response) => {
          resolve(response.data);
        }).catch((error) => {
          console.log(error);
          reject(error);
        });
      };
      fetchData();
    });
  },
};

export default FetchPagkageLatestVersion;
