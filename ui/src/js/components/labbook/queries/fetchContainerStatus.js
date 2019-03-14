// vendor
import { graphql } from 'react-relay';
// environment
import { fetchQuery } from 'JS/createRelayEnvironment';
// queries
import labbookUpdatesQuery from './fetchLabbookUpdateQuery';

const containerStatusQuery = graphql`
  query fetchContainerStatusQuery($name: String!, $owner: String!){
  labbook(name: $name, owner: $owner){
    environment{
      containerStatus
      imageStatus
    }
  }
}`;


const FetchContainerStatus = {
  getContainerStatus: (owner, labbookName, isLabbookUpdate) => {
    const variables = {
      owner,
      name: labbookName,
    };

    const query = isLabbookUpdate ? labbookUpdatesQuery() : containerStatusQuery();
    return new Promise((resolve, reject) => {
      const fetchData = function () {
        fetchQuery(query, variables).then((response) => {
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

export default FetchContainerStatus;
