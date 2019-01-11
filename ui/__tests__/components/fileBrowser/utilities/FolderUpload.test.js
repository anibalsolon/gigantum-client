
      import React from 'react'
      import renderer from 'react-test-renderer';
      import {mount} from 'enzyme'
      import FolderUpload from 'Components/fileBrowser/utilities/FolderUpload';

      import relayTestingUtils from 'relay-testing-utils'

      test('Test FolderUpload', () => {

        const wrapper = renderer.create(

           <FolderUpload />

        );

        const tree = wrapper.toJSON()

        expect(tree).toMatchSnapshot()

      })