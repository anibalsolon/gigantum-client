
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import LocalDatasets from 'Components/dashboard/datasets/localDatasets/LocalDatasets';
      import json from './__relaydata__/LocalDatasets.json';
      import history from 'JS/history';
      import { Provider } from 'react-redux';
      import store from 'JS/redux/store';
      import { BrowserRouter as Router } from 'react-router-dom';

      import relayTestingUtils from '@gigantum/relay-testing-utils'


      const fixtures = {
        auth: () => {

        },
        datasetList: json.data.datasetList,
        localDatasets: json.data.datasetList,
        history,
        refetchSort: () => {

        },
        filterDatasets: data => data,
      };

      test('Test LocalDatasets', () => {

        const wrapper = renderer.create(
          relayTestingUtils.relayWrap(
            <Provider store={store}>
              <Router>
                <LocalDatasets
                    {...fixtures}
                />
              </Router>
            </Provider>, {}, json.data.localDatasets)
        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })
