
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import DataBrowser from 'Components/dataset/data/DataBrowser';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test DataBrowser', () => {

        const wrapper = renderer.create(

           <DataBrowser />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })