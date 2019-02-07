import Datasets from './../Datasets';
import {
  createFragmentContainer,
  graphql,
} from 'react-relay';

export default createFragmentContainer(
  Datasets,
  graphql`
    fragment RemoteDatasetsContainer_datasetList on LabbookQuery{
      datasetList{
        id
        ...RemoteDatasets_remoteDatasets
      }
    }
  `,
);
