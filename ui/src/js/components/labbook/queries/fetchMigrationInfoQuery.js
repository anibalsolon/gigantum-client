// vendor
import { graphql } from 'react-relay';
// environment
import { fetchQuery } from 'JS/createRelayEnvironment';

const fetchMigrationInfoQuery = graphql`
  query fetchMigrationInfoQuery($name: String!, $owner: String!){
  labbook(name: $name, owner: $owner){
    id
    isDeprecated
    shouldMigrate
  }
}
`;

const FetchLabbook = {
  getLabook: (owner, labbookName) => {
    const variables = {
      owner,
      name: labbookName,
    };

    return new Promise((resolve, reject) => {
      const fetchData = function () {
        fetchQuery(fetchMigrationInfoQuery(), variables).then((response) => {
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

export default FetchLabbook;
