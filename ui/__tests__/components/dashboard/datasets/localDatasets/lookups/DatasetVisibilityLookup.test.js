
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import json from './../__relaydata__/LocalDatasets.json';
      import DatasetVisibilityLookup from 'Components/dashboard/datasets/localDatasets/lookups/DatasetVisibilityLookup';

      import relayTestingUtils from '@gigantum/relay-testing-utils'

      test('Test DatasetVisibilityLookup', async () => {
        let id = json.data.datasetList.localDatasets.edges[0].node.id;
        DatasetVisibilityLookup.query([id]).then((response) => {
          console.log(response);
          expect(response.data.ids.length).toEqual(0);
        });
      });