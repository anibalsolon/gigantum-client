
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import LabbookContainerQuery from 'Components/labbook/LabbookContainerQuery';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test LabbookContainerQuery', () => {

        const wrapper = renderer.create(

           <LabbookContainerQuery />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })