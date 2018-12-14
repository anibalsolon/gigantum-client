
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import sessionCheck from '/Auth/sessionCheck';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test sessionCheck', () => {

        const wrapper = renderer.create(

           <sessionCheck />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })