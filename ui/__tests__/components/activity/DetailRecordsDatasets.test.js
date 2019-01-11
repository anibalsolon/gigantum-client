
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import DetailRecordsDatasets from 'Components/activity/DetailRecordsDatasets';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test DetailRecordsDatasets', () => {

        const wrapper = renderer.create(

           <DetailRecordsDatasets />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })