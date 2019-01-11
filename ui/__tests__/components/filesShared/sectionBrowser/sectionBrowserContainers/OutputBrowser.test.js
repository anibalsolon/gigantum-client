
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import OutputBrowser from 'Components/filesShared/sectionBrowser/sectionBrowserContainers/OutputBrowser';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test OutputBrowser', () => {

        const wrapper = renderer.create(

           <OutputBrowser />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })