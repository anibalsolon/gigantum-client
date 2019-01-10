
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import DatasetContainerQuery from 'Components/dataset/DatasetContainerQuery';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test DatasetContainerQuery', () => {

        const wrapper = renderer.create(

           <DatasetContainerQuery />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })