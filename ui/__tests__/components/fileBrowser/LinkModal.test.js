
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import LinkModal from 'Components/fileBrowser/LinkModal';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test LinkModal', () => {

        const wrapper = renderer.create(

           <LinkModal />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })