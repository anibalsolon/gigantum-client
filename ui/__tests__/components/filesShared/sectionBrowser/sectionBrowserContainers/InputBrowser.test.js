
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import InputBrowser from 'Components/filesShared/sectionBrowser/sectionBrowserContainers/InputBrowser';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test InputBrowser', () => {

        const wrapper = renderer.create(

           <InputBrowser />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })